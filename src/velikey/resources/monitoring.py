"""
Monitoring resource for VeliKey SDK
"""

from typing import Dict, Any, Optional

class MonitoringResource:
    """Access monitoring and metrics."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        response = await self._client._request('GET', '/monitoring/dashboard')
        return response
    
    async def get_agent_health(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent health status."""
        params = {}
        if agent_id:
            params['agent_id'] = agent_id
            
        response = await self._client._request('GET', '/monitoring/health', params=params)
        return response
