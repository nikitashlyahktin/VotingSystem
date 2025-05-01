from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...domain.schemas import PollCreate, PollResponse, VoteCreate
from ...infrastructure.database.database import get_db_session
from ...infrastructure.database.models import Poll, PollOption, User, poll_votes
from ...infrastructure.security.auth import get_current_active_user
from ...application.dtos.vote_dto import PollResultsDTO

router = APIRouter()

@router.post("/", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
async def create_poll(
    poll: PollCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    # Create poll
    db_poll = Poll(
        title=poll.title,
        description=poll.description,
        is_multiple_choice=poll.is_multiple_choice,
        closing_date=poll.closing_date,
        creator_id=current_user.id
    )
    db.add(db_poll)
    db.commit()
    db.refresh(db_poll)
    
    # Create poll options
    for option in poll.options:
        db_option = PollOption(poll_id=db_poll.id, text=option.text)
        db.add(db_option)
    
    db.commit()
    db.refresh(db_poll)
    return db_poll

@router.get("/", response_model=List[PollResponse])
async def list_polls(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    polls = db.query(Poll).offset(skip).limit(limit).all()
    return polls

@router.get("/{poll_id}", response_model=PollResponse)
async def get_poll(
    poll_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    return poll

@router.post("/{poll_id}/vote")
async def vote(
    poll_id: int,
    vote: VoteCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    # Check if poll exists and is active
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    if not poll.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Poll is closed"
        )
    
    if poll.closing_date and poll.closing_date < datetime.utcnow():
        poll.is_active = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Poll has expired"
        )
    
    # Validate vote options
    options = db.query(PollOption).filter(
        PollOption.id.in_(vote.option_ids),
        PollOption.poll_id == poll_id
    ).all()
    
    if len(options) != len(vote.option_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid option IDs"
        )
    
    if not poll.is_multiple_choice and len(vote.option_ids) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This poll only allows single choice"
        )
    
    # Remove previous votes
    db.query(poll_votes).filter(
        poll_votes.c.user_id == current_user.id,
        poll_votes.c.poll_id == poll_id
    ).delete()
    
    # Add new votes
    for option_id in vote.option_ids:
        db.execute(
            poll_votes.insert().values(
                user_id=current_user.id,
                option_id=option_id,
                poll_id=poll_id
            )
        )
    
    db.commit()
    return {"message": "Vote recorded successfully"}

@router.post("/{poll_id}/close")
async def close_poll(
    poll_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    if poll.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the poll creator can close the poll"
        )
    
    poll.is_active = False
    db.commit()
    return {"message": "Poll closed successfully"}

@router.get("/{poll_id}/results", response_model=PollResultsDTO)
async def get_poll_results(
    poll_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    # Check if poll exists
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found"
        )
    
    # Get vote counts for each option
    results = {}
    for option in poll.options:
        vote_count = db.query(func.count(poll_votes.c.user_id)).filter(
            poll_votes.c.option_id == option.id
        ).scalar()
        results[option.id] = vote_count
    
    # Count total votes
    total_votes = sum(results.values())
    
    return PollResultsDTO(
        poll_id=poll_id,
        is_closed=not poll.is_active,
        total_votes=total_votes,
        results=results
    ) 