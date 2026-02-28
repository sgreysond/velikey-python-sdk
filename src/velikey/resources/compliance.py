"""Compliance resource for VeliKey SDK."""

from typing import Any, Dict, List

from ..models import ComplianceValidationResult

class ComplianceResource:
    """Manage compliance and audit functions."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_report(self, framework: str) -> Dict[str, Any]:
        """Get compliance report for a framework."""
        response = await self._client._request("GET", "/api/compliance-bundles")
        return response
    
    async def list_frameworks(self) -> List[str]:
        """List supported compliance frameworks."""
        response = await self._client._request("GET", "/api/compliance-bundles")
        frameworks = []
        for bundle in response.get("bundles", []):
            framework = bundle.get("framework")
            if isinstance(framework, str) and framework:
                frameworks.append(framework)
        return sorted(set(frameworks))

    async def validate_framework(self, framework: str) -> ComplianceValidationResult:
        """Validate that a compliance framework has an active bundle."""
        response = await self._client._request("GET", "/api/compliance-bundles")
        bundles = response.get("bundles", [])
        matching = [bundle for bundle in bundles if str(bundle.get("framework", "")).lower() == framework.lower()]
        compliant = any(bool(bundle.get("isActive", False)) for bundle in matching)
        issues: List[str] = []
        if not matching:
            issues.append(f"No compliance bundle found for framework '{framework}'")
        elif not compliant:
            issues.append(f"Framework '{framework}' has no active compliance bundle")

        score = 100 if compliant else 0
        return ComplianceValidationResult(
            framework=framework,
            compliant=compliant,
            score=score,
            issues=issues,
            evaluated_count=len(matching),
        )
