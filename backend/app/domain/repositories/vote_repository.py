from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from backend.app.domain.entities.vote import Vote


class VoteRepository(ABC):
    """Interface for vote data persistence operations"""

    @abstractmethod
    async def create(self, vote: Vote) -> Vote:
        """Create a new vote"""
        pass

    @abstractmethod
    async def get_by_id(self, vote_id: int) -> Optional[Vote]:
        """Get vote by ID"""
        pass

    @abstractmethod
    async def get_user_vote_for_poll(
        self, user_id: int, poll_id: int
    ) -> Optional[Vote]:
        """Get a user's vote for a specific poll"""
        pass

    @abstractmethod
    async def get_poll_results(self, poll_id: int) -> Dict[int, int]:
        """Get poll results as a dictionary of option_id to vote count"""
        pass

    @abstractmethod
    async def update(self, vote: Vote) -> Vote:
        """Update an existing vote (change option)"""
        pass

    @abstractmethod
    async def delete(self, vote_id: int) -> bool:
        """Delete a vote"""
        pass
