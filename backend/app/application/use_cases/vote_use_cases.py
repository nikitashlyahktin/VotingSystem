from datetime import datetime
from typing import Dict, Optional

from backend.app.domain.repositories.vote_repository import VoteRepository
from backend.app.domain.repositories.poll_repository import PollRepository
from backend.app.domain.entities.vote import Vote
from backend.app.application.dtos.vote_dto import (
    VoteCreateDTO,
    VoteResponseDTO,
    PollResultsDTO,
)


class CreateVoteUseCase:
    def __init__(
        self, vote_repository: VoteRepository, poll_repository: PollRepository
    ):
        self.vote_repository = vote_repository
        self.poll_repository = poll_repository

    async def execute(self, user_id: int, vote_data: VoteCreateDTO) -> VoteResponseDTO:
        """Create a new vote or update existing vote"""
        # Check if poll exists and is active
        poll = await self.poll_repository.get_by_id(vote_data.poll_id)
        if not poll:
            raise ValueError("Poll not found")

        if poll.is_closed:
            raise ValueError("Poll is closed")

        # Check if the option belongs to the poll
        valid_option = any(opt.id == vote_data.option_id for opt in poll.options)
        if not valid_option:
            raise ValueError("Invalid option for this poll")

        # Check if user already voted
        existing_vote = await self.vote_repository.get_user_vote_for_poll(
            user_id, vote_data.poll_id
        )

        if existing_vote:
            # Update existing vote
            existing_vote.option_id = vote_data.option_id
            existing_vote.updated_at = datetime.now()
            updated_vote = await self.vote_repository.update(existing_vote)
            return self._to_dto(updated_vote)
        else:
            # Create new vote
            new_vote = Vote(
                user_id=user_id,
                poll_id=vote_data.poll_id,
                option_id=vote_data.option_id,
                created_at=datetime.now(),
            )
            created_vote = await self.vote_repository.create(new_vote)
            return self._to_dto(created_vote)

    def _to_dto(self, vote: Vote) -> VoteResponseDTO:
        """Convert Vote entity to VoteResponseDTO"""
        return VoteResponseDTO(
            id=vote.id,
            user_id=vote.user_id,
            poll_id=vote.poll_id,
            option_id=vote.option_id,
            created_at=vote.created_at,
            updated_at=vote.updated_at,
        )


class GetPollResultsUseCase:
    def __init__(
        self, vote_repository: VoteRepository, poll_repository: PollRepository
    ):
        self.vote_repository = vote_repository
        self.poll_repository = poll_repository

    async def execute(self, poll_id: int) -> PollResultsDTO:
        """Get results for a poll"""
        # Check if poll exists
        poll = await self.poll_repository.get_by_id(poll_id)
        if not poll:
            raise ValueError("Poll not found")

        # Get vote counts for each option
        results = await self.vote_repository.get_poll_results(poll_id)

        # Count total votes
        total_votes = sum(results.values())

        return PollResultsDTO(
            poll_id=poll_id,
            is_closed=poll.is_closed,
            total_votes=total_votes,
            results=results,
        )
