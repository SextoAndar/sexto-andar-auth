"""
Tests for user profile update endpoint
"""
import pytest
from fastapi.testclient import TestClient


class TestUpdateProfile:
    """Test updating user profile (US04, US17)"""
    
    def test_update_full_name(self, client: TestClient, authenticated_user: dict):
        """Test user can update their full name"""
        update_data = {"fullName": "New Full Name"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == update_data["fullName"]
        assert data["id"] == authenticated_user["user"]["id"]
    
    def test_update_phone_number(self, client: TestClient, authenticated_user: dict):
        """Test user can update their phone number"""
        update_data = {"phoneNumber": "11911112222"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["phoneNumber"] == update_data["phoneNumber"]
    
    def test_update_email_with_correct_password(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test user can update their email with correct password"""
        update_data = {
            "email": "newemail@example.com",
            "currentPassword": test_user_data["password"]
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == update_data["email"]
    
    def test_update_email_without_password(self, client: TestClient, authenticated_user: dict):
        """Test user cannot update email without current password"""
        update_data = {"email": "another@example.com"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "Current password is required" in response.json()["detail"]
    
    def test_update_email_with_wrong_password(self, client: TestClient, authenticated_user: dict):
        """Test user cannot update email with wrong current password"""
        update_data = {
            "email": "wrongpass@example.com",
            "currentPassword": "wrongpassword"
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_update_email_already_exists(self, client: TestClient, authenticated_user: dict, test_property_owner_data: dict, test_user_data: dict):
        """Test user cannot update email to one that already exists"""
        # Create a second user to have a duplicate email
        client.post("/api/auth/register/property-owner", json=test_property_owner_data)
        
        update_data = {
            "email": test_property_owner_data["email"],
            "currentPassword": test_user_data["password"]
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]
    
    def test_update_password_with_correct_current_password(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test user can update their password with correct current password"""
        update_data = {
            "newPassword": "newsecurepassword123",
            "currentPassword": test_user_data["password"]
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["user"]["username"]  # Ensure other fields are unchanged
        
        # Verify new password by logging in again
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": authenticated_user["user"]["username"],
                "password": update_data["newPassword"]
            }
        )
        assert login_response.status_code == 200
    
    def test_update_password_without_current_password(self, client: TestClient, authenticated_user: dict):
        """Test user cannot update password without current password"""
        update_data = {"newPassword": "newsecurepassword123"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "Current password is required" in response.json()["detail"]
    
    def test_update_password_with_wrong_current_password(self, client: TestClient, authenticated_user: dict):
        """Test user cannot update password with wrong current password"""
        update_data = {
            "newPassword": "newsecurepassword123",
            "currentPassword": "wrongpassword"
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_update_multiple_fields(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test user can update multiple fields at once"""
        update_data = {
            "fullName": "Updated Name",
            "phoneNumber": "11933334444",
            "email": "multiupdate@example.com",
            "newPassword": "supernewpassword",
            "currentPassword": test_user_data["password"]
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == update_data["fullName"]
        assert data["phoneNumber"] == update_data["phoneNumber"]
        assert data["email"] == update_data["email"]
        
        # Verify new password
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": authenticated_user["user"]["username"],
                "password": update_data["newPassword"]
            }
        )
        assert login_response.status_code == 200
    
    def test_update_no_fields(self, client: TestClient, authenticated_user: dict):
        """Test updating with no fields provided returns bad request"""
        update_data = {}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        assert "No fields to update" in response.json()["detail"]
    
    def test_property_owner_can_update_profile(self, client: TestClient, authenticated_property_owner: dict):
        """Test property owner can update their profile"""
        update_data = {"fullName": "New Owner Name"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_property_owner["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == update_data["fullName"]
        assert data["id"] == authenticated_property_owner["user"]["id"]
    
    def test_admin_can_update_profile(self, client: TestClient, authenticated_admin: dict):
        """Test admin can update their own profile"""
        update_data = {"fullName": "New Admin Name"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_admin["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == update_data["fullName"]
        assert data["id"] == authenticated_admin["admin"]["id"]
    
    @pytest.mark.parametrize("invalid_email", ["invalid", "user@.com", "user@com."])
    def test_update_invalid_email_format(self, client: TestClient, authenticated_user: dict, invalid_email: str, test_user_data: dict):
        """Test updating with an invalid email format fails"""
        update_data = {
            "email": invalid_email,
            "currentPassword": test_user_data["password"]
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 422  # Pydantic validation error
    
    def test_update_short_password(self, client: TestClient, authenticated_user: dict, test_user_data: dict):
        """Test updating with a password shorter than 8 characters fails"""
        update_data = {
            "newPassword": "short",
            "currentPassword": test_user_data["password"]
        }
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 422  # Pydantic validation error
    
    def test_update_short_full_name(self, client: TestClient, authenticated_user: dict):
        """Test updating with a full name shorter than 3 characters fails"""
        update_data = {"fullName": "a"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 422  # Pydantic validation error
    
    def test_update_short_phone_number(self, client: TestClient, authenticated_user: dict):
        """Test updating with a phone number shorter than 10 characters fails"""
        update_data = {"phoneNumber": "123456789"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 422  # Pydantic validation error