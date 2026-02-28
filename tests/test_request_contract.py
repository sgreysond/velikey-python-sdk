"""Contract tests for request/auth behavior."""

import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from velikey import AegisClient, AegisClientSync
from velikey.exceptions import NotFoundError, VeliKeyError


def _response(status_code: int, payload: dict) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=payload,
        request=httpx.Request("GET", "https://axis.velikey.com/api/test"),
        headers={"Retry-After": "0"},
    )


def test_session_cookie_normalization():
    client = AegisClient(api_key=None, session_cookie="raw-session-token")
    assert client._client.headers["Cookie"] == "next-auth.session-token=raw-session-token"
    asyncio.run(client.close())


def test_request_retries_retryable_status():
    client = AegisClient(api_key="test-key", base_url="https://axis.velikey.com", max_retries=1)
    client._client.request = AsyncMock(side_effect=[_response(503, {"error": "try again"}), _response(200, {"ok": True})])

    result = asyncio.run(client._request("GET", "/api/test"))
    assert result == {"ok": True}
    assert client._client.request.await_count == 2
    asyncio.run(client.close())


def test_sync_client_resource_proxy_executes_coroutines():
    client = AegisClientSync(api_key="test-key", base_url="https://axis.velikey.com")
    client._async_client.agents.list = AsyncMock(return_value=[{"id": "agent-1"}])

    result = client.agents.list()
    assert result == [{"id": "agent-1"}]

    client.close()


def test_quick_setup_returns_clear_unsupported_when_route_missing():
    client = AegisClient(api_key="test-key", base_url="https://axis.velikey.com")
    client._request = AsyncMock(side_effect=NotFoundError("missing", status_code=404))

    with pytest.raises(VeliKeyError) as error:
        asyncio.run(client.quick_setup())
    assert error.value.status_code == 501

    asyncio.run(client.close())


def test_get_invoice_reads_from_listing_endpoint():
    client = AegisClient(api_key="test-key", base_url="https://axis.velikey.com")

    async def fake_request(*args, **kwargs):
        return [
            {"id": "inv_1", "amount": 10},
            {"id": "inv_2", "amount": 20},
        ]

    client._request = fake_request

    invoice = asyncio.run(client.billing.get_invoice("inv_2"))
    assert invoice["amount"] == 20

    asyncio.run(client.close())
