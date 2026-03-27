"""Smoke tests for the public API. Reads seed data — requires seed to be applied."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_list_products_ok(client: AsyncClient):
    resp = await client.get("/v1/public/products")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "has_more" in body
    assert isinstance(body["items"], list)
    assert len(body["items"]) > 0


async def test_list_products_pagination(client: AsyncClient):
    resp = await client.get("/v1/public/products", params={"limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) <= 5


async def test_list_products_has_more_true(client: AsyncClient):
    # Seed has 120 products; default limit=20 → has_more must be True
    resp = await client.get("/v1/public/products")
    assert resp.status_code == 200
    assert resp.json()["has_more"] is True


async def test_list_products_last_page(client: AsyncClient):
    # offset beyond all products → empty items, has_more False
    resp = await client.get("/v1/public/products", params={"offset": 10000, "limit": 20})
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["has_more"] is False


async def test_get_product_ok(client: AsyncClient):
    resp = await client.get("/v1/public/products/1")
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert "attributes" in body
    assert "offers" in body
    assert isinstance(body["attributes"], list)
    assert isinstance(body["offers"], list)


async def test_get_product_has_thumbnail_url(client: AsyncClient):
    resp = await client.get("/v1/public/products/1")
    assert resp.status_code == 200
    assert resp.json()["thumbnail_url"] is not None


async def test_get_product_offers_sorted_by_price(client: AsyncClient):
    resp = await client.get("/v1/public/products/1")
    assert resp.status_code == 200
    offers = resp.json()["offers"]
    if len(offers) >= 2:
        prices = [float(o["price_amount"]) for o in offers]
        assert prices == sorted(prices)


async def test_get_product_offers_sorted_by_delivery(client: AsyncClient):
    resp = await client.get("/v1/public/products/1", params={"offers_sort": "delivery_date"})
    assert resp.status_code == 200
    offers = resp.json()["offers"]
    if len(offers) >= 2:
        dates = [o["delivery_date"] for o in offers]
        assert dates == sorted(dates)


async def test_get_product_not_found(client: AsyncClient):
    resp = await client.get("/v1/public/products/999999")
    assert resp.status_code == 404


async def test_get_product_invalid_offers_sort(client: AsyncClient):
    resp = await client.get("/v1/public/products/1", params={"offers_sort": "invalid"})
    assert resp.status_code == 422
