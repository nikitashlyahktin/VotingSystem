from datetime import datetime
from typing import List

from backend.app.domain.repositories.poll_repository import PollRepository
from backend.app.domain.entities.poll import Poll, PollOption
from backend.app.application.dtos.poll_dto import (
    PollCreateDTO,
    PollResponseDTO,
    PollOptionResponseDTO,
)


class CreatePollUseCase:
    def __init__(self, poll_repository: PollRepository):
        self.poll_repository = poll_repository

    async def execute(self, user_id: int, poll_data: PollCreateDTO) -> PollResponseDTO:
        """Create a new poll"""
        # Create poll options from DTO
        options = [
            PollOption(text=option.text, order=idx)
            for idx, option in enumerate(poll_data.options)
        ]

        # Create poll entity
        new_poll = Poll(
            creator_id=user_id,
            title=poll_data.title,
            description=poll_data.description,
            multiple_choices_allowed=poll_data.multiple_choices_allowed,
            closes_at=poll_data.closes_at,
            options=options,
            created_at=datetime.now(),
        )

        # Save poll to repository
        created_poll = await self.poll_repository.create(new_poll)

        # Convert to response DTO
        return self._to_dto(created_poll)

    def _to_dto(self, poll: Poll) -> PollResponseDTO:
        """Convert Poll entity to PollResponseDTO"""
        options = [
            PollOptionResponseDTO(id=opt.id, text=opt.text) for opt in poll.options
        ]

        return PollResponseDTO(
            id=poll.id,
            creator_id=poll.creator_id,
            title=poll.title,
            description=poll.description,
            multiple_choices_allowed=poll.multiple_choices_allowed,
            is_closed=poll.is_closed,
            created_at=poll.created_at,
            closes_at=poll.closes_at,
            options=options,
        )


class GetPollUseCase:
    def __init__(self, poll_repository: PollRepository):
        self.poll_repository = poll_repository

    async def execute(self, poll_id: int) -> PollResponseDTO:
        """Get a poll by id"""
        poll = await self.poll_repository.get_by_id(poll_id)
        if not poll:
            raise ValueError("Poll not found")

        return self._to_dto(poll)

    def _to_dto(self, poll: Poll) -> PollResponseDTO:
        """Convert Poll entity to PollResponseDTO"""
        options = [
            PollOptionResponseDTO(id=opt.id, text=opt.text) for opt in poll.options
        ]

        return PollResponseDTO(
            id=poll.id,
            creator_id=poll.creator_id,
            title=poll.title,
            description=poll.description,
            multiple_choices_allowed=poll.multiple_choices_allowed,
            is_closed=poll.is_closed,
            created_at=poll.created_at,
            closes_at=poll.closes_at,
            options=options,
        )


class ListPollsUseCase:
    def __init__(self, poll_repository: PollRepository):
        self.poll_repository = poll_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[PollResponseDTO]:
        """List active polls with pagination"""
        polls = await self.poll_repository.get_active_polls(skip, limit)

        return [self._to_dto(poll) for poll in polls]

    def _to_dto(self, poll: Poll) -> PollResponseDTO:
        """Convert Poll entity to
        PollResponseDTO"""

        options = [
            PollOptionResponseDTO(id=opt.id, text=opt.text) for opt in poll.options
        ]

        return PollResponseDTO(
            id=poll.id,
            creator_id=poll.creator_id,
            title=poll.title,
            description=poll.description,
            multiple_choices_allowed=poll.multiple_choices_allowed,
            is_closed=poll.is_closed,
            created_at=poll.created_at,
            closes_at=poll.closes_at,
            options=options,
        )


class ClosePollUseCase:
    def __init__(self, poll_repository: PollRepository):
        self.poll_repository = poll_repository

    async def execute(self, user_id: int, poll_id: int) -> PollResponseDTO:
        """Close a poll manually"""
        # Retrieve the poll
        poll = await self.poll_repository.get_by_id(poll_id)
        if not poll:
            raise ValueError("Poll not found")

        # Ensure user is the creator
        if poll.creator_id != user_id:
            raise ValueError("Only the creator can close this poll")

        # Close the poll
        await self.poll_repository.close_poll(poll_id)

        # Return updated poll
        updated_poll = await self.poll_repository.get_by_id(poll_id)
        return self._to_dto(updated_poll)

    def _to_dto(self, poll: Poll) -> PollResponseDTO:
        """Convert Poll entity to PollResponseDTO"""
        options = [
            PollOptionResponseDTO(id=opt.id, text=opt.text) for opt in poll.options
        ]

        return PollResponseDTO(
            id=poll.id,
            creator_id=poll.creator_id,
            title=poll.title,
            description=poll.description,
            multiple_choices_allowed=poll.multiple_choices_allowed,
            is_closed=poll.is_closed,
            created_at=poll.created_at,
            closes_at=poll.closes_at,
            options=options,
        )


class CloseExpiredPollsUseCase:
    def __init__(self, poll_repository: PollRepository):
        self.poll_repository = poll_repository

    async def execute(self) -> int:
        """Close all polls that have passed their expiration date"""
        current_time = datetime.now()
        closed_count = await self.poll_repository.close_expired_polls(current_time)
        return closed_count
