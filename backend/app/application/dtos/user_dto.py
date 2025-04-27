from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreateDTO(BaseModel):
    """Data transfer object for user registration"""

    username: str
    email: str
    password: str


class UserLoginDTO(BaseModel):
    """Data transfer object for user login"""

    username: str
    password: str


class UserResponseDTO(BaseModel):
    """Data transfer object for user information response"""

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
