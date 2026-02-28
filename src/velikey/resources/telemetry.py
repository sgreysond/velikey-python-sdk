"""Telemetry resource for VeliKey SDK."""

import asyncio
from typing import Any, AsyncGenerator, Dict, Optional

class TelemetryResource:
    """Access telemetry and metrics."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_metrics(
        self,
        tenant: Optional[str] = None,
        time_range: str = "1h",
    ) -> Dict[str, Any]:
        """Get current metrics."""
        params = {"period": "current", "timeRange": time_range}
        if tenant:
            params["tenant"] = tenant

        response = await self._client._request("GET", "/api/usage/summary", params=params)
        return response
    
    async def stream(
        self,
        agent_id: Optional[str] = None,
        interval_s: float = 5.0,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream real-time telemetry data."""
        # Polling fallback; websocket transport is not currently exposed by Axis.
        while True:
            params = {"period": "current"}
            if agent_id:
                params["agentId"] = agent_id

            try:
                response = await self._client._request("GET", "/api/usage/summary", params=params)
                yield response
            except Exception:
                yield {"status": "error", "message": "Telemetry poll failed"}

            await asyncio.sleep(max(0.5, interval_s))
    
    async def submit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit telemetry data."""
        response = await self._client._request("POST", "/api/telemetry/ingest", json_data=data)
        return response
