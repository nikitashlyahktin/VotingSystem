import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from backend.app.infrastructure.security.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_active_user,
    SECRET_KEY,
    ALGORITHM,
    oauth2_scheme
)


class TestPasswordHandling:
    def test_password_hashing(self):
        """Test that passwords are properly hashed and verified"""
        # Test hashing
        password = "securepassword123"
        hashed = get_password_hash(password)

        # Verify the hash is different from the original password
        assert hashed != password

        # Verify the password correctly
        assert verify_password(password, hashed) is True

        # Verify wrong password fails
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_different_for_same_password(self):
        """Test that hashing the same password twice gives different hashes (due to salt)"""
        password = "securepassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to different salts
        assert hash1 != hash2

        # But both should verify against the original password
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_password_hashing_empty_string(self):
        """Test hashing and verification with empty string (edge case)"""
        password = ""
        hashed = get_password_hash(password)

        # Empty password should still hash to something
        assert hashed != password
        assert len(hashed) > 0

        # Verify the empty password correctly
        assert verify_password(password, hashed) is True
        assert verify_password("not-empty", hashed) is False


class TestTokenHandling:
    def test_create_access_token(self):
        """Test token creation with different expiry times"""
        data = {"sub": "test@example.com"}

        # Test with default expiry
        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("sub") == "test@example.com"
        assert "exp" in payload

        # Test with custom expiry
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("sub") == "test@example.com"

        # Expiry time should be set (we can't test the exact value due to timing differences)
        assert "exp" in payload

    def test_token_expiry_calculation(self):
        """Test that token expiry is calculated correctly"""
        # Set a fixed expiry time for testing
        test_expires_delta = timedelta(minutes=30)

        # Get approximate current time
        before_token = datetime.utcnow()

        # Create token with specific expiry
        token = create_access_token({"sub": "test@example.com"}, expires_delta=test_expires_delta)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Get time after token creation
        after_token = datetime.utcnow()

        # Extract expiry from token as a UTC timestamp - fixing timezone issue
        token_exp = datetime.utcfromtimestamp(payload["exp"])

        # Instead of exact comparison, check that the expiration time is within a reasonable range
        # The token expiry should be between now+delta-5sec and now+delta+5sec
        # This handles potential timing differences during test execution
        expected_min = before_token + test_expires_delta - timedelta(seconds=10)
        expected_max = after_token + test_expires_delta + timedelta(seconds=10)

        # Assert with a more lenient check
        assert token_exp >= expected_min, f"Token expiry {token_exp} is before minimum expected time {expected_min}"
        assert token_exp <= expected_max, f"Token expiry {token_exp} is after maximum expected time {expected_max}"

    def test_token_with_additional_claims(self):
        """Test creating tokens with additional claims"""
        data = {
            "sub": "test@example.com",
            "user_id": 123,
            "role": "admin"
        }

        token = create_access_token(data)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify all claims are present
        assert payload.get("sub") == "test@example.com"
        assert payload.get("user_id") == 123
        assert payload.get("role") == "admin"
        assert "exp" in payload


class TestUserAuthentication:
    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful user retrieval from token"""
        # Create a mock user
        user = MagicMock()
        user.email = "test@example.com"
        user.is_active = True

        # Create a mock database session
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_first = MagicMock(return_value=user)

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first = mock_first

        # Create a valid token
        token = create_access_token({"sub": "test@example.com"})

        # Mock jwt.decode to return our payload
        with patch('jose.jwt.decode', return_value={"sub": "test@example.com"}):
            # Call the function
            result_user = await get_current_user(token, mock_db)

            # Verify the result
            assert result_user == user

    @pytest.mark.asyncio
    async def test_get_current_user_missing_email(self):
        """Test error when email is missing from token"""
        # Mock jwt.decode to return payload without 'sub' claim
        with patch('jose.jwt.decode', return_value={}):
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user("token", MagicMock())

            # Check the exception details
            assert excinfo.value.status_code == 401
            assert "could not validate credentials" in str(excinfo.value.detail).lower()

    @pytest.mark.asyncio
    async def test_get_current_user_jwt_error(self):
        """Test error when JWT decoding fails"""
        # Mock jwt.decode to raise JWTError
        with patch('jose.jwt.decode', side_effect=JWTError()):
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user("invalid_token", MagicMock())

            # Check the exception details
            assert excinfo.value.status_code == 401
            assert "could not validate credentials" in str(excinfo.value.detail).lower()

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """Test error when user is not found in database"""
        # Create a mock database session that returns None for user
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_first = MagicMock(return_value=None)

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first = mock_first

        # Mock jwt.decode to return valid payload
        with patch('jose.jwt.decode', return_value={"sub": "nonexistent@example.com"}):
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user("token", mock_db)

            # Check the exception details
            assert excinfo.value.status_code == 401
            assert "could not validate credentials" in str(excinfo.value.detail).lower()

    @pytest.mark.asyncio
    async def test_get_current_active_user(self):
        """Test active user check"""
        # Create active user
        active_user = MagicMock()
        active_user.is_active = True

        # Test with active user
        result = await get_current_active_user(active_user)
        assert result == active_user

        # Create inactive user
        inactive_user = MagicMock()
        inactive_user.is_active = False

        # Test with inactive user - should raise HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await get_current_active_user(inactive_user)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert "inactive user" in str(excinfo.value.detail).lower()

    @pytest.mark.asyncio
    async def test_oauth2_scheme(self):
        """Test that the OAuth2 scheme is properly configured"""
        # Verify the scheme is properly configured
        assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"
        assert oauth2_scheme.auto_error is True
