"""
Tests for password handling (hashing and verification)
"""
import pytest
from app.auth.password_handler import hash_password, verify_password


class TestPasswordHandler:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert hashed != password  # Should be hashed, not plain
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix
    
    def test_verify_correct_password(self):
        """Test verifying correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_incorrect_password(self):
        """Test verifying incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_hash_same_password_produces_different_hashes(self):
        """Test that hashing the same password twice produces different hashes (due to salt)"""
        password = "testpassword123"
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different due to random salt
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_verify_with_empty_password(self):
        """Test verifying with empty password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        result = verify_password("", hashed)
        
        assert result is False
    
    def test_hash_unicode_password(self):
        """Test hashing password with unicode characters"""
        password = "пароль123密码"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True
