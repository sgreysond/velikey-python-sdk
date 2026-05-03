"""Gateway resource for VeliKey SDK (Phase 3.4)."""

from typing import Any, Dict, List, Literal, Optional, TypedDict

GatewayMode = Literal["INGRESS", "EGRESS", "BOTH"]
GatewayStatus = Literal[
    "PROVISIONING", "HEALTHY", "DEGRADED", "EXPIRED", "DECOMMISSIONED"
]
GatewayTemplate = Literal["SOC2", "PCI", "HIPAA", "GDPR", "CUSTOM"]
RotationTarget = Literal["cert", "key", "plugin-trust-anchor", "all"]


class Gateway(TypedDict, total=False):
    """Operator-visible gateway resource (matches /api/gateways response)."""

    id: str
    tenantId: str
    name: str
    mode: GatewayMode
    template: Optional[GatewayTemplate]
    status: GatewayStatus
    agentId: Optional[str]
    agentVersion: Optional[str]
    chartVersion: Optional[str]
    certExpiresAt: Optional[str]
    backendUrl: Optional[str]
    lastRolloutId: Optional[str]
    createdAt: str
    updatedAt: str


class InstallPlan(TypedDict):
    planId: str
    expiresAt: str
    bootstrapToken: str
    installScript: str
    gatewayId: str
    tenantId: str


class GatewaysResource:
    """Manage Aegis Gateway resources (Phase 3.4)."""

    def __init__(self, client):
        self._client = client

    async def install_plan(
        self,
        name: str,
        mode: GatewayMode,
        template: Optional[GatewayTemplate] = None,
        backend_url: Optional[str] = None,
        host_hint: Optional[str] = None,
    ) -> InstallPlan:
        """Mint a single-use install plan + bootstrap token + script.

        The bootstrap token expires in 15 minutes; treat it as a secret.
        """
        if not name or not name.strip():
            raise ValueError("name is required")
        data: Dict[str, Any] = {"name": name, "mode": mode}
        if template:
            data["template"] = template
        if backend_url:
            data["backendUrl"] = backend_url
        if host_hint:
            data["hostHint"] = host_hint
        return await self._client._request(
            "POST", "/api/gateway/install-plans", json_data=data
        )

    async def list(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        status: Optional[GatewayStatus] = None,
    ) -> Dict[str, Any]:
        """Paginated list of gateways for the caller's tenant."""
        params: Dict[str, str] = {}
        if limit:
            params["limit"] = str(limit)
        if cursor:
            params["cursor"] = cursor
        if status:
            params["status"] = status
        return await self._client._request(
            "GET", "/api/gateways", params=params
        )

    async def get(self, gateway_id: str) -> Gateway:
        """Fetch one gateway by id."""
        if not gateway_id or not gateway_id.strip():
            raise ValueError("gateway_id is required")
        return await self._client._request(
            "GET", f"/api/gateways/{gateway_id}"
        )

    async def rotate(
        self,
        gateway_id: str,
        target: RotationTarget = "cert",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rotate certs / keys / plugin trust anchors.

        Returns 202 Accepted with rotationId; reconcile happens on the
        next agent heartbeat (Phase 2 controller orchestrates the
        actual reload).
        """
        data: Dict[str, Any] = {"target": target, "confirm": "ROTATE"}
        if idempotency_key:
            data["idempotencyKey"] = idempotency_key
        return await self._client._request(
            "POST", f"/api/gateways/{gateway_id}/rotate", json_data=data
        )

    async def decommission(self, gateway_id: str) -> Gateway:
        """Decommission a gateway. Idempotent."""
        return await self._client._request(
            "DELETE",
            f"/api/gateways/{gateway_id}",
            params={"confirm": "DECOMMISSION"},
        )
