"""
Tests for Account repository
"""
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
    
    def test_username_exists(self, db_session):
        """Test checking if username exists"""
        account = Account(
            username="existinguser",
            fullName="Existing User",
            email="existing@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        db_session.add(account)
        db_session.flush()
        
        repo = AccountRepository(db_session)
        
        # Should exist
        assert repo.username_exists("existinguser")
        
        # Should not exist
        assert not repo.username_exists("nonexistent")
    
    def test_email_exists(self, db_session):
        """Test checking if email exists"""
        account = Account(
            username="emailuser",
            fullName="Email User",
            email="testemail@example.com",
            phoneNumber="11999999999",
            password=hash_password("password123"),
            role=RoleEnum.USER
        )
        db_session.add(account)
        db_session.flush()
        
        repo = AccountRepository(db_session)
        
        # Should exist
        assert repo.email_exists("testemail@example.com")
        
        # Should not exist
        assert not repo.email_exists("nonexistent@example.com")
    
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
    
    def test_get_all_paginated(self, db_session):
        """Test getting paginated accounts"""
        repo = AccountRepository(db_session)
        
        # Create multiple accounts
        for i in range(3):
            account = Account(
                username=f"paguser{i}",
                fullName=f"User {i}",
                email=f"paguser{i}@example.com",
                phoneNumber="11999999999",
                password=hash_password("password123"),
                role=RoleEnum.USER
            )
            repo.create(account)
        
        accounts, total = repo.get_all_paginated(page=1, size=10)
        
        assert len(accounts) >= 3
        assert total >= 3
        usernames = [acc.username for acc in accounts]
        assert "paguser0" in usernames
        assert "paguser1" in usernames
        assert "paguser2" in usernames
    
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
