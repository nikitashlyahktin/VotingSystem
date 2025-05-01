from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PollOptionBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=255)

class PollOptionCreate(PollOptionBase):
    pass

class PollOptionResponse(PollOptionBase):
    id: int
    poll_id: int
    vote_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class PollBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10, max_length=1000)
    is_multiple_choice: bool = False
    closing_date: Optional[datetime] = None

class PollCreate(PollBase):
    options: List[PollOptionCreate]

class PollResponse(PollBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    options: List[PollOptionResponse]
    
    class Config:
        from_attributes = True

class VoteCreate(BaseModel):
    poll_id: int
    option_ids: List[int]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 