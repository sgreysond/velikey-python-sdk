"""Agent resource for VeliKey SDK."""

from typing import Any, Dict, List, Optional

from ..exceptions import VeliKeyError
from ..models import Agent

class AgentsResource:
    """Manage VeliKey agents."""
    
    def __init__(self, client):
        self._client = client
    
    async def list(
        self,
        tenant: Optional[str] = None,
        region: Optional[str] = None,
        status: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> List[Agent]:
        """List agents with optional filtering."""
        params = {}
        if tenant:
            params["tenant"] = tenant
        if region:
            params["region"] = region
        if status:
            params["status"] = status
        if agent_id:
            params["agentId"] = agent_id

        response = await self._client._request("GET", "/api/agents", params=params)
        return [Agent(**agent) for agent in response.get("agents", [])]
    
    async def get(self, agent_id: str) -> Agent:
        """Get a specific agent by ID."""
        response = await self._client._request("GET", "/api/agents", params={"agentId": agent_id})
        agents = response.get("agents", [])
        if not agents:
            raise ValueError(f"Agent not found: {agent_id}")
        return Agent(**agents[0])
    
    async def update_config(
        self,
        agent_id: str,
        config: Dict[str, Any],
        dry_run: bool = False,
        explain: bool = False,
    ) -> Dict[str, Any]:
        """Update agent configuration.

        Note:
            Axis currently exposes `/api/agents` read flows and connectivity checks.
            Direct mutable config update endpoint is not yet exposed.
        """
        raise VeliKeyError(
            (
                "Unsupported operation: agents.update_config. "
                "Axis does not currently expose PUT /api/agents/{id} in public routes."
            ),
            status_code=501,
        )
    
    async def restart(self, agent_id: str) -> Dict[str, Any]:
        """Restart an agent."""
        response = await self._client._request("POST", f"/api/agents/{agent_id}/test-connectivity")
        return response
