"""VeliKey Aegis Python SDK - Quantum-safe crypto policy management."""

from .version import __version__
from .client import AegisClient, AegisClientSync, create_client, create_sync_client
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

# Backwards-compatible aliases expected by tests
Client = AegisClient

__all__ = [
    "AegisClient",
    "AegisClientSync",
    "Client",
    "create_client",
    "create_sync_client",
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
