"""Rollout resource for VeliKey SDK."""

from typing import Any, Dict, Optional

class RolloutsResource:
    """Manage policy rollouts."""
    
    def __init__(self, client):
        self._client = client
    
    async def plan(
        self,
        policy_id: str,
        canary_percent: Optional[int] = None,
        stabilization_window_s: Optional[int] = None,
        dry_run: bool = True,
        explain: bool = False,
    ) -> Dict[str, Any]:
        """Plan a policy rollout."""
        data = {"policyId": policy_id}
        if canary_percent is not None:
            data["canaryPercent"] = canary_percent
        if stabilization_window_s is not None:
            data["stabilizationWindowS"] = stabilization_window_s

        if dry_run:
            data["dryRun"] = True
        if explain:
            data["explain"] = True

        response = await self._client._request(
            "POST",
            "/api/rollouts/plan",
            json_data=data,
        )
        return response
    
    async def apply(
        self,
        plan_id: str,
        idempotency_key: Optional[str] = None,
        dry_run: bool = True,
        explain: bool = False,
    ) -> Dict[str, Any]:
        """Apply a rollout plan."""
        data = {"planId": plan_id}
        if idempotency_key:
            data["idempotencyKey"] = idempotency_key
        if dry_run:
            data["dryRun"] = True
        if explain:
            data["explain"] = True

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        response = await self._client._request(
            "POST",
            "/api/rollouts/apply",
            json_data=data,
            headers=headers
        )
        return response
    
    async def rollback(
        self,
        rollback_token: str,
        confirm: bool = True,
        explain: bool = False,
    ) -> Dict[str, Any]:
        """Trigger a rollback using a rollback token."""
        data = {"rollbackToken": rollback_token}
        if confirm:
            data["confirm"] = True
            data["confirmation"] = "ROLLBACK"
        if explain:
            data["explain"] = True

        response = await self._client._request(
            "POST",
            "/api/rollouts/rollback",
            json_data=data,
        )
        return response
