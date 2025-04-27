from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from backend.app.domain.entities.user import User


class AuthService(ABC):
    """Interface for authentication and authorization operations"""

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if a plaintext password matches a hash"""
        pass

    @abstractmethod
    async def get_password_hash(self, password: str) -> str:
        """Hash a password for storage"""
        pass

    @abstractmethod
    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create an access token for a user"""
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a token"""
        pass
