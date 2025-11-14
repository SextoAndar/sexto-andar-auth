"""
Tests for profile update endpoint (US04 and US17)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestUpdateProfile:
    """Test PUT /auth/profile endpoint"""
    
    def test_update_full_name(self, client: TestClient, authenticated_user: dict):
        """Test updating only full name"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={"fullName": "Updated Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == "Updated Name"
        assert data["id"] == authenticated_user["user"]["id"]
    
    def test_update_phone_number(self, client: TestClient, authenticated_user: dict):
        """Test updating only phone number"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={"phoneNumber": "+5511988887777"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == authenticated_user["user"]["id"]
    
    def test_update_email_with_correct_password(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test updating email with correct current password"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "email": "newemail@example.com",
                "currentPassword": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
    
    def test_update_email_without_password(self, client: TestClient, authenticated_user: dict):
        """Test updating email without current password fails"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == 400
        assert "Current password is required" in response.json()["detail"]
    
    def test_update_email_with_wrong_password(self, client: TestClient, authenticated_user: dict):
        """Test updating email with wrong current password fails"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "email": "newemail@example.com",
                "currentPassword": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_update_email_already_exists(self, client: TestClient, authenticated_user: dict, authenticated_property_owner: dict, test_user_data: dict):
        """Test updating to an email that already exists"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "email": authenticated_property_owner["user"]["email"],
                "currentPassword": test_user_data["password"]
            }
        )
        
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]
    
    def test_update_password_with_correct_current_password(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test updating password with correct current password"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "currentPassword": test_user_data["password"],
                "newPassword": "NewPassword123!"
            }
        )
        
        assert response.status_code == 200
        
        # Verify can login with new password
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_data["username"],
                "password": "NewPassword123!"
            }
        )
        assert login_response.status_code == 200
    
    def test_update_password_without_current_password(self, client: TestClient, authenticated_user: dict):
        """Test updating password without current password fails"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={"newPassword": "NewPassword123!"}
        )
        
        assert response.status_code == 400
        assert "Current password is required" in response.json()["detail"]
    
    def test_update_password_with_wrong_current_password(self, client: TestClient, authenticated_user: dict):
        """Test updating password with wrong current password fails"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "currentPassword": "WrongPassword123!",
                "newPassword": "NewPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_update_multiple_fields(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test updating multiple fields at once"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "fullName": "Complete New Name",
                "phoneNumber": "+5511977776666",
                "email": "completelynew@example.com",
                "currentPassword": test_user_data["password"],
                "newPassword": "CompletelyNew123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == "Complete New Name"
        assert data["email"] == "completelynew@example.com"
    
    def test_update_no_fields(self, client: TestClient, authenticated_user: dict):
        """Test updating with no fields fails"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={}
        )
        
        assert response.status_code == 400
        assert "No fields to update" in response.json()["detail"]
    
    def test_update_unauthenticated(self, client: TestClient):
        """Test updating profile without authentication fails"""
        response = client.put(
            "/api/auth/profile",
            json={"fullName": "New Name"}
        )
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_property_owner_can_update_profile(self, client: TestClient, authenticated_property_owner: dict):
        """Test that property owners can update their profile (US17)"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_property_owner["cookies"],
            json={"fullName": "Updated Owner Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == "Updated Owner Name"
        assert data["role"] == "PROPERTY_OWNER"
    
    def test_admin_can_update_profile(self, client: TestClient, authenticated_admin: dict):
        """Test that admins can update their profile"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_admin["cookies"],
            json={"fullName": "Updated Admin Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == "Updated Admin Name"
        assert data["role"] == "ADMIN"
    
    def test_update_invalid_email_format(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test updating with invalid email format"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "email": "invalid-email",
                "currentPassword": test_user_data["password"]
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_update_short_password(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test updating with password less than 8 characters"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={
                "currentPassword": test_user_data["password"],
                "newPassword": "short"
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_update_short_full_name(self, client: TestClient, authenticated_user: dict):
        """Test updating with full name less than 2 characters"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={"fullName": "A"}
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_update_short_phone_number(self, client: TestClient, authenticated_user: dict):
        """Test updating with phone number less than 10 characters"""
        response = client.put(
            "/api/auth/profile",
            cookies=authenticated_user["cookies"],
            json={"phoneNumber": "123"}
        )
        
        assert response.status_code == 422  # Pydantic validation error


class TestUpdateProfileAuthentication:
    """Test authentication requirements for profile updates"""
    
    def test_update_requires_authentication(self, client: TestClient):
        """Test that profile update requires authentication"""
        response = client.put(
            "/api/auth/profile",
            json={"fullName": "New Name"}
        )
        
        assert response.status_code == 401
    
    def test_update_with_invalid_token(self, client: TestClient):
        """Test that profile update with invalid token fails"""
        response = client.put(
            "/api/auth/profile",
            cookies={"access_token": "invalid_token"},
            json={"fullName": "New Name"}
        )
        
        assert response.status_code == 401
