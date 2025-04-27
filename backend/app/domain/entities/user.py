from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """User entity representing a registered user in the system"""

    id: Optional[int] = None
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    is_active: bool = True
    created_at: datetime = None
