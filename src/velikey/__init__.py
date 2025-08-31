"""VeliKey Aegis Python SDK - Quantum-safe crypto policy management."""

from .client import AegisClient
from .models import (
    Agent,
    Policy,
    PolicyTemplate,
    ComplianceFramework,
    HealthScore,
    UsageMetrics,
    SecurityAlert,
    DiagnosticResult,
)
from .exceptions import (
    VeliKeyError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
)

__version__ = "0.1.0"
__all__ = [
    "AegisClient",
    "Agent",
    "Policy", 
    "PolicyTemplate",
    "ComplianceFramework",
    "HealthScore",
    "UsageMetrics",
    "SecurityAlert",
    "DiagnosticResult",
    "VeliKeyError",
    "AuthenticationError",
    "ValidationError", 
    "RateLimitError",
    "NotFoundError",
]
