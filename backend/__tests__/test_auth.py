from datetime import UTC

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth.utils import create_access_token
from app.main import app


@pytest.mark.asyncio
async def test_login_valid_credentials_returns_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "admin@condocombat.com", "senha": "123456"},
        )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "admin@condocombat.com", "senha": "wrong-password"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            json={"email": "unknown@test.com", "senha": "123456"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token_returns_user():
    token = create_access_token(data={"sub": "admin@condocombat.com"})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@condocombat.com"
    assert body["nome"] == "Admin"
    assert body["tipo"] == "sindico"


@pytest.mark.asyncio
async def test_me_without_token_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_expired_token_returns_401():
    from datetime import datetime, timedelta

    from jose import jwt

    from app.config import settings

    expired_payload = {
        "sub": "admin@condocombat.com",
        "exp": datetime.now(UTC) - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )
    assert response.status_code == 401
