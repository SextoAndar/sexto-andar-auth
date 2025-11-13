"""
Tests for GET /auth/admin/users/{user_id}
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


def test_admin_can_get_any_user(client: TestClient, authenticated_admin: dict, created_user: dict):
    """Admin can fetch any user without relation check"""
    response = client.get(
        f"/api/auth/admin/users/{created_user['id']}",
        cookies=authenticated_admin["cookies"]
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_user["id"]
    assert data["username"] == created_user["username"]
    assert "password" not in data


@patch("app.controllers.auth_controller.check_user_property_relation", new_callable=AsyncMock)
def test_property_owner_can_get_own_user(mock_check, client: TestClient, test_property_owner_data: dict):
    """Property owner can fetch their own info without relation check"""
    # Register property owner
    reg = client.post("/api/auth/register/property-owner", json=test_property_owner_data)
    assert reg.status_code == 201
    owner = reg.json()

    # Login as owner
    login = client.post("/api/auth/login", json={"username": test_property_owner_data["username"], "password": test_property_owner_data["password"]})
    assert login.status_code == 200

    # Fetch own user (should not call relation check)
    response = client.get(f"/api/auth/admin/users/{owner['id']}", cookies=login.cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == owner["id"]
    assert data["username"] == owner["username"]
    
    # Should NOT have called the relation check (owner accessing own data)
    mock_check.assert_not_called()


@patch("app.controllers.auth_controller.check_user_property_relation", new_callable=AsyncMock)
def test_property_owner_can_get_user_with_relation(mock_check, client: TestClient, test_property_owner_data: dict, created_user: dict):
    """Property owner can fetch user who has relation (visits/proposals)"""
    # Mock: user HAS relation with owner's properties
    mock_check.return_value = True
    
    # Register property owner
    reg = client.post("/api/auth/register/property-owner", json=test_property_owner_data)
    assert reg.status_code == 201
    owner = reg.json()

    # Login as owner
    login = client.post("/api/auth/login", json={"username": test_property_owner_data["username"], "password": test_property_owner_data["password"]})
    assert login.status_code == 200

    # Fetch user with relation (visitor/proposer)
    response = client.get(f"/api/auth/admin/users/{created_user['id']}", cookies=login.cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_user["id"]
    assert data["username"] == created_user["username"]
    assert "password" not in data
    
    # Should have called the relation check
    mock_check.assert_called_once()


@patch("app.controllers.auth_controller.check_user_property_relation", new_callable=AsyncMock)
def test_property_owner_cannot_get_user_without_relation(mock_check, client: TestClient, test_property_owner_data: dict, created_user: dict):
    """Property owner CANNOT fetch user without relation - SECURITY TEST"""
    # Mock: user has NO relation with owner's properties
    mock_check.return_value = False
    
    # Register property owner
    reg = client.post("/api/auth/register/property-owner", json=test_property_owner_data)
    assert reg.status_code == 201
    owner = reg.json()

    # Login as owner
    login = client.post("/api/auth/login", json={"username": test_property_owner_data["username"], "password": test_property_owner_data["password"]})
    assert login.status_code == 200

    # Attempt to fetch unrelated user (should be blocked)
    response = client.get(f"/api/auth/admin/users/{created_user['id']}", cookies=login.cookies)
    assert response.status_code == 403
    assert "interacted with your properties" in response.json()["detail"]
    
    # Should have called the relation check
    mock_check.assert_called_once()


def test_regular_user_cannot_access_endpoint(client: TestClient, authenticated_user: dict, created_user: dict):
    """Regular users cannot access this endpoint"""
    response = client.get(f"/api/auth/admin/users/{created_user['id']}", cookies=authenticated_user["cookies"])
    assert response.status_code == 403


def test_unauthenticated_cannot_access(client: TestClient, created_user: dict):
    """Unauthenticated requests are rejected"""
    response = client.get(f"/api/auth/admin/users/{created_user['id']}")
    assert response.status_code == 401

