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


class TestPasswordHandlerParametrized:
    """Parametrized tests for password handling"""
    
    @pytest.mark.parametrize("password", [
        "simple123",
        "C0mpl3x!P@ssw0rd",
        "a" * 50,  # Long password
        "Spëc!@l-Çhârs_123",
        "1234567890",
        "UPPERCASE",
        "lowercase",
        "MixedCase123",
    ])
    def test_hash_and_verify_various_passwords(self, password):
        """Test hashing and verifying various password formats"""
        hashed = hash_password(password)
        
        # Should hash successfully
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert verify_password(password + "wrong", hashed) is False
    
    @pytest.mark.parametrize("wrong_password,correct_password", [
        ("password", "Password"),  # Case sensitive
        ("password123", "password124"),  # Different number
        ("password ", "password"),  # Extra space
        (" password", "password"),  # Leading space
        ("passwor", "password"),  # Missing character
        ("passwords", "password"),  # Extra character
    ])
    def test_verify_similar_but_wrong_passwords(self, wrong_password, correct_password):
        """Test that similar but incorrect passwords fail verification"""
        hashed = hash_password(correct_password)
        
        assert verify_password(wrong_password, hashed) is False
        assert verify_password(correct_password, hashed) is True
    
    @pytest.mark.parametrize("password", [
        "",  # Empty
        " ",  # Just space
        "   ",  # Multiple spaces
    ])
    def test_verify_empty_or_whitespace_passwords(self, password):
        """Test verification with empty or whitespace passwords"""
        correct_password = "testpassword123"
        hashed = hash_password(correct_password)
        
        # Empty/whitespace should not match
        assert verify_password(password, hashed) is False
