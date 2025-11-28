from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, AsyncMock


class TestGetUserById:
    """Tests for the /admin/users/{user_id} endpoint (US24, US31, US32)"""
    
    def test_admin_can_get_any_user(self, client: TestClient, authenticated_admin: dict, created_user: dict):
        """Admin should be able to retrieve any user's information"""
        user_id = created_user["id"]
        response = client.get(
            f"/api/auth/admin/users/{user_id}",
            headers=authenticated_admin["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == created_user["email"]
    
    def test_property_owner_can_get_own_user(self, client: TestClient, authenticated_property_owner: dict):
        """Property owner should be able to retrieve their own information"""
        owner_id = authenticated_property_owner["user"]["id"]
        response = client.get(
            f"/api/auth/admin/users/{owner_id}",
            headers=authenticated_property_owner["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == owner_id
        assert data["email"] == authenticated_property_owner["user"]["email"]
    
    @patch("app.controllers.auth_controller.check_user_property_relation", new_callable=AsyncMock)
    def test_property_owner_can_get_user_with_relation(self, mock_check_relation: AsyncMock, client: TestClient, authenticated_property_owner: dict, created_user: dict):
        """Property owner should be able to retrieve information of users related to their properties"""
        mock_check_relation.return_value = True  # Simulate a successful relation check
        
        user_id = created_user["id"]
        response = client.get(
            f"/api/auth/admin/users/{user_id}",
            headers=authenticated_property_owner["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        
        mock_check_relation.assert_called_once_with(
            user_id=user_id,
            owner_id=authenticated_property_owner["user"]["id"]
        )
    
    @patch("app.controllers.auth_controller.check_user_property_relation", new_callable=AsyncMock)
    def test_property_owner_cannot_get_user_without_relation(self, mock_check_relation: AsyncMock, client: TestClient, authenticated_property_owner: dict, created_user: dict):
        """Property owner should not be able to retrieve information of users not related to their properties"""
        mock_check_relation.return_value = False  # Simulate a failed relation check
        
        user_id = created_user["id"]
        response = client.get(
            f"/api/auth/admin/users/{user_id}",
            headers=authenticated_property_owner["headers"]
        )
        assert response.status_code == 403
        assert "You can only access information of users who interacted with your properties" in response.json()["detail"]
        
        mock_check_relation.assert_called_once_with(
            user_id=user_id,
            owner_id=authenticated_property_owner["user"]["id"]
        )
    
    def test_regular_user_cannot_access_endpoint(self, client: TestClient, authenticated_user: dict, created_admin: dict):
        """Regular users should not be able to access the admin user retrieval endpoint"""
        admin_id = created_admin["id"]
        response = client.get(
            f"/api/auth/admin/users/{admin_id}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_unauthenticated_user_cannot_access_endpoint(self, client: TestClient, created_user: dict):
        """Unauthenticated users should not be able to access the admin user retrieval endpoint"""
        user_id = created_user["id"]
        response = client.get(f"/api/auth/admin/users/{user_id}")
        assert response.status_code == 403