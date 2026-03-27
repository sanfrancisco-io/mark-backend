"""Smoke tests for the admin API. Creates and tears down its own data."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ── Products ───────────────────────────────────────────────────────────────────

async def test_list_products(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/v1/admin/products", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "has_more" in body


async def test_create_product(client: AsyncClient, auth_headers: dict, new_product: dict):
    assert new_product["id"] > 0
    assert new_product["name"] == "Fixture Product"
    assert float(new_product["price_amount"]) == 999.99
    assert new_product["stock"] == 5


async def test_get_product(client: AsyncClient, auth_headers: dict, new_product: dict):
    resp = await client.get(f"/v1/admin/products/{new_product['id']}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == new_product["id"]
    assert "attributes" in body
    assert "offers" in body


async def test_update_product(client: AsyncClient, auth_headers: dict, new_product: dict):
    resp = await client.put(
        f"/v1/admin/products/{new_product['id']}",
        json={"name": "Updated Name", "stock": 42},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Updated Name"
    assert body["stock"] == 42
    # price_amount should be unchanged
    assert float(body["price_amount"]) == 999.99


async def test_delete_product(client: AsyncClient, auth_headers: dict):
    # Create a dedicated product for deletion (not using fixture — fixture also teardowns)
    create = await client.post(
        "/v1/admin/products",
        json={"name": "To Be Deleted", "price_amount": "1.00", "stock": 0},
        headers=auth_headers,
    )
    assert create.status_code == 201
    pid = create.json()["id"]

    delete = await client.delete(f"/v1/admin/products/{pid}", headers=auth_headers)
    assert delete.status_code == 204

    get = await client.get(f"/v1/admin/products/{pid}", headers=auth_headers)
    assert get.status_code == 404


async def test_get_product_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/v1/admin/products/999999", headers=auth_headers)
    assert resp.status_code == 404


# ── Sellers ────────────────────────────────────────────────────────────────────

async def test_list_sellers(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/v1/admin/sellers", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 10  # seed created 10 sellers


async def test_create_seller(client: AsyncClient, auth_headers: dict, new_seller: dict):
    assert new_seller["id"] > 0
    assert new_seller["name"] == "Fixture Seller"
    assert float(new_seller["rating"]) == 4.5


# ── Offers ─────────────────────────────────────────────────────────────────────

async def test_create_and_delete_offer(
    client: AsyncClient, auth_headers: dict, new_product: dict, new_seller: dict
):
    from datetime import date, timedelta

    delivery = (date.today() + timedelta(days=2)).isoformat()
    resp = await client.post(
        f"/v1/admin/products/{new_product['id']}/offers",
        json={
            "seller_id": new_seller["id"],
            "price_amount": "500.00",
            "price_currency": "RUB",
            "delivery_date": delivery,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    offer = resp.json()
    assert offer["id"] > 0
    assert float(offer["price_amount"]) == 500.00
    assert offer["seller"]["id"] == new_seller["id"]

    # Update
    update = await client.put(
        f"/v1/admin/offers/{offer['id']}",
        json={"price_amount": "450.00"},
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert float(update.json()["price_amount"]) == 450.00

    # Delete
    delete = await client.delete(f"/v1/admin/offers/{offer['id']}", headers=auth_headers)
    assert delete.status_code == 204


async def test_create_offer_seller_not_found(
    client: AsyncClient, auth_headers: dict, new_product: dict
):
    from datetime import date, timedelta

    resp = await client.post(
        f"/v1/admin/products/{new_product['id']}/offers",
        json={
            "seller_id": 999999,
            "price_amount": "100.00",
            "delivery_date": date.today().isoformat(),
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404
