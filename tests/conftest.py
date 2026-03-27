import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import DATABASE_URL, get_db, make_test_session_factory
from app.main import app

ADMIN_CREDS = {"username": "admin", "password": "admin"}


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    HTTP client with per-test NullPool DB session.
    NullPool creates a fresh connection per session — no shared pool across tests.
    """
    session_factory = make_test_session_factory(DATABASE_URL)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient) -> dict:
    resp = await client.post("/v1/admin/auth/login", json=ADMIN_CREDS)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def new_product(client: AsyncClient, auth_headers: dict) -> dict:
    """Creates a product before the test and deletes it after (best-effort)."""
    resp = await client.post(
        "/v1/admin/products",
        json={"name": "Fixture Product", "price_amount": "999.99", "stock": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    product = resp.json()
    yield product
    await client.delete(f"/v1/admin/products/{product['id']}", headers=auth_headers)


@pytest_asyncio.fixture(scope="function")
async def new_seller(client: AsyncClient, auth_headers: dict) -> dict:
    """Creates a seller before the test and leaves cleanup to cascade or manual teardown."""
    resp = await client.post(
        "/v1/admin/sellers",
        json={"name": "Fixture Seller", "rating": "4.5"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()
