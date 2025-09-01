"""
Rollout resource for VeliKey SDK
"""

from typing import Dict, Any, Optional

class RolloutsResource:
    """Manage policy rollouts."""
    
    def __init__(self, client):
        self._client = client
    
    async def plan(self, 
                   policy_id: str,
                   canary_percent: Optional[int] = None,
                   stabilization_window_s: Optional[int] = None,
                   dry_run: bool = True,
                   explain: bool = False) -> Dict[str, Any]:
        """Plan a policy rollout."""
        data = {'policy_id': policy_id}
        if canary_percent is not None:
            data['canary_percent'] = canary_percent
        if stabilization_window_s is not None:
            data['stabilization_window_s'] = stabilization_window_s
            
        params = {}
        if dry_run:
            params['dry_run'] = 'true'
        if explain:
            params['explain'] = 'true'
            
        response = await self._client._request(
            'POST', 
            '/ai/rollouts/plan',
            json=data,
            params=params
        )
        return response
    
    async def apply(self, 
                    plan_id: str,
                    idempotency_key: Optional[str] = None,
                    dry_run: bool = True,
                    explain: bool = False) -> Dict[str, Any]:
        """Apply a rollout plan."""
        data = {'plan_id': plan_id}
        if idempotency_key:
            data['idempotency_key'] = idempotency_key
            
        params = {}
        if dry_run:
            params['dry_run'] = 'true'
        if explain:
            params['explain'] = 'true'
            
        headers = {}
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
            
        response = await self._client._request(
            'POST', 
            '/ai/rollouts/apply',
            json=data,
            params=params,
            headers=headers
        )
        return response
    
    async def rollback(self, 
                       rollback_token: str,
                       explain: bool = False) -> Dict[str, Any]:
        """Trigger a rollback using a rollback token."""
        data = {'rollback_token': rollback_token}
        
        params = {}
        if explain:
            params['explain'] = 'true'
            
        response = await self._client._request(
            'POST', 
            '/ai/rollouts/rollback',
            json=data,
            params=params
        )
        return response
