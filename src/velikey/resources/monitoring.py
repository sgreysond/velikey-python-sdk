"""Monitoring resource for VeliKey SDK."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..models import HealthScore, SecurityAlert, UsageMetrics


class MonitoringResource:
    """Access monitoring and metrics."""

    def __init__(self, client):
        self._client = client

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return await self._client._request("GET", "/api/usage")

    async def get_agent_health(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent health status."""
        if agent_id:
            return await self._client._request("GET", f"/api/agents/{agent_id}/health")
        return await self._client._request("GET", "/api/health")

    async def get_live_metrics(self) -> UsageMetrics:
        """Get live usage metrics from usage summary endpoint."""
        summary = await self._client._request("GET", "/api/usage/summary")
        usage = summary.get("usage", {})
        period = summary.get("period", {})
        now = datetime.now(timezone.utc)
        return UsageMetrics(
            agents_deployed=int(usage.get("agents", 0) or 0),
            policies_active=int(usage.get("environments", 0) or 0),
            connections_processed=int(usage.get("telemetryDays", 0) or 0),
            bytes_analyzed=int(float(usage.get("telemetryDataGB", 0.0) or 0.0) * (1024 ** 3)),
            uptime_percentage=100.0,
            period_start=period.get("start", now),
            period_end=period.get("end", now),
        )

    async def get_health_score(self) -> HealthScore:
        """Derive health score from usage + active alerts."""
        summary = await self._client._request("GET", "/api/usage/summary")
        alerts_response = await self._client._request(
            "GET",
            "/api/alerts",
            params={"resolved": "false", "limit": "200"},
        )

        usage = summary.get("usage", {})
        alerts = alerts_response.get("alerts", [])
        critical_alerts = [
            alert
            for alert in alerts
            if str(alert.get("severity", "")).lower() in {"critical", "emergency"}
        ]

        telemetry_days = int(usage.get("telemetryDays", 0) or 0)
        agents = int(usage.get("agents", 0) or 0)
        score = 100
        if agents == 0:
            score -= 30
        if telemetry_days == 0:
            score -= 25
        score -= min(45, len(critical_alerts) * 15)
        score = max(0, min(100, score))

        recommendations: List[str] = []
        if agents == 0:
            recommendations.append("Enroll at least one active agent")
        if telemetry_days == 0:
            recommendations.append("Send telemetry traffic to validate metering")
        if critical_alerts:
            recommendations.append("Resolve critical alerts before rollout promotion")

        return HealthScore(
            overall_score=score,
            category_scores={
                "agents": 100 if agents > 0 else 40,
                "telemetry": 100 if telemetry_days > 0 else 40,
                "alerts": max(0, 100 - (len(critical_alerts) * 20)),
            },
            risk_factors=[f"{len(critical_alerts)} critical/emergency alerts"] if critical_alerts else [],
            recommendations=recommendations,
            trend="stable" if not critical_alerts else "warning",
            calculated_at=datetime.now(timezone.utc),
        )

    async def get_active_alerts(self, limit: int = 50) -> List[SecurityAlert]:
        """Return active alerts for the current tenant."""
        response = await self._client._request(
            "GET",
            "/api/alerts",
            params={"resolved": "false", "limit": str(limit)},
        )
        return [SecurityAlert(**alert) for alert in response.get("alerts", [])]
