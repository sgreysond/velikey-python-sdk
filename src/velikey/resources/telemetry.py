"""
Telemetry resource for VeliKey SDK
"""

from typing import Dict, Any, Optional, AsyncGenerator
import asyncio

class TelemetryResource:
    """Access telemetry and metrics."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_metrics(self, 
                         tenant: Optional[str] = None,
                         time_range: str = '1h') -> Dict[str, Any]:
        """Get current metrics."""
        params = {'time_range': time_range}
        if tenant:
            params['tenant'] = tenant
            
        response = await self._client._request('GET', '/telemetry/metrics', params=params)
        return response
    
    async def stream(self, 
                     agent_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream real-time telemetry data."""
        # This would typically use WebSocket, but for now we'll simulate with polling
        while True:
            params = {}
            if agent_id:
                params['agent_id'] = agent_id
                
            try:
                response = await self._client._request('GET', '/telemetry/stream', params=params)
                yield response
            except Exception as e:
                # In real implementation, handle WebSocket errors
                print(f"Telemetry stream error: {e}")
                
            await asyncio.sleep(5)  # Poll every 5 seconds
    
    async def submit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit telemetry data."""
        response = await self._client._request('POST', '/telemetry', json=data)
        return response
