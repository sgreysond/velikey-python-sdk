"""Billing resource for VeliKey SDK."""

from typing import Dict, Any, Optional

from ..exceptions import NotFoundError

class BillingResource:
    """Manage billing and usage."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_usage(
        self,
        tenant: Optional[str] = None,
        month: Optional[str] = None,
        period: str = "current",
    ) -> Dict[str, Any]:
        """Get usage statistics."""
        params = {}
        if tenant:
            params["tenant"] = tenant
        if month:
            params["month"] = month
        if period:
            params["period"] = period

        response = await self._client._request("GET", "/api/usage/summary", params=params)
        return response
    
    async def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice details by ID from invoice listing endpoint."""
        response = await self._client._request("GET", "/api/invoices")
        if isinstance(response, list):
            invoices = response
        else:
            invoices = response.get("invoices", [])

        for invoice in invoices:
            if str(invoice.get("id")) == str(invoice_id):
                return invoice
        raise NotFoundError(f"Invoice not found: {invoice_id}", status_code=404)
