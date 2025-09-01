"""
Compliance resource for VeliKey SDK
"""

from typing import Dict, Any, List

class ComplianceResource:
    """Manage compliance and audit functions."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_report(self, framework: str) -> Dict[str, Any]:
        """Get compliance report for a framework."""
        response = await self._client._request('GET', f'/compliance/reports/{framework}')
        return response
    
    async def list_frameworks(self) -> List[str]:
        """List supported compliance frameworks."""
        response = await self._client._request('GET', '/compliance/frameworks')
        return response.get('frameworks', [])
