"""VeliKey data models and types."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator, validator


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    UPDATING = "updating"
    ERROR = "error"
    DEGRADED = "degraded"


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
    id: str
    name: str
    version: str
    status: AgentStatus
    location: str
    capabilities: List[str]
    last_heartbeat: datetime
    uptime: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('last_heartbeat', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class Policy(BaseModel):
    """Security policy configuration."""
    id: str
    name: str
    description: Optional[str] = None
    compliance_framework: ComplianceFramework
    rules: Dict[str, Any]
    enforcement_mode: PolicyMode = PolicyMode.OBSERVE
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    @validator('created_at', 'updated_at', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v

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
    id: str
    name: str
    description: str
    compliance_framework: ComplianceFramework
    algorithms: Dict[str, Any]
    recommended_for: List[str] = Field(default_factory=list)


class UsageMetrics(BaseModel):
    """Customer usage metrics."""
    agents_deployed: int
    policies_active: int
    connections_processed: int
    bytes_analyzed: int
    uptime_percentage: float
    period_start: datetime
    period_end: datetime


class HealthScore(BaseModel):
    """Customer health score."""
    overall_score: int = Field(ge=0, le=100)
    category_scores: Dict[str, int]
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    trend: str = "stable"
    calculated_at: datetime


class SecurityAlert(BaseModel):
    """Security alert information."""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    category: str
    source: str
    created_at: datetime
    resolved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DiagnosticResult(BaseModel):
    """Diagnostic test result."""
    test_name: str
    category: str
    status: str  # "passed", "failed", "warning"
    message: str
    details: Optional[str] = None
    fix_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    duration_ms: int


class CustomerInfo(BaseModel):
    """Customer account information."""
    id: str
    email: str
    company: str
    plan: str
    status: str
    trial_ends_at: Optional[datetime] = None
    created_at: datetime


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
        ComplianceFramework.SOC2: {
            "name": name or "SOC2 Type II Compliance",
            "compliance_standard": "SOC2 Type II",
            "aegis": {
                "pq_ready": ["TLS_KYBER768_P256_SHA256"],
                "preferred": ["TLS_AES_256_GCM_SHA384"],
                "prohibited": ["TLS 1.0", "TLS 1.1", "SSL V2", "SSL V3"],
            },
        },
        ComplianceFramework.PCI_DSS: {
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
    
    config = templates.get(template, {})
    config.update(overrides)
    return config
