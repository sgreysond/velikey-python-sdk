"""VeliKey data models and types."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    UPDATING = "updating"
    ERROR = "error"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class PolicyMode(str, Enum):
    """Policy enforcement mode."""
    OBSERVE = "observe"
    ENFORCE = "enforce"
    CANARY = "canary"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    PCI_DSS = "pci-dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    CUSTOM = "custom"


class Agent(BaseModel):
    """VeliKey agent representation."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str = "unknown-agent"
    version: str = "unknown"
    status: str = AgentStatus.UNKNOWN if hasattr(AgentStatus, "UNKNOWN") else "unknown"
    location: str = "unknown"
    capabilities: List[str] = Field(default_factory=list)
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="lastHeartbeat")
    uptime: str = "unknown"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_agent_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        if "id" not in normalized and isinstance(normalized.get("agentId"), str):
            normalized["id"] = normalized["agentId"]
        if "name" not in normalized and isinstance(normalized.get("agentId"), str):
            normalized["name"] = normalized["agentId"]
        if "last_heartbeat" not in normalized and normalized.get("lastHeartbeat") is not None:
            normalized["last_heartbeat"] = normalized["lastHeartbeat"]
        if "location" not in normalized:
            normalized["location"] = normalized.get("region") or "unknown"
        if "uptime" not in normalized:
            normalized["uptime"] = "unknown"
        if "status" in normalized and isinstance(normalized["status"], str):
            normalized["status"] = normalized["status"].lower()
        return normalized

    @field_validator("last_heartbeat", mode="before")
    @classmethod
    def parse_last_heartbeat(cls, value: Any) -> datetime:
        return _parse_dt(value)


class Policy(BaseModel):
    """Security policy configuration."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str = "Unnamed Policy"
    description: Optional[str] = None
    compliance_framework: Optional[str] = None
    rules: Dict[str, Any] = Field(default_factory=dict)
    enforcement_mode: PolicyMode = PolicyMode.OBSERVE
    is_active: bool = Field(default=True, alias="isActive")
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")
    created_by: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_policy_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        if "compliance_framework" not in normalized and isinstance(normalized.get("policyType"), str):
            normalized["compliance_framework"] = normalized["policyType"]
        if "enforcement_mode" in normalized and isinstance(normalized["enforcement_mode"], str):
            normalized["enforcement_mode"] = normalized["enforcement_mode"].lower()
        return normalized

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_policy_timestamps(cls, value: Any) -> datetime:
        return _parse_dt(value)

    @field_validator("rules", mode="before")
    @classmethod
    def normalize_rules(cls, value: Any) -> Dict[str, Any]:
        # Some live environments may return [] for legacy/empty rule payloads.
        # Normalize to a mapping so downstream SDK helpers remain stable.
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            return {"items": value}
        return {}


class PolicyTemplate(BaseModel):
    """Pre-built policy template."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str
    description: str = ""
    compliance_framework: Optional[str] = None
    algorithms: Dict[str, Any] = Field(default_factory=dict)
    recommended_for: List[str] = Field(default_factory=list)


class UsageMetrics(BaseModel):
    """Customer usage metrics."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    agents_deployed: int = 0
    policies_active: int = 0
    connections_processed: int = 0
    bytes_analyzed: int = 0
    uptime_percentage: float = 0.0
    period_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthScore(BaseModel):
    """Customer health score."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    overall_score: int = Field(default=0, ge=0, le=100)
    category_scores: Dict[str, int] = Field(default_factory=dict)
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    trend: str = "stable"
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityAlert(BaseModel):
    """Security alert information."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    title: str = ""
    description: str = ""
    severity: str = AlertSeverity.INFO
    category: str = "general"
    source: str = "axis"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    resolved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_alert_created_at(cls, value: Any) -> datetime:
        return _parse_dt(value)


class DiagnosticResult(BaseModel):
    """Diagnostic test result."""
    test_name: str = ""
    category: str = "system"
    status: str = "unknown"  # "passed", "failed", "warning"
    message: str = ""
    details: Optional[str] = None
    fix_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    duration_ms: int = 0


class CustomerInfo(BaseModel):
    """Customer account information."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    email: str
    company: str = ""
    plan: str = "unknown"
    status: str = "unknown"
    trial_ends_at: Optional[datetime] = Field(default=None, alias="trialEndsAt")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")

    @field_validator("trial_ends_at", "created_at", mode="before")
    @classmethod
    def parse_customer_dates(cls, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        return _parse_dt(value)


class SetupResult(BaseModel):
    """Quick setup operation result."""
    policy_id: str
    policy_name: str
    deployment_instructions: Dict[str, str]
    next_steps: List[str]


class SecurityStatus(BaseModel):
    """Comprehensive security status."""
    agents_online: str
    policies_active: int
    health_score: int
    critical_alerts: int
    recommendations: List[str]
    last_updated: datetime


class ComplianceValidationResult(BaseModel):
    """Compliance validation status for a single framework."""

    framework: str
    compliant: bool
    score: int = 0
    issues: List[str] = Field(default_factory=list)
    evaluated_count: int = 0


class PolicyUpdate(BaseModel):
    """Policy update specification."""
    policy_id: str
    changes: Dict[str, Any]
    description: Optional[str] = None


class BulkUpdateResult(BaseModel):
    """Bulk policy update result."""
    successful_updates: int
    failed_updates: int
    results: List[Policy]
    failures: List[tuple]


# Event models for real-time subscriptions
class AgentEvent(BaseModel):
    """Agent status change event."""
    event_type: str  # "agent.online", "agent.offline", "agent.updated"
    agent_id: str
    timestamp: datetime
    data: Dict[str, Any]


class PolicyEvent(BaseModel):
    """Policy change event."""
    event_type: str  # "policy.created", "policy.updated", "policy.deployed"
    policy_id: str
    timestamp: datetime
    data: Dict[str, Any]


class SecurityEvent(BaseModel):
    """Security-related event."""
    event_type: str  # "violation.detected", "threat.blocked", "crypto.compromised"
    severity: AlertSeverity
    timestamp: datetime
    source: str
    data: Dict[str, Any]


# Configuration builders for common scenarios
class PolicyBuilder:
    """Fluent interface for building custom policies."""
    
    def __init__(self):
        self._rules = {
            "compliance_standard": "Custom",
            "aegis": {},
            "somnus": {},
            "logos": {},
        }
        self._enforcement_mode = PolicyMode.OBSERVE
        
    def compliance_standard(self, standard: str) -> "PolicyBuilder":
        """Set compliance standard."""
        self._rules["compliance_standard"] = standard
        return self
        
    def aegis_config(self, **config) -> "PolicyBuilder":
        """Configure Aegis TLS settings."""
        self._rules["aegis"].update(config)
        return self
        
    def somnus_config(self, **config) -> "PolicyBuilder":
        """Configure Somnus encryption settings."""
        self._rules["somnus"].update(config)
        return self
        
    def logos_config(self, **config) -> "PolicyBuilder":
        """Configure Logos application crypto settings."""
        self._rules["logos"].update(config)
        return self
        
    def enforcement_mode(self, mode: PolicyMode) -> "PolicyBuilder":
        """Set policy enforcement mode."""
        self._enforcement_mode = mode
        return self
        
    def post_quantum_ready(self) -> "PolicyBuilder":
        """Enable post-quantum cryptography across all components."""
        self._rules["aegis"]["pq_ready"] = ["TLS_KYBER768_P256_SHA256"]
        self._rules["somnus"]["pq_ready"] = ["Kyber-768 + AES-KWP"]
        self._rules["logos"]["pq_ready"] = ["Kyber-768 + AES-KWP (DEK/Field Key Wrap)"]
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build the policy configuration."""
        return {
            "rules": self._rules,
            "enforcement_mode": self._enforcement_mode,
        }


class AgentConfigBuilder:
    """Fluent interface for building agent configurations."""
    
    def __init__(self):
        self._config = {
            "deployment_method": "helm",
            "namespace": "aegis-system",
            "replicas": 1,
            "resources": {
                "cpu": "100m",
                "memory": "128Mi",
            },
            "networking": {
                "listen_port": 8444,
                "health_port": 9080,
            },
        }
    
    def deployment_method(self, method: str) -> "AgentConfigBuilder":
        """Set deployment method (helm, docker, binary)."""
        self._config["deployment_method"] = method
        return self
        
    def namespace(self, namespace: str) -> "AgentConfigBuilder":
        """Set Kubernetes namespace."""
        self._config["namespace"] = namespace
        return self
        
    def replicas(self, count: int) -> "AgentConfigBuilder":
        """Set number of agent replicas."""
        self._config["replicas"] = count
        return self
        
    def resources(self, cpu: str, memory: str) -> "AgentConfigBuilder":
        """Set resource limits."""
        self._config["resources"] = {"cpu": cpu, "memory": memory}
        return self
        
    def backend_url(self, url: str) -> "AgentConfigBuilder":
        """Set backend URL for proxying."""
        self._config["networking"]["backend_url"] = url
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build the agent configuration."""
        return self._config


# Utility functions
def create_policy_from_template(
    template: ComplianceFramework,
    name: Optional[str] = None,
    **overrides,
) -> Dict[str, Any]:
    """Create a policy from a compliance template.
    
    Args:
        template: Compliance framework template
        name: Custom policy name
        **overrides: Template overrides
        
    Returns:
        Policy configuration dictionary
    """
    templates = {
        "soc2": {
            "name": name or "SOC2 Type II Compliance",
            "compliance_standard": "SOC2 Type II",
            "aegis": {
                "pq_ready": ["TLS_KYBER768_P256_SHA256"],
                "preferred": ["TLS_AES_256_GCM_SHA384"],
                "prohibited": ["TLS 1.0", "TLS 1.1", "SSL V2", "SSL V3"],
            },
        },
        "pci-dss": {
            "name": name or "PCI DSS 4.0 Compliance", 
            "compliance_standard": "PCI DSS 4.0",
            "aegis": {
                "pq_ready": ["TLS_KYBER768_P256_SHA256"],
                "preferred": ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"],
                "prohibited": ["SSLv2", "SSLv3", "TLS 1.0", "TLS 1.1", "RC4"],
            },
        },
        # Add other templates...
    }

    normalized_template = template.value if isinstance(template, ComplianceFramework) else str(template).lower()
    config = templates.get(normalized_template, {})
    config.update(overrides)
    return config
