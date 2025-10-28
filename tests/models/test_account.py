"""
Tests for Account model
"""
import pytest
from app.models.account import Account, RoleEnum
from app.auth.password_handler import hash_password


class TestAccountModel:
    """Test Account model methods and properties"""
    
    def test_is_user(self, db_session):
        """Test is_user method"""
        account = Account(
            username="testuser",
            fullName="Test User",
            email="test@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        
        db_session.add(account)
        db_session.flush()
        
        assert account.is_user() is True
        
        account.role = RoleEnum.ADMIN
        assert account.is_user() is False
    
    def test_is_property_owner(self, db_session):
        """Test is_property_owner method"""
        account = Account(
            username="testowner",
            fullName="Test Owner",
            email="owner@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.PROPERTY_OWNER
        )
        
        db_session.add(account)
        db_session.flush()
        
        assert account.is_property_owner() is True
        
        account.role = RoleEnum.USER
        assert account.is_property_owner() is False
    
    def test_is_admin(self, db_session):
        """Test is_admin method"""
        account = Account(
            username="testadmin",
            fullName="Test Admin",
            email="admin@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.ADMIN
        )
        
        db_session.add(account)
        db_session.flush()
        
        assert account.is_admin() is True
        
        account.role = RoleEnum.USER
        assert account.is_admin() is False
    
    def test_account_creation(self, db_session):
        """Test creating an account with all fields"""
        account = Account(
            username="newuser",
            fullName="New User",
            email="new@example.com",
            phoneNumber="11988888888",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        
        db_session.add(account)
        db_session.commit()
        
        assert account.id is not None
        assert account.username == "newuser"
        assert account.email == "new@example.com"
        assert account.role == RoleEnum.USER
        assert account.created_at is not None
    
    def test_role_enum_values(self):
        """Test RoleEnum has correct values"""
        assert RoleEnum.USER.value == "USER"
        assert RoleEnum.PROPERTY_OWNER.value == "PROPERTY_OWNER"
        assert RoleEnum.ADMIN.value == "ADMIN"
    
    def test_account_repr(self, db_session):
        """Test account string representation"""
        account = Account(
            username="testuser",
            fullName="Test User",
            email="test@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        
        db_session.add(account)
        db_session.flush()
        
        repr_str = repr(account)
        assert "testuser" in repr_str or "Account" in repr_str
    
    def test_get_role_display(self, db_session):
        """Test get_role_display method"""
        account = Account(
            username="roleuser",
            fullName="Role User",
            email="role@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        
        db_session.add(account)
        db_session.flush()
        
        assert account.get_role_display() == "User"
        
        account.role = RoleEnum.PROPERTY_OWNER
        assert account.get_role_display() == "Property Owner"
        
        account.role = RoleEnum.ADMIN
        assert account.get_role_display() == "Administrator"
