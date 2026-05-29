import httpx
import pytest


@pytest.mark.anyio
async def test_login_sets_http_only_cookie(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert "access_token=" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]


@pytest.mark.anyio
async def test_current_user_requires_authentication(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_current_user_returns_authenticated_user(
    authenticated_client: httpx.AsyncClient,
) -> None:
    response = await authenticated_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["role"] == "admin"
