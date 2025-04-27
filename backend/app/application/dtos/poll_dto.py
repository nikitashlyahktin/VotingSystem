from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PollOptionCreateDTO(BaseModel):
    """DTO for creating a poll option"""

    text: str


class PollCreateDTO(BaseModel):
    """DTO for creating a new poll"""

    title: str
    description: str
    multiple_choices_allowed: bool = False
    closes_at: Optional[datetime] = None
    options: List[PollOptionCreateDTO]


class PollOptionResponseDTO(BaseModel):
    """DTO for returning poll option information"""

    id: int
    text: str


class PollResponseDTO(BaseModel):
    """DTO for returning poll information"""

    id: int
    creator_id: int
    title: str
    description: str
    multiple_choices_allowed: bool
    is_closed: bool
    created_at: datetime
    closes_at: Optional[datetime]
    options: List[PollOptionResponseDTO]
