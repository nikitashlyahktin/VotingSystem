import pytest
from datetime import datetime, timedelta
from backend.app.domain.entities.user import User
from backend.app.domain.entities.poll import Poll, PollOption
from backend.app.domain.entities.vote import Vote


class TestUserEntity:
    def test_user_creation(self):
        """Test that a User entity can be created with default and custom values"""
        # Default user
        default_user = User()
        assert default_user.id is None
        assert default_user.username == ""
        assert default_user.email == ""
        assert default_user.hashed_password == ""
        assert default_user.is_active is True
        assert default_user.created_at is None

        # Custom user
        now = datetime.now()
        custom_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            is_active=True,
            created_at=now
        )
        assert custom_user.id == 1
        assert custom_user.username == "testuser"
        assert custom_user.email == "test@example.com"
        assert custom_user.hashed_password == "hashedpassword123"
        assert custom_user.is_active is True
        assert custom_user.created_at == now


class TestPollEntity:
    def test_poll_option_creation(self):
        """Test that a PollOption entity can be created with default and custom values"""
        # Default poll option
        default_option = PollOption()
        assert default_option.id is None
        assert default_option.poll_id is None
        assert default_option.text == ""
        assert default_option.order == 0

        # Custom poll option
        custom_option = PollOption(
            id=1,
            poll_id=10,
            text="Option 1",
            order=1
        )
        assert custom_option.id == 1
        assert custom_option.poll_id == 10
        assert custom_option.text == "Option 1"
        assert custom_option.order == 1

    def test_poll_creation(self):
        """Test that a Poll entity can be created with default and custom values"""
        # Default poll
        default_poll = Poll()
        assert default_poll.id is None
        assert default_poll.creator_id == 0
        assert default_poll.title == ""
        assert default_poll.description == ""
        assert default_poll.multiple_choices_allowed is False
        assert default_poll.is_closed is False
        assert default_poll.created_at is None
        assert default_poll.closes_at is None
        assert default_poll.options == []

        # Custom poll
        now = datetime.now()
        close_date = now + timedelta(days=7)
        options = [
            PollOption(id=1, poll_id=10, text="Option 1", order=1),
            PollOption(id=2, poll_id=10, text="Option 2", order=2)
        ]
        
        custom_poll = Poll(
            id=10,
            creator_id=1,
            title="Test Poll",
            description="This is a test poll",
            multiple_choices_allowed=True,
            is_closed=False,
            created_at=now,
            closes_at=close_date,
            options=options
        )
        
        assert custom_poll.id == 10
        assert custom_poll.creator_id == 1
        assert custom_poll.title == "Test Poll"
        assert custom_poll.description == "This is a test poll"
        assert custom_poll.multiple_choices_allowed is True
        assert custom_poll.is_closed is False
        assert custom_poll.created_at == now
        assert custom_poll.closes_at == close_date
        assert len(custom_poll.options) == 2
        assert custom_poll.options[0].text == "Option 1"
        assert custom_poll.options[1].text == "Option 2"


class TestVoteEntity:
    def test_vote_creation(self):
        """Test that a Vote entity can be created with default and custom values"""
        # Default vote
        default_vote = Vote()
        assert default_vote.id is None
        assert default_vote.user_id == 0
        assert default_vote.poll_id == 0
        assert default_vote.option_id == 0
        assert default_vote.created_at is None
        assert default_vote.updated_at is None

        # Custom vote
        now = datetime.now()
        custom_vote = Vote(
            id=1,
            user_id=5,
            poll_id=10,
            option_id=15,
            created_at=now,
            updated_at=now
        )
        assert custom_vote.id == 1
        assert custom_vote.user_id == 5
        assert custom_vote.poll_id == 10
        assert custom_vote.option_id == 15
        assert custom_vote.created_at == now
        assert custom_vote.updated_at == now 