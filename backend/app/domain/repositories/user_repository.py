from abc import ABC, abstractmethod
from typing import List, Optional

from backend.app.domain.entities.user import User


class UserRepository(ABC):
    """Interface for user data persistence operations"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user data"""
        pass
