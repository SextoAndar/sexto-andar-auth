"""
Tests for Account repository
"""
import pytest
from app.repositories.account_repository import AccountRepository
from app.models.account import Account, RoleEnum
from app.auth.password_handler import hash_password


class TestAccountRepository:
    """Test AccountRepository methods"""
    
    def test_create_account(self, db_session):
        """Test creating an account"""
        repo = AccountRepository(db_session)
        
        account = Account(
            username="newuser",
            fullName="New User",
            email="new@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        
        created = repo.create(account)
        
        assert created.id is not None
        assert created.username == "newuser"
        assert created.email == "new@example.com"
    
    def test_get_by_id(self, db_session, created_user):
        """Test getting account by ID"""
        repo = AccountRepository(db_session)
        
        account = repo.get_by_id(created_user["id"])
        
        assert account is not None
        assert str(account.id) == created_user["id"]
        assert account.username == created_user["username"]
    
    def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent account by ID"""
        repo = AccountRepository(db_session)
        
        account = repo.get_by_id("00000000-0000-0000-0000-000000000000")
        
        assert account is None
    
    def test_get_by_username(self, db_session, created_user):
        """Test getting account by username"""
        repo = AccountRepository(db_session)
        
        account = repo.get_by_username(created_user["username"])
        
        assert account is not None
        assert account.username == created_user["username"]
    
    def test_get_by_username_not_found(self, db_session):
        """Test getting non-existent account by username"""
        repo = AccountRepository(db_session)
        
        account = repo.get_by_username("nonexistent_user")
        
        assert account is None
    
    def test_get_by_email(self, db_session, created_user):
        """Test getting account by email"""
        repo = AccountRepository(db_session)
        
        account = repo.get_by_email(created_user["email"])
        
        assert account is not None
        assert account.email == created_user["email"]
    
    def test_get_by_email_not_found(self, db_session):
        """Test getting non-existent account by email"""
        repo = AccountRepository(db_session)
        
        account = repo.get_by_email("nonexistent@example.com")
        
        assert account is None
    
    def test_exists_by_username(self, db_session, created_user):
        """Test checking if username exists"""
        repo = AccountRepository(db_session)
        
        exists = repo.exists_by_username(created_user["username"])
        
        assert exists is True
    
    def test_exists_by_username_not_found(self, db_session):
        """Test checking if non-existent username exists"""
        repo = AccountRepository(db_session)
        
        exists = repo.exists_by_username("nonexistent_user")
        
        assert exists is False
    
    def test_exists_by_email(self, db_session, created_user):
        """Test checking if email exists"""
        repo = AccountRepository(db_session)
        
        exists = repo.exists_by_email(created_user["email"])
        
        assert exists is True
    
    def test_exists_by_email_not_found(self, db_session):
        """Test checking if non-existent email exists"""
        repo = AccountRepository(db_session)
        
        exists = repo.exists_by_email("nonexistent@example.com")
        
        assert exists is False
    
    def test_count_admins(self, db_session, created_admin):
        """Test counting admin users"""
        repo = AccountRepository(db_session)
        
        count = repo.count_admins()
        
        assert count >= 1
    
    def test_delete_account(self, db_session):
        """Test deleting an account"""
        repo = AccountRepository(db_session)
        
        # Create account
        account = Account(
            username="todelete",
            fullName="To Delete",
            email="delete@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        created = repo.create(account)
        account_id = str(created.id)
        
        # Delete account
        repo.delete(created)
        
        # Verify deletion
        deleted_account = repo.get_by_id(account_id)
        assert deleted_account is None
    
    def test_get_all_accounts(self, db_session, created_user, created_admin):
        """Test getting all accounts"""
        repo = AccountRepository(db_session)
        
        accounts = repo.get_all()
        
        assert len(accounts) >= 2
        assert any(str(acc.id) == created_user["id"] for acc in accounts)
        assert any(str(acc.id) == created_admin["id"] for acc in accounts)
    
    def test_username_case_insensitive(self, db_session, created_user):
        """Test that username search is case insensitive"""
        repo = AccountRepository(db_session)
        
        # Search with different case
        username_upper = created_user["username"].upper()
        account = repo.get_by_username(username_upper)
        
        # Should still find the account
        assert account is not None
        assert account.username.lower() == created_user["username"].lower()
    
    def test_email_case_insensitive(self, db_session, created_user):
        """Test that email search is case insensitive"""
        repo = AccountRepository(db_session)
        
        # Search with different case
        email_upper = created_user["email"].upper()
        account = repo.get_by_email(email_upper)
        
        # Should still find the account
        assert account is not None
        assert account.email.lower() == created_user["email"].lower()
