"""
Agent resource for VeliKey SDK
"""

from typing import List, Optional, Dict, Any
from ..models import Agent

class AgentsResource:
    """Manage VeliKey agents."""
    
    def __init__(self, client):
        self._client = client
    
    async def list(self, 
                   tenant: Optional[str] = None,
                   region: Optional[str] = None,
                   status: Optional[str] = None) -> List[Agent]:
        """List agents with optional filtering."""
        params = {}
        if tenant:
            params['tenant'] = tenant
        if region:
            params['region'] = region
        if status:
            params['status'] = status
            
        response = await self._client._request('GET', '/agents', params=params)
        return [Agent(**agent) for agent in response.get('agents', [])]
    
    async def get(self, agent_id: str) -> Agent:
        """Get a specific agent by ID."""
        response = await self._client._request('GET', f'/agents/{agent_id}')
        return Agent(**response)
    
    async def update_config(self, 
                           agent_id: str, 
                           config: Dict[str, Any],
                           dry_run: bool = False,
                           explain: bool = False) -> Dict[str, Any]:
        """Update agent configuration."""
        params = {}
        if dry_run:
            params['dry_run'] = 'true'
        if explain:
            params['explain'] = 'true'
            
        response = await self._client._request(
            'PUT', 
            f'/agents/{agent_id}/config',
            json=config,
            params=params
        )
        return response
    
    async def restart(self, agent_id: str) -> Dict[str, Any]:
        """Restart an agent."""
        response = await self._client._request('POST', f'/agents/{agent_id}/restart')
        return response
