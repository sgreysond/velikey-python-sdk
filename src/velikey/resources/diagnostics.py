"""Diagnostics resource for VeliKey SDK."""

from typing import Any, Dict

class DiagnosticsResource:
    """System diagnostics and troubleshooting."""
    
    def __init__(self, client):
        self._client = client
    
    async def run_check(self, check_type: str = 'full') -> Dict[str, Any]:
        """Run system diagnostics."""
        health = await self._client._request("GET", "/api/health")
        return {
            "checkType": check_type,
            "status": health.get("status", "unknown"),
            "checks": health.get("checks", {}),
            "timestamp": health.get("timestamp"),
        }
    
    async def get_logs(self, agent_id: str, lines: int = 100) -> Dict[str, Any]:
        """Get agent logs."""
        params = {"lines": str(lines)}
        response = await self._client._request("GET", f"/api/agents/{agent_id}/metrics", params=params)
        return response
