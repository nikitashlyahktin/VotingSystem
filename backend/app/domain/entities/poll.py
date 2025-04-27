from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class PollOption:
    """Option that can be selected in a poll"""

    id: Optional[int] = None
    poll_id: Optional[int] = None
    text: str = ""
    order: int = 0


@dataclass
class Poll:
    """Poll entity representing a voting poll created by a user"""

    id: Optional[int] = None
    creator_id: int = 0
    title: str = ""
    description: str = ""
    multiple_choices_allowed: bool = False
    is_closed: bool = False
    created_at: datetime = None
    closes_at: Optional[datetime] = None
    options: List[PollOption] = field(default_factory=list)
