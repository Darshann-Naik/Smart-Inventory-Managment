# /apps/user_service/tests/test_auth.py
import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app # Import the main app instance

pytestmark = pytest.mark.asyncio

async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "store_name": "Test Store"
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["data"]["email"] == "testuser@example.com"
    assert "id" in data["data"]

async def test_register_duplicate_user(client: AsyncClient):
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "store_name": "Test Store"
        },
    )
    # Second attempt
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "anotherpassword",
            "first_name": "Another",
            "last_name": "User",
            "store_name": "Another Store"
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    error_data = response.json()
    assert "A user with this email already exists" in error_data["errors"][0]["detail"]

async def test_login_for_access_token(client: AsyncClient):
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "loginpassword",
            "first_name": "Login",
            "last_name": "User",
            "store_name": "Login Store"
        },
    )
    # Attempt login
    login_response = await client.post(
        "/api/v1/auth/token",
        data={"username": "loginuser@example.com", "password": "loginpassword"},
    )
    assert login_response.status_code == status.HTTP_200_OK
    token_data = login_response.json()["data"]
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

async def test_login_wrong_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "wronguser@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED