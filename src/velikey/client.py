"""VeliKey Aegis Python Client."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from .exceptions import AuthenticationError, NotFoundError, RateLimitError, ValidationError, VeliKeyError
from .models import BulkUpdateResult, CustomerInfo, PolicyUpdate, SecurityStatus, SetupResult
from .resources import (
    AgentsResource,
    BillingResource,
    ComplianceResource,
    DiagnosticsResource,
    MonitoringResource,
    PoliciesResource,
    RolloutsResource,
    TelemetryResource,
)
from .version import __version__


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
        api_key: Optional[str] = None,
        session_cookie: Optional[str] = None,
        base_url: str = "https://api.velikey.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ):
        """Initialize the VeliKey client.
        
        Args:
            api_key: Your VeliKey API key (bearer token style)
            session_cookie: Optional NextAuth session cookie value
            base_url: API base URL (default: https://api.velikey.com)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts for failed requests
            verify_ssl: Whether to verify SSL certificates
        """
        if not api_key and not session_cookie:
            raise ValueError("Either api_key or session_cookie must be provided")

        self.api_key = api_key
        self.session_cookie = self._normalize_session_cookie(session_cookie)
        self.base_url = base_url.rstrip("/")
        self.max_retries = max(0, int(max_retries))

        headers = {
            "Accept": "application/json",
            "User-Agent": f"velikey-python-sdk/{__version__}",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if self.session_cookie:
            headers["Cookie"] = self.session_cookie

        self._client = httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl,
            headers=headers,
        )

        # Initialize resource managers
        self.agents = AgentsResource(self)
        self.policies = PoliciesResource(self)
        self.monitoring = MonitoringResource(self)
        self.compliance = ComplianceResource(self)
        self.diagnostics = DiagnosticsResource(self)
        self.billing = BillingResource(self)
        self.rollouts = RolloutsResource(self)
        self.telemetry = TelemetryResource(self)

    @staticmethod
    def _normalize_session_cookie(session_cookie: Optional[str]) -> Optional[str]:
        if not session_cookie:
            return None
        normalized = session_cookie.strip()
        if "=" in normalized:
            return normalized
        return f"next-auth.session-token={normalized}"

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except Exception:
            payload = None

        if isinstance(payload, dict):
            for key in ("detail", "error", "message"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value

        if response.text:
            return response.text[:500]
        return f"HTTP {response.status_code}"

    async def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code < 400:
            return

        error_detail = self._extract_error_message(response)
        if response.status_code == 401:
            raise AuthenticationError(error_detail or "Invalid credentials", status_code=401)
        if response.status_code == 400:
            raise ValidationError(error_detail or "Invalid request", status_code=400)
        if response.status_code == 404:
            raise NotFoundError(error_detail or "Resource not found", status_code=404)
        if response.status_code == 429:
            raise RateLimitError(error_detail or "Rate limit exceeded", status_code=429)
        raise VeliKeyError(error_detail or f"HTTP {response.status_code}", status_code=response.status_code)

    @staticmethod
    async def _maybe_sleep_for_retry(response: Optional[httpx.Response], attempt: int) -> None:
        retry_after = None
        if response is not None:
            retry_after_header = response.headers.get("Retry-After")
            if retry_after_header:
                try:
                    retry_after = float(retry_after_header)
                except ValueError:
                    retry_after = None
        if retry_after is None:
            retry_after = min(2.0, 0.25 * (2 ** attempt))
        await asyncio.sleep(max(0.0, retry_after))

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
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
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
        if "json" in kwargs and json_data is None:
            json_data = kwargs.pop("json")

        url = f"{self.base_url}{endpoint}"
        retryable_statuses = {429, 500, 502, 503, 504}
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    **kwargs,
                )

                if response.status_code in retryable_statuses and attempt < self.max_retries:
                    await self._maybe_sleep_for_retry(response, attempt)
                    continue

                await self._raise_for_status(response)

                if not response.content:
                    return {}
                try:
                    parsed = response.json()
                except ValueError:
                    return {"raw": response.text}
                return parsed if isinstance(parsed, dict) else {"data": parsed}
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RequestError) as error:
                last_error = error
                if attempt >= self.max_retries:
                    break
                await self._maybe_sleep_for_retry(None, attempt)
                continue

        raise VeliKeyError(f"Request failed after retries: {last_error}")

    async def get_health(self) -> Dict[str, str]:
        """Get API health status.
        
        Returns:
            Health status information
        """
        try:
            return await self._request("GET", "/api/healthz")
        except VeliKeyError:
            return await self._request("GET", "/health")

    async def get_customer_info(self) -> CustomerInfo:
        """Get current customer information.
        
        Returns:
            Customer account information
        """
        data = await self._request("GET", "/api/user/profile")
        payload = data.get("user", data)
        return CustomerInfo(**payload)

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
        try:
            data = await self._request("POST", "/api/setup/quick", json_data=payload)
        except NotFoundError as error:
            raise VeliKeyError(
                (
                    "Unsupported operation: quick_setup. "
                    "Axis does not currently expose POST /api/setup/quick."
                ),
                status_code=501,
            ) from error
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


class _SyncResourceProxy:
    """Wrap an async resource and expose sync methods."""

    def __init__(self, resource: Any, runner):
        self._resource = resource
        self._runner = runner

    def __getattr__(self, name: str):
        attr = getattr(self._resource, name)
        if not callable(attr):
            return attr

        def sync_wrapper(*args, **kwargs):
            result = attr(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return self._runner(result)
            return result

        return sync_wrapper


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
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        return self._loop.run_until_complete(coro)

    def __getattr__(self, name):
        """Proxy attribute access to async client."""
        attr = getattr(self._async_client, name)

        if name in {
            "agents",
            "policies",
            "monitoring",
            "compliance",
            "diagnostics",
            "billing",
            "rollouts",
            "telemetry",
        }:
            return _SyncResourceProxy(attr, self._run_async)

        if callable(attr):
            def sync_wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    return self._run_async(result)
                return result
            return sync_wrapper
        return attr

    def close(self):
        """Close the client and event loop."""
        if self._loop is not None:
            self._loop.run_until_complete(self._async_client.close())
            self._loop.close()
            self._loop = None


# Convenience factory functions
def create_client(
    api_key: Optional[str] = None,
    session_cookie: Optional[str] = None,
    **kwargs,
) -> AegisClient:
    """Create an async VeliKey client.
    
    Args:
        api_key: Optional VeliKey API key
        session_cookie: Optional NextAuth session cookie value
        **kwargs: Additional client configuration
        
    Returns:
        Configured AegisClient instance
    """
    return AegisClient(api_key=api_key, session_cookie=session_cookie, **kwargs)


def create_sync_client(
    api_key: Optional[str] = None,
    session_cookie: Optional[str] = None,
    **kwargs,
) -> AegisClientSync:
    """Create a synchronous VeliKey client.
    
    Args:
        api_key: Optional VeliKey API key
        session_cookie: Optional NextAuth session cookie value
        **kwargs: Additional client configuration
        
    Returns:
        Configured AegisClientSync instance
    """
    return AegisClientSync(api_key=api_key, session_cookie=session_cookie, **kwargs)
