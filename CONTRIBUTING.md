# Contributing to VeliKey Python SDK

We welcome contributions to the VeliKey Python SDK! This document provides guidelines for contributing to the Python client library for VeliKey Aegis.

## Development Environment

### Prerequisites

- **Python**: 3.8+ (recommended: use pyenv)
- **pip**: Python package manager (or poetry/pipenv)
- **Git**: For version control
- **VeliKey Aegis**: Access to control plane for testing

### Setup

```bash
# Clone the repository
git clone https://github.com/velikey/velikey-python-sdk.git
cd velikey-python-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,docs]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow [[memory:7696176]]

1. **Create a feature branch** from `main`
2. **Make your changes** with appropriate tests
3. **Run quality checks**:
   ```bash
   python -m pytest
   black src tests
   isort src tests  
   mypy src
   flake8 src tests
   ```
4. **Commit with conventional messages** (feat, fix, chore, docs, refactor)
5. **Open a Pull Request** with clear description
6. **Address review feedback** promptly

## Code Quality Standards

### Testing Requirements [[memory:7696167]]

All contributions must include comprehensive testing:

- **Unit Tests**: Individual function and class testing
- **Integration Tests**: API integration testing
- **End-to-End Tests**: Complete workflow testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/               # Unit tests only
pytest tests/integration/        # Integration tests
pytest tests/e2e/               # End-to-end tests

# Run with coverage
pytest --cov=velikey --cov-report=html --cov-report=term

# Run async tests
pytest -v tests/test_async.py
```

### Code Style

We use strict code formatting and linting:

```bash
# Format code
black src tests
isort src tests

# Check formatting
black --check src tests
isort --check-only src tests

# Type checking
mypy src

# Linting
flake8 src tests

# Security checking
bandit -r src/
```

### Code Quality Tools Configuration

The project uses these tools with specific configurations:

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.8"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
asyncio_mode = "auto"
```

## Project Structure

```
src/velikey/
├── __init__.py              # Package exports
├── client.py                # Main client classes
├── models.py                # Data models and types
├── exceptions.py            # Custom exceptions
├── resources/               # API resource modules
│   ├── __init__.py
│   ├── agents.py           # Agent management
│   ├── policies.py         # Policy management
│   ├── monitoring.py       # Metrics and alerts
│   ├── compliance.py       # Compliance validation
│   └── diagnostics.py      # System diagnostics
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── auth.py            # Authentication helpers
│   ├── formatting.py      # Output formatting
│   └── validation.py      # Input validation
└── _internal/             # Internal modules
    ├── __init__.py
    ├── http.py            # HTTP client wrapper
    └── config.py          # Configuration management

tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests  
├── e2e/                  # End-to-end tests
├── fixtures/             # Test fixtures
└── conftest.py           # Pytest configuration

examples/                 # Usage examples
docs/                    # Documentation source
```

## API Design Guidelines

### Client Architecture

The SDK follows a resource-based architecture:

```python
# Main client class
class AegisClient:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self._http_client = HttpClient(api_key, base_url)
        
        # Resource properties
        self.agents = AgentsResource(self._http_client)
        self.policies = PoliciesResource(self._http_client)
        self.monitoring = MonitoringResource(self._http_client)
        self.compliance = ComplianceResource(self._http_client)
        self.diagnostics = DiagnosticsResource(self._http_client)
    
    async def quick_setup(
        self, 
        compliance_framework: str,
        enforcement_mode: str = "observe",
        post_quantum: bool = True
    ) -> QuickSetupResult:
        """High-level setup method for new customers."""
        # Implementation
        
    async def get_security_status(self) -> SecurityStatus:
        """Get overall security status and health score."""
        # Implementation
        
    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self._http_client.close()
```

### Resource Classes

Each resource follows consistent patterns:

```python
class PoliciesResource:
    def __init__(self, http_client: HttpClient):
        self._http = http_client
    
    async def list(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filter: Optional[str] = None
    ) -> List[Policy]:
        """List policies with optional filtering."""
        # Implementation
    
    async def get(self, policy_id: str) -> Policy:
        """Get a specific policy by ID."""
        # Implementation
    
    async def create(
        self,
        name: str,
        rules: Dict[str, Any],
        compliance_framework: Optional[str] = None
    ) -> Policy:
        """Create a new policy."""
        # Implementation
    
    async def update(
        self,
        policy_id: str,
        **kwargs: Any
    ) -> Policy:
        """Update an existing policy."""
        # Implementation
    
    async def delete(self, policy_id: str) -> None:
        """Delete a policy."""
        # Implementation
    
    async def deploy(
        self,
        policy_id: str,
        target_agents: Optional[List[str]] = None
    ) -> PolicyDeployment:
        """Deploy policy to agents."""
        # Implementation
```

### Data Models

Use Pydantic for data validation and serialization:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Policy(BaseModel):
    id: str
    name: str
    compliance_framework: Optional[str] = None
    enforcement_mode: Literal["observe", "enforce"]
    rules: Dict[str, Any]
    status: Literal["draft", "active", "archived"]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        extra = "ignore"  # Ignore unknown fields

class SecurityStatus(BaseModel):
    health_score: int = Field(..., ge=0, le=100)
    agents_online: str  # Format: "5/10"
    critical_alerts: int = Field(..., ge=0)
    policy_compliance: float = Field(..., ge=0.0, le=1.0)
    last_updated: datetime

class QuickSetupResult(BaseModel):
    policy_id: str
    policy_name: str
    agents_targeted: int
    deployment_status: str
    next_steps: List[str]
```

### Error Handling

Define clear exception hierarchy:

```python
class VeliKeyError(Exception):
    """Base exception for all VeliKey SDK errors."""
    
    def __init__(self, message: str, response: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.response = response

class AuthenticationError(VeliKeyError):
    """Authentication failed."""
    pass

class AuthorizationError(VeliKeyError):
    """Insufficient permissions."""
    pass

class ValidationError(VeliKeyError):
    """Input validation failed."""
    pass

class ApiError(VeliKeyError):
    """API request failed."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int, 
        response: Optional[Dict] = None
    ):
        super().__init__(message, response)
        self.status_code = status_code

class RateLimitError(ApiError):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.retry_after = retry_after
```

## Adding New Features

### Adding a New Resource

1. **Create resource module**:
```python
# src/velikey/resources/certificates.py
from typing import List, Optional
from ..models import Certificate
from .._internal.http import HttpClient

class CertificatesResource:
    def __init__(self, http_client: HttpClient):
        self._http = http_client
    
    async def list(self) -> List[Certificate]:
        """List all certificates."""
        response = await self._http.get("/certificates")
        return [Certificate(**cert) for cert in response["certificates"]]
    
    async def validate(self, cert_id: str) -> CertificateValidation:
        """Validate a certificate."""
        response = await self._http.post(f"/certificates/{cert_id}/validate")
        return CertificateValidation(**response)
```

2. **Add to main client**:
```python
# src/velikey/client.py
from .resources.certificates import CertificatesResource

class AegisClient:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        # ... existing code ...
        self.certificates = CertificatesResource(self._http_client)
```

3. **Write comprehensive tests**:
```python
# tests/unit/resources/test_certificates.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from velikey.resources.certificates import CertificatesResource
from velikey.models import Certificate

@pytest.fixture
def certificates_resource():
    http_client = AsyncMock()
    return CertificatesResource(http_client)

@pytest.mark.asyncio
async def test_list_certificates(certificates_resource):
    # Mock response
    certificates_resource._http.get.return_value = {
        "certificates": [
            {
                "id": "cert_123",
                "subject": "CN=example.com",
                "valid_from": "2024-01-01T00:00:00Z",
                "valid_to": "2025-01-01T00:00:00Z"
            }
        ]
    }
    
    certificates = await certificates_resource.list()
    
    assert len(certificates) == 1
    assert certificates[0].id == "cert_123"
    assert certificates[0].subject == "CN=example.com"
    certificates_resource._http.get.assert_called_once_with("/certificates")
```

### Adding Async/Sync Support

Provide both async and sync clients:

```python
# src/velikey/client.py
import asyncio
from typing import TypeVar, Callable, Any

T = TypeVar('T')

def sync_wrapper(async_func: Callable[..., T]) -> Callable[..., T]:
    """Wrap async function to work synchronously."""
    def wrapper(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))
    return wrapper

class AegisClientSync:
    """Synchronous version of AegisClient."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self._async_client = AegisClient(api_key, base_url)
        
        # Create sync versions of all methods
        self.get_security_status = sync_wrapper(
            self._async_client.get_security_status
        )
        self.quick_setup = sync_wrapper(self._async_client.quick_setup)
        
        # Wrap resource methods
        self.agents = self._wrap_resource(self._async_client.agents)
        self.policies = self._wrap_resource(self._async_client.policies)
    
    def _wrap_resource(self, async_resource):
        """Create sync wrapper for resource methods."""
        class SyncWrapper:
            def __init__(self, async_resource):
                self._async = async_resource
                
            def __getattr__(self, name):
                attr = getattr(self._async, name)
                if callable(attr):
                    return sync_wrapper(attr)
                return attr
        
        return SyncWrapper(async_resource)
    
    def close(self) -> None:
        """Close the client."""
        asyncio.run(self._async_client.close())
```

## Testing Guidelines

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, patch
from velikey import AegisClient
from velikey.exceptions import AuthenticationError

@pytest.mark.asyncio
async def test_client_authentication_failure():
    with patch('velikey._internal.http.HttpClient') as mock_http:
        mock_http.return_value.get.side_effect = AuthenticationError(
            "Invalid API key"
        )
        
        client = AegisClient("invalid_key")
        
        with pytest.raises(AuthenticationError):
            await client.get_security_status()

@pytest.mark.asyncio
async def test_policy_creation():
    client = AegisClient("test_key")
    
    with patch.object(client.policies, 'create') as mock_create:
        mock_create.return_value = Policy(
            id="pol_123",
            name="Test Policy",
            enforcement_mode="observe",
            rules={},
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        policy = await client.policies.create(
            name="Test Policy",
            rules={"tls": {"min_version": "1.2"}}
        )
        
        assert policy.name == "Test Policy"
        assert policy.enforcement_mode == "observe"
        mock_create.assert_called_once()
```

### Integration Testing

```python
# tests/integration/test_client_integration.py
import pytest
import os
from velikey import AegisClient

# Skip if no API key provided
pytestmark = pytest.mark.skipif(
    not os.getenv("VELIKEY_TEST_API_KEY"),
    reason="No test API key provided"
)

@pytest.fixture
async def client():
    client = AegisClient(os.getenv("VELIKEY_TEST_API_KEY"))
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_get_security_status_integration(client):
    status = await client.get_security_status()
    
    assert isinstance(status.health_score, int)
    assert 0 <= status.health_score <= 100
    assert "/" in status.agents_online  # Format: "5/10"
    assert isinstance(status.critical_alerts, int)

@pytest.mark.asyncio
async def test_policy_crud_integration(client):
    # Create policy
    policy = await client.policies.create(
        name="Test Integration Policy",
        rules={"tls": {"min_version": "1.2"}},
        compliance_framework="soc2"
    )
    
    assert policy.name == "Test Integration Policy"
    assert policy.status in ["draft", "active"]
    
    try:
        # Get policy
        retrieved = await client.policies.get(policy.id)
        assert retrieved.id == policy.id
        assert retrieved.name == policy.name
        
        # Update policy
        updated = await client.policies.update(
            policy.id,
            enforcement_mode="enforce"
        )
        assert updated.enforcement_mode == "enforce"
        
    finally:
        # Clean up
        await client.policies.delete(policy.id)
```

### Mocking External Services

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock
import httpx

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    mock = AsyncMock()
    mock.get = AsyncMock()
    mock.post = AsyncMock()
    mock.put = AsyncMock()
    mock.delete = AsyncMock()
    return mock

@pytest.fixture
def mock_responses():
    """Common mock responses for tests."""
    return {
        "security_status": {
            "health_score": 85,
            "agents_online": "5/10",
            "critical_alerts": 0,
            "policy_compliance": 0.92,
            "last_updated": "2024-01-15T10:30:00Z"
        },
        "agents": [
            {
                "id": "agent_123",
                "name": "prod-agent-1",
                "status": "online",
                "last_seen": "2024-01-15T10:25:00Z"
            }
        ]
    }
```

## Documentation

### Docstring Standards

Use Google-style docstrings:

```python
async def create_policy(
    self,
    name: str,
    rules: Dict[str, Any],
    compliance_framework: Optional[str] = None,
    enforcement_mode: str = "observe"
) -> Policy:
    """Create a new security policy.
    
    Args:
        name: Human-readable name for the policy
        rules: Policy rules configuration as a dictionary
        compliance_framework: Optional compliance framework (soc2, pci-dss, hipaa)
        enforcement_mode: Policy enforcement mode (observe or enforce)
    
    Returns:
        The created Policy object
    
    Raises:
        ValidationError: If the policy configuration is invalid
        AuthenticationError: If the API key is invalid
        ApiError: If the API request fails
    
    Example:
        >>> client = AegisClient("sk_test_123...")
        >>> policy = await client.policies.create(
        ...     name="Production Security Policy",
        ...     rules={"tls": {"min_version": "1.2"}},
        ...     compliance_framework="soc2"
        ... )
        >>> print(f"Created policy: {policy.name}")
    """
    # Implementation
```

### Type Hints

Use comprehensive type hints:

```python
from typing import List, Optional, Dict, Any, Union, TypeVar, Generic, Awaitable
from typing_extensions import Literal  # For Python < 3.8

# Generic types for resources
ResourceT = TypeVar('ResourceT')

class BaseResource(Generic[ResourceT]):
    """Base class for API resources."""
    
    def __init__(self, http_client: HttpClient, resource_class: type[ResourceT]):
        self._http = http_client
        self._resource_class = resource_class
    
    async def get(self, resource_id: str) -> ResourceT:
        """Get resource by ID."""
        # Implementation

# Union types for flexible parameters
PolicyIdentifier = Union[str, Policy]  # Accept either policy ID or Policy object

# Literal types for restricted values
EnforcementMode = Literal["observe", "enforce"]
ComplianceFramework = Literal["soc2", "pci-dss", "hipaa", "gdpr"]
```

## Performance Considerations

### Async/Await Best Practices

```python
import asyncio
from typing import List

class AegisClient:
    async def bulk_operation_example(self, policy_ids: List[str]) -> List[Policy]:
        """Example of efficient bulk operations."""
        
        # Good: Concurrent execution
        tasks = [self.policies.get(policy_id) for policy_id in policy_ids]
        policies = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        results = []
        for policy in policies:
            if isinstance(policy, Exception):
                # Log error or handle as appropriate
                continue
            results.append(policy)
        
        return results
    
    async def with_retry(self, operation: Awaitable[T], max_retries: int = 3) -> T:
        """Retry operations with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await operation
            except (ConnectionError, TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
```

### Memory Management

```python
class AegisClient:
    def __init__(self, api_key: str):
        self._session = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=10)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, '_session'):
            await self._session.aclose()

# Usage with context manager
async with AegisClient("sk_test_123...") as client:
    status = await client.get_security_status()
    # Client automatically closed
```

## Git Commit Guidelines

Use conventional commit messages:

```
feat(client): add bulk policy operations
fix(auth): handle token refresh edge case
docs(readme): update installation examples
test(policies): add comprehensive validation tests
refactor(http): improve error handling
```

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**
3. **Build and test**:
   ```bash
   python -m build
   twine check dist/*
   ```
4. **Test upload** to TestPyPI:
   ```bash
   twine upload --repository testpypi dist/*
   ```
5. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## Getting Help

- **GitHub Discussions**: For questions and ideas
- **GitHub Issues**: For bug reports and feature requests
- **Community Forum**: [community.velikey.com](https://community.velikey.com)
- **Email**: [python-sdk@velikey.com](mailto:python-sdk@velikey.com)

## License

By contributing to VeliKey Python SDK, you agree that your contributions will be licensed under the MIT License.
