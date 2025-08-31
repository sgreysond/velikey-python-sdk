"""Tests for VeliKey Python SDK client."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from velikey import AegisClient, AegisClientSync
from velikey.exceptions import AuthenticationError, ValidationError


class TestAegisClient:
    """Test async client functionality."""

    @pytest.fixture
    def client(self):
        return AegisClient(
            api_key="test-api-key",
            base_url="https://api-test.velikey.com"
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initializes correctly."""
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://api-test.velikey.com"
        assert hasattr(client, 'agents')
        assert hasattr(client, 'policies')
        assert hasattr(client, 'monitoring')

    @pytest.mark.asyncio
    async def test_authentication_error(self, client):
        """Test authentication error handling."""
        with patch.object(client._client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"detail": "Unauthorized"}
            mock_request.return_value = mock_response
            
            with pytest.raises(AuthenticationError):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_validation_error(self, client):
        """Test validation error handling."""
        with patch.object(client._client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"detail": "Invalid request"}
            mock_request.return_value = mock_response
            
            with pytest.raises(ValidationError):
                await client._request("POST", "/test", json_data={"invalid": "data"})

    @pytest.mark.asyncio
    async def test_quick_setup(self, client):
        """Test quick setup functionality."""
        with patch.object(client, '_request') as mock_request:
            mock_request.return_value = {
                "policy_id": "test-policy-123",
                "policy_name": "Test Policy",
                "deployment_instructions": {"helm": "helm install..."},
                "next_steps": ["Deploy agents", "Verify connectivity"]
            }
            
            result = await client.quick_setup(
                compliance_framework="soc2",
                enforcement_mode="observe",
                post_quantum=True
            )
            
            assert result.policy_id == "test-policy-123"
            assert result.policy_name == "Test Policy"
            assert len(result.next_steps) == 2

    @pytest.mark.asyncio
    async def test_security_status(self, client):
        """Test security status retrieval."""
        # Mock agents.list()
        with patch.object(client.agents, 'list') as mock_agents:
            mock_agents.return_value = [
                Mock(id="agent-1", status="online"),
                Mock(id="agent-2", status="online"),
            ]
            
            # Mock policies.list()
            with patch.object(client.policies, 'list') as mock_policies:
                mock_policies.return_value = [
                    Mock(id="policy-1", is_active=True),
                ]
                
                # Mock monitoring.get_health_score()
                with patch.object(client.monitoring, 'get_health_score') as mock_health:
                    mock_health.return_value = Mock(
                        overall_score=85,
                        recommendations=["Enable post-quantum crypto"]
                    )
                    
                    # Mock monitoring.get_active_alerts()
                    with patch.object(client.monitoring, 'get_active_alerts') as mock_alerts:
                        mock_alerts.return_value = []
                        
                        status = await client.get_security_status()
                        
                        assert status.agents_online == "2/2"
                        assert status.policies_active == 1
                        assert status.health_score == 85
                        assert status.critical_alerts == 0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager usage."""
        async with AegisClient(api_key="test") as client:
            assert client.api_key == "test"
        # Client should be closed after context exit


class TestAegisClientSync:
    """Test synchronous client wrapper."""

    def test_sync_client_initialization(self):
        """Test sync client initializes correctly."""
        client = AegisClientSync(api_key="test-key")
        assert client._async_client.api_key == "test-key"

    def test_sync_method_calls(self):
        """Test sync method calls work."""
        with patch('velikey.client.asyncio.new_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.return_value = {"status": "ok"}
            
            client = AegisClientSync(api_key="test")
            
            # This would normally be an async call
            with patch.object(client._async_client, 'get_health') as mock_health:
                mock_health.return_value = {"status": "ok"}
                result = client.get_health()
                assert result == {"status": "ok"}


class TestPolicyBuilder:
    """Test policy builder functionality."""

    def test_policy_builder_creation(self):
        """Test policy builder creates correct configuration."""
        from velikey.models import PolicyBuilder
        
        builder = PolicyBuilder()
        config = builder \
            .compliance_standard("SOC2 Type II") \
            .post_quantum_ready() \
            .enforcement_mode("enforce") \
            .build()
        
        assert config["rules"]["compliance_standard"] == "SOC2 Type II"
        assert "pq_ready" in config["rules"]["aegis"]
        assert config["enforcement_mode"] == "enforce"

    def test_policy_template_creation(self):
        """Test policy creation from templates."""
        from velikey.models import create_policy_from_template, ComplianceFramework
        
        policy_config = create_policy_from_template(
            ComplianceFramework.SOC2,
            name="Custom SOC2 Policy"
        )
        
        assert policy_config["name"] == "Custom SOC2 Policy"
        assert policy_config["compliance_standard"] == "SOC2 Type II"
        assert "aegis" in policy_config


class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_client_factory(self):
        """Test client factory function."""
        from velikey import create_client, create_sync_client
        
        async_client = create_client("test-key")
        assert isinstance(async_client, AegisClient)
        assert async_client.api_key == "test-key"
        
        sync_client = create_sync_client("test-key")
        assert isinstance(sync_client, AegisClientSync)


@pytest.mark.integration
class TestIntegration:
    """Integration tests (require actual API or mock server)."""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow from setup to monitoring."""
        # This would run against a test API server
        pytest.skip("Integration test - requires test API server")
        
        client = AegisClient(api_key="test-integration-key")
        
        # 1. Quick setup
        setup = await client.quick_setup("soc2")
        assert setup.policy_id
        
        # 2. Verify policy creation
        policy = await client.policies.get(setup.policy_id)
        assert policy.name == setup.policy_name
        
        # 3. Check security status
        status = await client.get_security_status()
        assert status.health_score > 0
        
        await client.close()


# Fixtures for common test data
@pytest.fixture
def sample_agent():
    """Sample agent data for testing."""
    return {
        "id": "agent-123",
        "name": "Test Agent",
        "version": "1.0.0",
        "status": "online",
        "location": "us-west-2",
        "capabilities": ["monitoring", "encryption"],
        "last_heartbeat": "2024-01-01T12:00:00Z",
        "uptime": "2h 30m",
        "metadata": {}
    }

@pytest.fixture
def sample_policy():
    """Sample policy data for testing."""
    return {
        "id": "policy-123",
        "name": "Test Policy",
        "compliance_framework": "soc2",
        "rules": {
            "compliance_standard": "SOC2 Type II",
            "aegis": {
                "preferred": ["TLS_AES_256_GCM_SHA384"],
                "prohibited": ["TLS 1.0", "TLS 1.1"]
            }
        },
        "enforcement_mode": "observe",
        "is_active": True,
        "version": 1,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
