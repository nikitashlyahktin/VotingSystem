from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from backend.app.domain.entities.poll import Poll


class PollRepository(ABC):
    """Interface for poll data persistence operations"""

    @abstractmethod
    async def create(self, poll: Poll) -> Poll:
        """Create a new poll"""
        pass

    @abstractmethod
    async def get_by_id(self, poll_id: int) -> Optional[Poll]:
        """Get poll by ID"""
        pass

    @abstractmethod
    async def get_active_polls(self, skip: int = 0, limit: int = 100) -> List[Poll]:
        """Get active polls with pagination"""
        pass

    @abstractmethod
    async def get_user_polls(self, user_id: int) -> List[Poll]:
        """Get polls created by a specific user"""
        pass

    @abstractmethod
    async def update(self, poll: Poll) -> Poll:
        """Update poll data"""
        pass

    @abstractmethod
    async def close_poll(self, poll_id: int) -> bool:
        """Close a poll manually"""
        pass

    @abstractmethod
    async def close_expired_polls(self, current_time: datetime) -> int:
        """Close all polls that have passed their expiration date"""
        pass
