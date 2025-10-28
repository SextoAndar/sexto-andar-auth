"""
Tests for admin-only endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestAdminCreateEndpoint:
    """Test admin creation endpoint (admin-only)"""
    
    def test_create_admin_as_admin(self, client: TestClient, authenticated_admin: dict):
        """Test admin can create another admin"""
        new_admin_data = {
            "username": "newadmin",
            "fullName": "New Admin",
            "email": "newadmin@example.com",
            "password": "newadminpass123",
            "phoneNumber": "11966666666"
        }
        
        response = client.post(
            "/api/auth/admin/create-admin",
            json=new_admin_data,
            cookies=authenticated_admin["cookies"]
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["username"] == new_admin_data["username"]
        assert data["role"] == "ADMIN"
        assert "password" not in data
    
    def test_create_admin_as_regular_user(self, client: TestClient, authenticated_user: dict):
        """Test regular user cannot create admin"""
        new_admin_data = {
            "username": "newadmin",
            "fullName": "New Admin",
            "email": "newadmin@example.com",
            "password": "newadminpass123",
            "phoneNumber": "11966666666"
        }
        
        response = client.post(
            "/api/auth/admin/create-admin",
            json=new_admin_data,
            cookies=authenticated_user["cookies"]
        )
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_create_admin_unauthenticated(self, client: TestClient):
        """Test unauthenticated user cannot create admin"""
        new_admin_data = {
            "username": "newadmin",
            "fullName": "New Admin",
            "email": "newadmin@example.com",
            "password": "newadminpass123",
            "phoneNumber": "11966666666"
        }
        
        response = client.post(
            "/api/auth/admin/create-admin",
            json=new_admin_data
        )
        
        assert response.status_code == 401
    
    def test_create_admin_duplicate_username(self, client: TestClient, authenticated_admin: dict):
        """Test cannot create admin with duplicate username"""
        admin_data = {
            "username": authenticated_admin["admin"]["username"],
            "fullName": "Duplicate Admin",
            "email": "duplicate@example.com",
            "password": "duplicatepass123",
            "phoneNumber": "11955555555"
        }
        
        response = client.post(
            "/api/auth/admin/create-admin",
            json=admin_data,
            cookies=authenticated_admin["cookies"]
        )
        
        assert response.status_code == 400


class TestAdminDeleteEndpoint:
    """Test admin deletion endpoint (admin-only)"""
    
    def test_delete_admin_as_admin(self, client: TestClient, authenticated_admin: dict):
        """Test admin can delete another admin"""
        # First create another admin
        new_admin_data = {
            "username": "adminToDelete",
            "fullName": "Admin To Delete",
            "email": "deleteme@example.com",
            "password": "deletepass123",
            "phoneNumber": "11944444444"
        }
        
        create_response = client.post(
            "/api/auth/admin/create-admin",
            json=new_admin_data,
            cookies=authenticated_admin["cookies"]
        )
        assert create_response.status_code == 201
        admin_to_delete_id = create_response.json()["id"]
        
        # Now delete it
        delete_response = client.delete(
            f"/api/auth/admin/delete-admin/{admin_to_delete_id}",
            cookies=authenticated_admin["cookies"]
        )
        
        assert delete_response.status_code == 204
    
    def test_delete_admin_self_deletion_fails(self, client: TestClient, authenticated_admin: dict):
        """Test admin cannot delete themselves"""
        response = client.delete(
            f"/api/auth/admin/delete-admin/{authenticated_admin['admin']['id']}",
            cookies=authenticated_admin["cookies"]
        )
        
        assert response.status_code == 400
        assert "Cannot delete your own admin account" in response.json()["detail"]
    
    def test_delete_admin_as_regular_user(self, client: TestClient, authenticated_user: dict, created_admin: dict):
        """Test regular user cannot delete admin"""
        response = client.delete(
            f"/api/auth/admin/delete-admin/{created_admin['id']}",
            cookies=authenticated_user["cookies"]
        )
        
        assert response.status_code == 403
    
    def test_delete_admin_unauthenticated(self, client: TestClient, created_admin: dict):
        """Test unauthenticated user cannot delete admin"""
        response = client.delete(
            f"/api/auth/admin/delete-admin/{created_admin['id']}"
        )
        
        assert response.status_code == 401
    
    def test_delete_nonexistent_admin(self, client: TestClient, authenticated_admin: dict):
        """Test deleting nonexistent admin fails"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.delete(
            f"/api/auth/admin/delete-admin/{fake_id}",
            cookies=authenticated_admin["cookies"]
        )
        
        assert response.status_code == 404
        assert "Admin account not found" in response.json()["detail"]
    
    def test_delete_non_admin_user_fails(self, client: TestClient, authenticated_admin: dict, created_user: dict):
        """Test cannot delete non-admin using admin delete endpoint"""
        response = client.delete(
            f"/api/auth/admin/delete-admin/{created_user['id']}",
            cookies=authenticated_admin["cookies"]
        )
        
        assert response.status_code == 400
        assert "not an admin" in response.json()["detail"].lower()


class TestAdminAuthorization:
    """Test that admin endpoints properly check authorization"""
    
    def test_admin_endpoints_require_admin_role(self, client: TestClient, authenticated_user: dict):
        """Test all admin endpoints reject non-admin users"""
        # Test create admin
        response = client.post(
            "/api/auth/admin/create-admin",
            json={
                "username": "test",
                "fullName": "Test",
                "email": "test@example.com",
                "password": "test123456",
                "phoneNumber": "11999999999"
            },
            cookies=authenticated_user["cookies"]
        )
        assert response.status_code == 403
        
        # Test delete admin
        response = client.delete(
            "/api/auth/admin/delete-admin/fake-id",
            cookies=authenticated_user["cookies"]
        )
        assert response.status_code == 403
