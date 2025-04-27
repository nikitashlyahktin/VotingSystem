from pydantic import BaseModel
from typing import Dict
from datetime import datetime


class VoteCreateDTO(BaseModel):
    """DTO for creating a new vote"""

    poll_id: int
    option_id: int


class VoteResponseDTO(BaseModel):
    """DTO for returning vote information"""

    id: int
    user_id: int
    poll_id: int
    option_id: int
    created_at: datetime
    updated_at: datetime = None


class PollResultsDTO(BaseModel):
    """DTO for returning poll results"""

    poll_id: int
    is_closed: bool
    total_votes: int
    results: Dict[int, int]  # option_id -> count
