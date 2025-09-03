"""VeliKey Aegis Python Client."""

import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import httpx
from .models import *
from .exceptions import *
from .resources import (
    AgentsResource,
    PoliciesResource,
    MonitoringResource,
    ComplianceResource,
    DiagnosticsResource,
    BillingResource,
)
from . import __version__


class AegisClient:
    """Main client for VeliKey Aegis API.
    
    Examples:
        Basic usage:
        >>> client = AegisClient(api_key="your-api-key")
        >>> agents = await client.agents.list()
        >>> print(f"Found {len(agents)} agents")
        
        Policy management:
        >>> policy = await client.policies.create_from_template("soc2")
        >>> await client.policies.deploy(policy.id)
        
        Real-time monitoring:
        >>> metrics = await client.monitoring.get_live_metrics()
        >>> if metrics.policy_violations > 0:
        ...     await client.monitoring.create_alert("Policy violations detected")
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.velikey.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ):
        """Initialize the VeliKey client.
        
        Args:
            api_key: Your VeliKey API key
            base_url: API base URL (default: https://api.velikey.com)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts for failed requests
            verify_ssl: Whether to verify SSL certificates
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        
        self._client = httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"velikey-python-sdk/{__version__}",
                "Content-Type": "application/json",
            },
        )
        
        # Initialize resource managers
        self.agents = AgentsResource(self)
        self.policies = PoliciesResource(self)
        self.monitoring = MonitoringResource(self)
        self.compliance = ComplianceResource(self)
        self.diagnostics = DiagnosticsResource(self)
        self.billing = BillingResource(self)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """Make an authenticated request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON request body
            **kwargs: Additional httpx request parameters
            
        Returns:
            Response JSON data
            
        Raises:
            AuthenticationError: Invalid API key or expired token
            ValidationError: Invalid request data
            RateLimitError: Rate limit exceeded
            NotFoundError: Resource not found
            VeliKeyError: Other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                **kwargs,
            )
            
            # Handle HTTP errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or expired token")
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Invalid request")
                raise ValidationError(error_detail)
            elif response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_detail = response.json().get("detail", f"HTTP {response.status_code}")
                raise VeliKeyError(error_detail)
            
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            raise VeliKeyError(f"Request failed: {e}")

    async def get_health(self) -> Dict[str, str]:
        """Get API health status.
        
        Returns:
            Health status information
        """
        return await self._request("GET", "/health")

    async def get_customer_info(self) -> CustomerInfo:
        """Get current customer information.
        
        Returns:
            Customer account information
        """
        data = await self._request("GET", "/api/customers/profile")
        return CustomerInfo(**data)

    # Convenience methods for common operations
    async def quick_setup(
        self,
        compliance_framework: str = "soc2",
        enforcement_mode: str = "observe",
        post_quantum: bool = True,
    ) -> SetupResult:
        """Quick setup for new customers (single API call used in tests)."""
        payload = {
            "complianceFramework": compliance_framework,
            "enforcementMode": enforcement_mode,
            "postQuantum": post_quantum,
        }
        data = await self._request("POST", "/api/setup/quick", json_data=payload)
        return SetupResult(
            policy_id=data.get("policy_id", ""),
            policy_name=data.get("policy_name", ""),
            deployment_instructions=data.get("deployment_instructions", {}),
            next_steps=data.get("next_steps", []),
        )

    async def get_security_status(self) -> SecurityStatus:
        """Get comprehensive security status.
        
        Returns:
            Current security posture and recommendations
        """
        # Gather data from multiple endpoints
        agents = await self.agents.list()
        policies = await self.policies.list()
        health = await self.monitoring.get_health_score()
        alerts = await self.monitoring.get_active_alerts()
        
        # Calculate security metrics
        total_agents = len(agents)
        online_agents = len([a for a in agents if a.status == "online"])
        active_policies = len([p for p in policies if p.is_active])
        critical_alerts = len([a for a in alerts if a.severity == "critical"])
        
        return SecurityStatus(
            agents_online=f"{online_agents}/{total_agents}",
            policies_active=active_policies,
            health_score=health.overall_score,
            critical_alerts=critical_alerts,
            recommendations=health.recommendations,
            last_updated=datetime.now(),
        )

    async def bulk_policy_update(
        self,
        policy_updates: List[PolicyUpdate],
        rollback_on_failure: bool = True,
    ) -> BulkUpdateResult:
        """Update multiple policies atomically.
        
        Args:
            policy_updates: List of policy updates to apply
            rollback_on_failure: Whether to rollback all changes if any fail
            
        Returns:
            Results of bulk update operation
        """
        results = []
        failed_updates = []
        
        for update in policy_updates:
            try:
                result = await self.policies.update(update.policy_id, update.changes)
                results.append(result)
            except Exception as e:
                failed_updates.append((update, str(e)))
                if rollback_on_failure:
                    # Rollback previous updates
                    for prev_result in results:
                        try:
                            await self.policies.rollback(prev_result.id)
                        except Exception:
                            pass  # Best effort rollback
                    raise VeliKeyError(f"Bulk update failed: {e}")
        
        return BulkUpdateResult(
            successful_updates=len(results),
            failed_updates=len(failed_updates),
            results=results,
            failures=failed_updates,
        )


# Synchronous wrapper for non-async environments
class AegisClientSync:
    """Synchronous wrapper for AegisClient.
    
    Examples:
        >>> client = AegisClientSync(api_key="your-api-key")
        >>> agents = client.agents.list()
        >>> print(f"Found {len(agents)} agents")
    """
    
    def __init__(self, **kwargs):
        self._async_client = AegisClient(**kwargs)
        self._loop = None

    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        return self._loop.run_until_complete(coro)

    def __getattr__(self, name):
        """Proxy attribute access to async client."""
        attr = getattr(self._async_client, name)
        if hasattr(attr, '__call__'):
            def sync_wrapper(*args, **kwargs):
                return self._run_async(attr(*args, **kwargs))
            return sync_wrapper
        return attr

    def close(self):
        """Close the client and event loop."""
        if self._loop:
            self._loop.run_until_complete(self._async_client.close())
            self._loop.close()


# Convenience factory functions
def create_client(api_key: str, **kwargs) -> AegisClient:
    """Create an async VeliKey client.
    
    Args:
        api_key: Your VeliKey API key
        **kwargs: Additional client configuration
        
    Returns:
        Configured AegisClient instance
    """
    return AegisClient(api_key=api_key, **kwargs)


def create_sync_client(api_key: str, **kwargs) -> AegisClientSync:
    """Create a synchronous VeliKey client.
    
    Args:
        api_key: Your VeliKey API key
        **kwargs: Additional client configuration
        
    Returns:
        Configured AegisClientSync instance
    """
    return AegisClientSync(api_key=api_key, **kwargs)
