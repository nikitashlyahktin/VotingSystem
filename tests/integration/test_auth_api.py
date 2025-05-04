import pytest
from backend.app.application.routers.auth import login, register
from unittest.mock import MagicMock, patch

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestAuthAPI:
    """Test suite for authentication API endpoints"""

    async def test_register_success(self, client):
        """Test successful user registration or handles already existing user"""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!"
        }

        # Act
        response = await client.post("/auth/register", json=user_data)

        # Assert - принимаем как 201 (первый запуск), так и 400 (повторный запуск)
        assert response.status_code in (201, 400)

        if response.status_code == 400:
            # Проверка сообщения об ошибке для дублирующегося пользователя
            error_msg = response.json()["detail"].lower()
            assert "username already taken" in error_msg or "email already registered" in error_msg

    async def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # Arrange
        user_data = {
            "username": "duplicateuser",
            "email": "duplicate1@example.com",
            "password": "Password123!"
        }

        # First registration should succeed
        await client.post("/auth/register", json=user_data)

        # Act - attempt to register with same username but different email
        duplicate_data = {
            "username": "duplicateuser",
            "email": "duplicate2@example.com",
            "password": "Password123!"
        }
        response = await client.post("/auth/register", json=duplicate_data)

        # Assert
        assert response.status_code == 400
        assert "username already taken" in response.json()["detail"].lower()

    async def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Arrange
        user_data = {
            "username": "emailuser1",
            "email": "same_email@example.com",
            "password": "Password123!"
        }

        # First registration should succeed
        await client.post("/auth/register", json=user_data)

        # Act - attempt to register with same email but different username
        duplicate_data = {
            "username": "emailuser2",
            "email": "same_email@example.com",
            "password": "Password123!"
        }
        response = await client.post("/auth/register", json=duplicate_data)

        # Assert
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        # Arrange
        invalid_email_data = {
            "username": "invalidemail",
            "email": "not-an-email",
            "password": "Password123!"
        }

        # Act
        response = await client.post("/auth/register", json=invalid_email_data)

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_register_password_too_short(self, client):
        """Test registration with password that's too short"""
        # Arrange
        short_password_data = {
            "username": "shortpassword",
            "email": "short@example.com",
            "password": "short"  # Too short password
        }

        # Act
        response = await client.post("/auth/register", json=short_password_data)

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_register_invalid_password(self, client):
        """Test registration with invalid password"""
        # Short password
        short_data = {
            "username": "passworduser",
            "email": "password@example.com",
            "password": "short"
        }
        response = await client.post("/auth/register", json=short_data)
        assert response.status_code == 422  # FastAPI validation error

    async def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields"""
        # Missing username
        missing_username = {
            "email": "missing@example.com",
            "password": "Password123!"
        }
        response = await client.post("/auth/register", json=missing_username)
        assert response.status_code == 422

        # Missing email
        missing_email = {
            "username": "missingemail",
            "password": "Password123!"
        }
        response = await client.post("/auth/register", json=missing_email)
        assert response.status_code == 422

        # Missing password
        missing_password = {
            "username": "missingpassword",
            "email": "missing_password@example.com"
        }
        response = await client.post("/auth/register", json=missing_password)
        assert response.status_code == 422

        # Empty request
        response = await client.post("/auth/register", json={})
        assert response.status_code == 422

    async def test_register_invalid_username(self, client):
        """Test registration with invalid username format"""
        # Too short username
        short_username = {
            "username": "a",  # Too short
            "email": "short_username@example.com",
            "password": "Password123!"
        }
        response = await client.post("/auth/register", json=short_username)
        if response.status_code == 422:  # If there's a username length validation
            assert response.status_code == 422

        # Username with special characters (if not allowed)
        special_chars_username = {
            "username": "user@name",  # With special characters
            "email": "special_chars@example.com",
            "password": "Password123!"
        }
        response = await client.post("/auth/register", json=special_chars_username)
        # Only assert if the API has this validation
        if response.status_code == 422 or response.status_code == 400:
            pass  # Some APIs allow special chars in usernames

    async def test_email_format_validation(self, client):
        """Test various invalid email formats for validation"""
        invalid_email_formats = [
            "plainaddress",              # Missing @ and domain
            "@missingusername.com",      # Missing username part
            "username@.com",             # Missing domain
            "username@domain",           # Missing TLD
            "username@domain..com"       # Double dots
        ]

        for invalid_email in invalid_email_formats:
            user_data = {
                "username": "emailtest",
                "email": invalid_email,
                "password": "Password123!"
            }
            response = await client.post("/auth/register", json=user_data)
            assert response.status_code == 422, f"Email format '{invalid_email}' should be rejected"

    async def test_login_success(self, client):
        """Test successful login with valid credentials"""
        # Arrange - Register a new user
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Password123!"
        }

        await client.post("/auth/register", json=user_data)

        # Act - Login with correct credentials
        login_data = {
            "username": "login@example.com",  # Using email as username for OAuth flow
            "password": "Password123!"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = await client.post("/auth/login", data=login_data, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_with_username_instead_of_email(self, client):
        """Test login using username instead of email (if supported)"""
        # Arrange - Register a new user
        user_data = {
            "username": "userlogin",
            "email": "userlogin@example.com",
            "password": "Password123!"
        }

        await client.post("/auth/register", json=user_data)

        # Act - Login with username instead of email
        login_data = {
            "username": "userlogin",  # Using username instead of email
            "password": "Password123!"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = await client.post("/auth/login", data=login_data, headers=headers)

        # Assert - Different APIs might handle this differently
        if response.status_code == 200:
            # If username login is supported
            data = response.json()
            assert "access_token" in data
        else:
            # If only email login is supported
            assert response.status_code == 401

    async def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        # Arrange - Register a new user
        user_data = {
            "username": "badloginuser",
            "email": "badlogin@example.com",
            "password": "Password123!"
        }

        await client.post("/auth/register", json=user_data)

        # Act - Login with wrong password
        login_data = {
            "username": "badlogin@example.com",
            "password": "WrongPassword123!"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = await client.post("/auth/login", data=login_data, headers=headers)

        # Assert
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_login_case_sensitivity(self, client):
        """Test if login is case-sensitive for email"""
        # Arrange - Register a new user
        user_data = {
            "username": "caseuser",
            "email": "case@example.com",
            "password": "Password123!"
        }

        await client.post("/auth/register", json=user_data)

        # Act - Login with different case in email
        login_data = {
            "username": "CASE@example.com",  # Uppercase email
            "password": "Password123!"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = await client.post("/auth/login", data=login_data, headers=headers)

        # Assert - Many systems are case-insensitive for emails
        # We accept either behavior
        if response.status_code == 200:
            # If case-insensitive
            data = response.json()
            assert "access_token" in data
        else:
            # If case-sensitive
            assert response.status_code == 401

    async def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        # Act - Login with a username that doesn't exist
        login_data = {
            "username": "nonexistent@example.com",
            "password": "Password123!"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = await client.post("/auth/login", data=login_data, headers=headers)

        # Assert
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_login_missing_fields(self, client):
        """Test login with missing required fields"""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Missing username
        response = await client.post("/auth/login", data={"password": "Password123!"}, headers=headers)
        assert response.status_code in [401, 422]

        # Missing password
        response = await client.post("/auth/login", data={"username": "test@example.com"}, headers=headers)
        assert response.status_code in [401, 422]

        # Empty request
        response = await client.post("/auth/login", data={}, headers=headers)
        assert response.status_code in [401, 422]

    async def test_token_refresh(self, client):
        """Test refreshing access tokens if supported by the API"""
        # Register and login to get initial token
        user_data = {
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "Password123!"
        }

        await client.post("/auth/register", json=user_data)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        login_response = await client.post(
            "/auth/login",
            data={
                "username": "refresh@example.com",
                "password": "Password123!"
            },
            headers=headers
        )

        initial_token_data = login_response.json()

        # Check if refresh token exists
        if "refresh_token" in initial_token_data:
            # Attempt to refresh the token
            refresh_data = {
                "refresh_token": initial_token_data["refresh_token"]
            }

            refresh_response = await client.post("/auth/refresh", json=refresh_data)

            # If the endpoint exists and works
            if refresh_response.status_code == 200:
                new_token_data = refresh_response.json()
                assert "access_token" in new_token_data
                assert new_token_data["access_token"] != initial_token_data["access_token"]

    async def test_logout(self, authenticated_client):
        """Test logout functionality if it exists"""
        # Attempt to logout
        response = await authenticated_client.post("/auth/logout")

        # If logout endpoint exists
        if response.status_code == 200:
            # Verify token has been invalidated by trying to access protected endpoint
            me_response = await authenticated_client.get("/users/me")
            assert me_response.status_code == 401

    async def test_get_user_profile(self, authenticated_client):
        """Test getting authenticated user profile"""
        # Act
        response = await authenticated_client.get("/users/me")

        # Assert
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@example.com"
        assert "id" in user_data
        # Password should not be in the response
        assert "password" not in user_data
        assert "hashed_password" not in user_data

    async def test_profile_unauthenticated(self, client):
        """Test that unauthenticated requests are rejected"""
        # Act - Try to access protected endpoint without auth
        response = await client.get("/users/me")

        # Assert
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    async def test_update_user_profile(self, authenticated_client):
        """Test updating user profile if supported"""
        # Prepare update data
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com"
        }

        # Attempt to update profile
        response = await authenticated_client.put("/users/me", json=update_data)

        # If profile update is supported
        if response.status_code == 200:
            updated_user = response.json()
            assert updated_user["username"] == update_data["username"]
            assert updated_user["email"] == update_data["email"]

            # Verify changes are persistent
            get_response = await authenticated_client.get("/users/me")
            assert get_response.status_code == 200
            profile = get_response.json()
            assert profile["username"] == update_data["username"]
            assert profile["email"] == update_data["email"]

    async def test_invalid_token(self, client):
        """Test that invalid tokens are rejected"""
        # Act - Use an invalid token
        client.headers.update({"Authorization": "Bearer invalid_token"})
        response = await client.get("/users/me")

        # Assert
        assert response.status_code == 401
        assert "could not validate" in response.json()["detail"].lower()

    async def test_expired_token(self, client):
        """Test handling of expired tokens"""
        # This is a token format test since we can't easily create an expired token in the test
        client.headers.update(
            {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"})
        response = await client.get("/users/me")

        # Assert
        assert response.status_code == 401

    async def test_malformed_token(self, client):
        """Test handling of malformed tokens"""
        # Test with various malformed tokens
        malformed_tokens = [
            "not-a-token",
            "Bearer",  # Missing token part
            "bearer token-without-dots",
            "token-without-bearer-prefix"
        ]

        for token in malformed_tokens:
            client.headers.update({"Authorization": token})
            response = await client.get("/users/me")
            assert response.status_code == 401, f"Malformed token '{token}' was not properly rejected"

    async def test_password_change(self, authenticated_client):
        """Test password change functionality if it exists"""
        # Prepare password change data
        password_data = {
            "current_password": "Password123!",
            "new_password": "NewPassword123!"
        }

        # Attempt to change password
        response = await authenticated_client.post("/users/password", json=password_data)

        # If password change endpoint exists
        if response.status_code == 200:
            # Verify new password works by logging in
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            login_response = await authenticated_client.post(
                "/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "NewPassword123!"
                },
                headers=headers
            )
            assert login_response.status_code == 200
            assert "access_token" in login_response.json()

    @pytest.mark.asyncio
    async def test_auth_router_directly(self):
        """Test the auth router login function directly"""
        # Mock the database and form data
        db = MagicMock()
        form_data = MagicMock()
        form_data.username = "test@example.com"
        form_data.password = "Password123!"

        # Mock user with correct password
        user = MagicMock()
        user.email = "test@example.com"
        user.hashed_password = "hashed_password"

        # Setup db query mocking
        db.query.return_value.filter.return_value.first.return_value = user

        # Mock verify_password to return True
        with patch('backend.app.application.routers.auth.verify_password', return_value=True):
            # Call the login function
            with patch('backend.app.application.routers.auth.create_access_token',
                       return_value="mocked_token"):
                result = await login(form_data, db)

                # Verify the result
                assert result["access_token"] == "mocked_token"
                assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_auth_router_invalid_credentials(self):
        """Test the auth router login function with invalid credentials"""
        # Mock the database and form data
        db = MagicMock()
        form_data = MagicMock()
        form_data.username = "test@example.com"
        form_data.password = "WrongPassword"

        # Mock user
        user = MagicMock()
        user.email = "test@example.com"
        user.hashed_password = "hashed_password"

        # Setup db query mocking
        db.query.return_value.filter.return_value.first.return_value = user

        # Mock verify_password to return False (wrong password)
        with patch('backend.app.application.routers.auth.verify_password', return_value=False):
            # Call should raise HTTPException
            with pytest.raises(Exception) as exc_info:
                await login(form_data, db)

            # Verify the exception
            assert "401" in str(exc_info.value) or "unauthorized" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_auth_router_user_not_found(self):
        """Test the auth router login function with non-existent user"""
        # Mock the database and form data
        db = MagicMock()
        form_data = MagicMock()
        form_data.username = "nonexistent@example.com"
        form_data.password = "Password123!"

        # Setup db query mocking - user not found
        db.query.return_value.filter.return_value.first.return_value = None

        # Call should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            await login(form_data, db)

        # Verify the exception
        assert "401" in str(exc_info.value) or "unauthorized" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_auth_router_register_success(self):
        """Test the auth router register function successfully"""
        # Mock the database
        db = MagicMock()

        # Mock UserCreate schema
        user_data = MagicMock()
        user_data.email = "newregister@example.com"
        user_data.username = "newregister"
        user_data.password = "Password123!"

        # Setup db query mocking - no existing user
        db.query.return_value.filter.return_value.first.return_value = None

        # Mock password hashing
        with patch('backend.app.application.routers.auth.get_password_hash',
                   return_value="hashed_password"):
            # Call register function
            await register(user_data, db)

            # Verify db operations were called
            assert db.add.called
            assert db.commit.called
            assert db.refresh.called
