"""
Billing resource for VeliKey SDK
"""

from typing import Dict, Any, Optional

class BillingResource:
    """Manage billing and usage."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_usage(self, 
                       tenant: Optional[str] = None,
                       month: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics."""
        params = {}
        if tenant:
            params['tenant'] = tenant
        if month:
            params['month'] = month
            
        response = await self._client._request('GET', '/billing/usage', params=params)
        return response
    
    async def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice details."""
        response = await self._client._request('GET', f'/billing/invoices/{invoice_id}')
        return response
