from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Vote:
    """Vote entity representing a user's vote on a poll option"""

    id: Optional[int] = None
    user_id: int = 0
    poll_id: int = 0
    option_id: int = 0
    created_at: datetime = None
    updated_at: Optional[datetime] = None
