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


class TestAccountValidationParametrized:
    """Parametrized tests for Account model validation"""
    
    @pytest.mark.parametrize("username,should_fail", [
        ("ab", True),  # Too short (< 3)
        ("abc", False),  # Minimum valid
        ("user123", False),  # Valid
        ("a" * 50, False),  # Maximum valid
        ("a" * 51, True),  # Too long (> 50)
        ("user_name", False),  # Valid with underscore
        ("user-name", True),  # Invalid with dash
        ("user name", True),  # Invalid with space
        ("user@name", True),  # Invalid with special char
        ("123user", False),  # Valid with numbers
        ("_user", False),  # Valid starting with underscore
        ("", True),  # Empty
    ])
    def test_username_validation(self, db_session, username, should_fail):
        """Test username validation with various inputs"""
        if should_fail:
            with pytest.raises(ValueError):
                account = Account(
                    username=username,
                    fullName="Test User",
                    email="test@example.com",
                    phoneNumber="11999999999",
                    password=hash_password("password123"),
                    role=RoleEnum.USER
                )
                db_session.add(account)
                db_session.flush()
        else:
            account = Account(
                username=username,
                fullName="Test User",
                email="test@example.com",
                phoneNumber="11999999999",
                password=hash_password("password123"),
                role=RoleEnum.USER
            )
            db_session.add(account)
            db_session.flush()
            assert account.username == username.lower()  # Should be lowercased
    
    @pytest.mark.parametrize("phone,should_fail", [
        ("11999999999", False),  # Valid Brazilian mobile
        ("1199999999", False),  # Valid 10 digits
        ("119999999999", False),  # Valid 12 digits
        ("11 99999-9999", False),  # Valid with formatting
        ("(11) 99999-9999", False),  # Valid with formatting
        ("123456789", True),  # Too short (< 10)
        ("1234567890123456", True),  # Too long (> 15)
        (None, False),  # None is allowed (nullable)
    ])
    def test_phone_validation(self, db_session, phone, should_fail):
        """Test phone number validation with various inputs"""
        if should_fail:
            with pytest.raises(ValueError):
                account = Account(
                    username="testuser",
                    fullName="Test User",
                    email="test@example.com",
                    phoneNumber=phone,
                    password=hash_password("password123"),
                    role=RoleEnum.USER
                )
                db_session.add(account)
                db_session.flush()
        else:
            account = Account(
                username="testuser",
                fullName="Test User",
                email="test@example.com",
                phoneNumber=phone,
                password=hash_password("password123"),
                role=RoleEnum.USER
            )
            db_session.add(account)
            db_session.flush()
            assert account.phoneNumber == phone
    
    @pytest.mark.parametrize("password,should_fail", [
        ("pass123", True),  # Too short (< 8)
        ("password", False),  # Minimum valid
        ("P@ssw0rd!123", False),  # Strong password
        ("a" * 100, False),  # Long password
        ("12345678", False),  # Valid 8 chars
        ("   ", True),  # Just spaces (< 8 after strip)
    ])
    def test_password_length_validation(self, db_session, password, should_fail):
        """Test password length validation"""
        if should_fail:
            with pytest.raises(ValueError, match="Password must have at least 8 characters"):
                account = Account(
                    username="testuser",
                    fullName="Test User",
                    email="test@example.com",
                    phoneNumber="11999999999",
                    password=password,
                    role=RoleEnum.USER
                )
                db_session.add(account)
                db_session.flush()
        else:
            # For valid passwords, use hash_password
            account = Account(
                username="testuser",
                fullName="Test User",
                email="test@example.com",
                phoneNumber="11999999999",
                password=hash_password(password),
                role=RoleEnum.USER
            )
            db_session.add(account)
            db_session.flush()
            assert account.password is not None
    
    @pytest.mark.parametrize("role,method,expected", [
        (RoleEnum.USER, "is_user", True),
        (RoleEnum.USER, "is_property_owner", False),
        (RoleEnum.USER, "is_admin", False),
        (RoleEnum.PROPERTY_OWNER, "is_user", False),
        (RoleEnum.PROPERTY_OWNER, "is_property_owner", True),
        (RoleEnum.PROPERTY_OWNER, "is_admin", False),
        (RoleEnum.ADMIN, "is_user", False),
        (RoleEnum.ADMIN, "is_property_owner", False),
        (RoleEnum.ADMIN, "is_admin", True),
    ])
    def test_role_check_methods(self, db_session, role, method, expected):
        """Test role checking methods for all role types"""
        account = Account(
            username="roletest",
            fullName="Role Test",
            email="role@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=role
        )
        
        db_session.add(account)
        db_session.flush()
        
        # Call the method dynamically
        result = getattr(account, method)()
        assert result == expected
