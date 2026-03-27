"""Smoke tests for JWT authentication."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_login_success(client: AsyncClient):
    resp = await client.post(
        "/v1/admin/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


async def test_login_wrong_password(client: AsyncClient):
    resp = await client.post(
        "/v1/admin/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_wrong_username(client: AsyncClient):
    resp = await client.post(
        "/v1/admin/auth/login",
        json={"username": "hacker", "password": "admin"},
    )
    assert resp.status_code == 401


async def test_admin_no_token(client: AsyncClient):
    resp = await client.get("/v1/admin/products")
    # HTTPBearer returns 403 when Authorization header is absent
    assert resp.status_code == 403


async def test_admin_invalid_token(client: AsyncClient):
    resp = await client.get(
        "/v1/admin/products",
        headers={"Authorization": "Bearer this.is.not.a.valid.token"},
    )
    assert resp.status_code == 401


async def test_admin_malformed_header(client: AsyncClient):
    # Not a Bearer scheme
    resp = await client.get(
        "/v1/admin/products",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert resp.status_code == 403
