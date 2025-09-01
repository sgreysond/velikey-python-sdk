"""
Diagnostics resource for VeliKey SDK
"""

from typing import Dict, Any

class DiagnosticsResource:
    """System diagnostics and troubleshooting."""
    
    def __init__(self, client):
        self._client = client
    
    async def run_check(self, check_type: str = 'full') -> Dict[str, Any]:
        """Run system diagnostics."""
        params = {'type': check_type}
        response = await self._client._request('GET', '/diagnostics/check', params=params)
        return response
    
    async def get_logs(self, agent_id: str, lines: int = 100) -> Dict[str, Any]:
        """Get agent logs."""
        params = {'lines': str(lines)}
        response = await self._client._request('GET', f'/agents/{agent_id}/logs', params=params)
        return response
