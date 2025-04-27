from typing import Optional, Dict, Any

from backend.app.domain.services.auth_service import AuthService
from backend.app.domain.repositories.user_repository import UserRepository
from backend.app.domain.entities.user import User
from backend.app.application.dtos.user_dto import (
    UserCreateDTO,
    UserLoginDTO,
    UserResponseDTO,
)


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def execute(self, user_data: UserCreateDTO) -> UserResponseDTO:
        """Register a new user"""
        # Check if username or email already exists
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already registered")

        existing_email = await self.user_repository.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already registered")

        # Create new user
        hashed_password = await self.auth_service.get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        created_user = await self.user_repository.create(new_user)

        # Return user data without password
        return UserResponseDTO(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
        )


class LoginUserUseCase:
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def execute(self, login_data: UserLoginDTO) -> Dict[str, Any]:
        """Authenticate a user and generate access token"""
        # Find the user
        user = await self.user_repository.get_by_username(login_data.username)
        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        valid_password = await self.auth_service.verify_password(
            login_data.password, user.hashed_password
        )
        if not valid_password:
            raise ValueError("Invalid credentials")

        # Generate token
        token_data = {"sub": user.username, "user_id": user.id}
        token = await self.auth_service.create_access_token(token_data)

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponseDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
            ),
        }


class GetCurrentUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: int) -> UserResponseDTO:
        """Get current user information"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return UserResponseDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
        )
