import pytest
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from backend.app.domain.entities.user import User
from backend.app.domain.entities.poll import Poll, PollOption
from backend.app.domain.entities.vote import Vote
from backend.app.domain.repositories.user_repository import UserRepository
from backend.app.domain.repositories.poll_repository import PollRepository
from backend.app.domain.repositories.vote_repository import VoteRepository


class MockUserRepository(UserRepository):
    """Mock implementation of user repository for testing"""

    def __init__(self):
        self.users = {}
        self.id_counter = 1
        self.emails = {}
        self.usernames = {}

    async def create(self, user: User) -> User:
        if user.email in self.emails:
            raise ValueError(f"Email {user.email} already exists")

        if user.username in self.usernames:
            raise ValueError(f"Username {user.username} already taken")

        user.id = self.id_counter
        self.id_counter += 1
        user.created_at = datetime.now()

        self.users[user.id] = user
        self.emails[user.email] = user.id
        self.usernames[user.username] = user.id

        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        user_id = self.emails.get(email)
        if user_id:
            return self.users.get(user_id)
        return None

    async def get_by_username(self, username: str) -> Optional[User]:
        user_id = self.usernames.get(username)
        if user_id:
            return self.users.get(user_id)
        return None

    async def update(self, user: User) -> User:
        if user.id not in self.users:
            raise ValueError(f"User with ID {user.id} not found")

        # Check if email is being changed to one that already exists
        if user.email != self.users[user.id].email and user.email in self.emails:
            raise ValueError(f"Email {user.email} already exists")

        # Check if username is being changed to one that already exists
        if user.username != self.users[user.id].username and user.username in self.usernames:
            raise ValueError(f"Username {user.username} already taken")

        # Update email mapping if changed
        if user.email != self.users[user.id].email:
            old_email = self.users[user.id].email
            del self.emails[old_email]
            self.emails[user.email] = user.id

        # Update username mapping if changed
        if user.username != self.users[user.id].username:
            old_username = self.users[user.id].username
            del self.usernames[old_username]
            self.usernames[user.username] = user.id

        self.users[user.id] = user
        return user


class MockPollRepository(PollRepository):
    """Mock implementation of poll repository for testing"""

    def __init__(self):
        self.polls = {}
        self.id_counter = 1
        self.option_id_counter = 1

    async def create(self, poll: Poll) -> Poll:
        poll.id = self.id_counter
        self.id_counter += 1
        poll.created_at = datetime.now()

        # Set IDs for options and link to poll
        for option in poll.options:
            option.id = self.option_id_counter
            self.option_id_counter += 1
            option.poll_id = poll.id

        self.polls[poll.id] = poll
        return poll

    async def get_by_id(self, poll_id: int) -> Optional[Poll]:
        return self.polls.get(poll_id)

    async def get_active_polls(self, skip: int = 0, limit: int = 100) -> List[Poll]:
        active_polls = [
            poll for poll in self.polls.values()
            if not poll.is_closed
        ]
        return active_polls[skip:skip + limit]

    async def get_user_polls(self, user_id: int) -> List[Poll]:
        return [
            poll for poll in self.polls.values()
            if poll.creator_id == user_id
        ]

    async def update(self, poll: Poll) -> Poll:
        if poll.id not in self.polls:
            raise ValueError(f"Poll with ID {poll.id} not found")

        self.polls[poll.id] = poll
        return poll

    async def close_poll(self, poll_id: int) -> bool:
        if poll_id not in self.polls:
            return False

        self.polls[poll_id].is_closed = True
        return True

    async def close_expired_polls(self, current_time: datetime) -> int:
        closed_count = 0
        for poll in self.polls.values():
            if not poll.is_closed and poll.closes_at and poll.closes_at <= current_time:
                poll.is_closed = True
                closed_count += 1

        return closed_count


class MockVoteRepository(VoteRepository):
    """Mock implementation of vote repository for testing"""

    def __init__(self):
        self.votes = {}
        self.id_counter = 1
        self.user_poll_votes = {}  # key: (user_id, poll_id)

    async def create(self, vote: Vote) -> Vote:
        vote.id = self.id_counter
        self.id_counter += 1
        vote.created_at = datetime.now()

        self.votes[vote.id] = vote
        self.user_poll_votes[(vote.user_id, vote.poll_id)] = vote.id

        return vote

    async def get_by_id(self, vote_id: int) -> Optional[Vote]:
        return self.votes.get(vote_id)

    async def get_user_vote_for_poll(
        self, user_id: int, poll_id: int
    ) -> Optional[Vote]:
        vote_id = self.user_poll_votes.get((user_id, poll_id))
        if vote_id:
            return self.votes.get(vote_id)
        return None

    async def get_poll_results(self, poll_id: int) -> Dict[int, int]:
        results = {}
        for vote in self.votes.values():
            if vote.poll_id == poll_id:
                results[vote.option_id] = results.get(vote.option_id, 0) + 1

        return results

    async def update(self, vote: Vote) -> Vote:
        if vote.id not in self.votes:
            raise ValueError(f"Vote with ID {vote.id} not found")

        vote.updated_at = datetime.now()
        self.votes[vote.id] = vote
        return vote

    async def delete(self, vote_id: int) -> bool:
        if vote_id not in self.votes:
            return False

        vote = self.votes[vote_id]
        del self.user_poll_votes[(vote.user_id, vote.poll_id)]
        del self.votes[vote_id]

        return True


class TestUserRepository:
    @pytest.fixture
    def user_repo(self):
        return MockUserRepository()

    async def test_create_user(self, user_repo):
        user = User(username="testuser", email="test@example.com", hashed_password="hashed123")
        created_user = await user_repo.create(user)

        assert created_user.id is not None
        assert created_user.created_at is not None
        assert created_user.username == "testuser"
        assert created_user.email == "test@example.com"

    async def test_create_duplicate_email(self, user_repo):
        user1 = User(username="user1", email="same@example.com", hashed_password="hashed123")
        await user_repo.create(user1)

        user2 = User(username="user2", email="same@example.com", hashed_password="hashed123")
        with pytest.raises(ValueError):
            await user_repo.create(user2)

    async def test_create_duplicate_username(self, user_repo):
        user1 = User(username="sameuser", email="user1@example.com", hashed_password="hashed123")
        await user_repo.create(user1)

        user2 = User(username="sameuser", email="user2@example.com", hashed_password="hashed123")
        with pytest.raises(ValueError):
            await user_repo.create(user2)

    async def test_get_by_id(self, user_repo):
        user = User(username="testuser", email="test@example.com", hashed_password="hashed123")
        created_user = await user_repo.create(user)

        fetched_user = await user_repo.get_by_id(created_user.id)
        assert fetched_user is not None
        assert fetched_user.id == created_user.id
        assert fetched_user.username == "testuser"

    async def test_get_by_email(self, user_repo):
        user = User(username="testuser", email="test@example.com", hashed_password="hashed123")
        await user_repo.create(user)

        fetched_user = await user_repo.get_by_email("test@example.com")
        assert fetched_user is not None
        assert fetched_user.username == "testuser"

    async def test_get_by_username(self, user_repo):
        user = User(username="testuser", email="test@example.com", hashed_password="hashed123")
        await user_repo.create(user)

        fetched_user = await user_repo.get_by_username("testuser")
        assert fetched_user is not None
        assert fetched_user.email == "test@example.com"

    async def test_update_user(self, user_repo):
        user = User(username="oldname", email="old@example.com", hashed_password="hashed123")
        created_user = await user_repo.create(user)

        created_user.username = "newname"
        created_user.email = "new@example.com"

        updated_user = await user_repo.update(created_user)
        assert updated_user.username == "newname"
        assert updated_user.email == "new@example.com"

        # Check the mappings were updated
        fetched_by_new_username = await user_repo.get_by_username("newname")
        assert fetched_by_new_username is not None

        fetched_by_new_email = await user_repo.get_by_email("new@example.com")
        assert fetched_by_new_email is not None


class TestPollRepository:
    @pytest.fixture
    def poll_repo(self):
        return MockPollRepository()

    async def test_create_poll(self, poll_repo):
        options = [
            PollOption(text="Option 1", order=0),
            PollOption(text="Option 2", order=1)
        ]
        poll = Poll(
            creator_id=1,
            title="Test Poll",
            description="Test poll description",
            multiple_choices_allowed=False,
            options=options
        )

        created_poll = await poll_repo.create(poll)

        assert created_poll.id is not None
        assert created_poll.created_at is not None
        assert created_poll.title == "Test Poll"
        assert len(created_poll.options) == 2
        assert all(opt.id is not None for opt in created_poll.options)
        assert all(opt.poll_id == created_poll.id for opt in created_poll.options)

    async def test_get_by_id(self, poll_repo):
        poll = Poll(
            creator_id=1,
            title="Test Poll",
            description="Test poll description",
            options=[PollOption(text="Option 1")]
        )
        created_poll = await poll_repo.create(poll)

        fetched_poll = await poll_repo.get_by_id(created_poll.id)
        assert fetched_poll is not None
        assert fetched_poll.id == created_poll.id
        assert fetched_poll.title == "Test Poll"

    async def test_get_active_polls(self, poll_repo):
        # Create active polls
        for i in range(3):
            poll = Poll(
                creator_id=1,
                title=f"Active Poll {i}",
                options=[PollOption(text="Option")]
            )
            await poll_repo.create(poll)

        # Create closed poll
        closed_poll = Poll(
            creator_id=1,
            title="Closed Poll",
            is_closed=True,
            options=[PollOption(text="Option")]
        )
        await poll_repo.create(closed_poll)

        active_polls = await poll_repo.get_active_polls()
        assert len(active_polls) == 3
        assert all(not poll.is_closed for poll in active_polls)

    async def test_get_user_polls(self, poll_repo):
        # Create polls for user 1
        for i in range(2):
            poll = Poll(
                creator_id=1,
                title=f"User 1 Poll {i}",
                options=[PollOption(text="Option")]
            )
            await poll_repo.create(poll)

        # Create poll for user 2
        poll = Poll(
            creator_id=2,
            title="User 2 Poll",
            options=[PollOption(text="Option")]
        )
        await poll_repo.create(poll)

        user1_polls = await poll_repo.get_user_polls(1)
        assert len(user1_polls) == 2
        assert all(poll.creator_id == 1 for poll in user1_polls)

        user2_polls = await poll_repo.get_user_polls(2)
        assert len(user2_polls) == 1
        assert user2_polls[0].creator_id == 2

    async def test_close_poll(self, poll_repo):
        poll = Poll(
            creator_id=1,
            title="Test Poll",
            options=[PollOption(text="Option")]
        )
        created_poll = await poll_repo.create(poll)

        result = await poll_repo.close_poll(created_poll.id)
        assert result is True

        closed_poll = await poll_repo.get_by_id(created_poll.id)
        assert closed_poll.is_closed is True

    async def test_close_expired_polls(self, poll_repo):
        now = datetime.now()
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)

        # Create expired poll
        expired_poll = Poll(
            creator_id=1,
            title="Expired Poll",
            closes_at=past,
            options=[PollOption(text="Option")]
        )
        await poll_repo.create(expired_poll)

        # Create future poll
        future_poll = Poll(
            creator_id=1,
            title="Future Poll",
            closes_at=future,
            options=[PollOption(text="Option")]
        )
        await poll_repo.create(future_poll)

        # Create poll with no expiry
        no_expiry_poll = Poll(
            creator_id=1,
            title="No Expiry Poll",
            options=[PollOption(text="Option")]
        )
        await poll_repo.create(no_expiry_poll)

        closed_count = await poll_repo.close_expired_polls(now)
        assert closed_count == 1

        expired = await poll_repo.get_by_id(expired_poll.id)
        assert expired.is_closed is True

        future_p = await poll_repo.get_by_id(future_poll.id)
        assert future_p.is_closed is False

        no_expiry = await poll_repo.get_by_id(no_expiry_poll.id)
        assert no_expiry.is_closed is False


class TestVoteRepository:
    @pytest.fixture
    def vote_repo(self):
        return MockVoteRepository()

    async def test_create_vote(self, vote_repo):
        vote = Vote(user_id=1, poll_id=1, option_id=1)
        created_vote = await vote_repo.create(vote)

        assert created_vote.id is not None
        assert created_vote.created_at is not None
        assert created_vote.user_id == 1
        assert created_vote.poll_id == 1
        assert created_vote.option_id == 1

    async def test_get_by_id(self, vote_repo):
        vote = Vote(user_id=1, poll_id=1, option_id=1)
        created_vote = await vote_repo.create(vote)

        fetched_vote = await vote_repo.get_by_id(created_vote.id)
        assert fetched_vote is not None
        assert fetched_vote.id == created_vote.id
        assert fetched_vote.user_id == 1

    async def test_get_user_vote_for_poll(self, vote_repo):
        vote = Vote(user_id=1, poll_id=2, option_id=3)
        await vote_repo.create(vote)

        fetched_vote = await vote_repo.get_user_vote_for_poll(1, 2)
        assert fetched_vote is not None
        assert fetched_vote.user_id == 1
        assert fetched_vote.poll_id == 2
        assert fetched_vote.option_id == 3

        # Non-existent vote
        non_existent = await vote_repo.get_user_vote_for_poll(1, 999)
        assert non_existent is None

    async def test_get_poll_results(self, vote_repo):
        # Create votes for poll 1
        for i in range(3):
            await vote_repo.create(Vote(user_id=i, poll_id=1, option_id=1))  # 3 votes for option 1

        for i in range(3, 5):
            await vote_repo.create(Vote(user_id=i, poll_id=1, option_id=2))  # 2 votes for option 2

        # Create vote for a different poll
        await vote_repo.create(Vote(user_id=99, poll_id=2, option_id=1))

        results = await vote_repo.get_poll_results(1)
        assert results == {1: 3, 2: 2}

        # Poll with no votes
        empty_results = await vote_repo.get_poll_results(999)
        assert empty_results == {}

    async def test_update_vote(self, vote_repo):
        vote = Vote(user_id=1, poll_id=1, option_id=1)
        created_vote = await vote_repo.create(vote)

        # Change the option
        created_vote.option_id = 2
        updated_vote = await vote_repo.update(created_vote)

        assert updated_vote.option_id == 2
        assert updated_vote.updated_at is not None

    async def test_delete_vote(self, vote_repo):
        vote = Vote(user_id=1, poll_id=1, option_id=1)
        created_vote = await vote_repo.create(vote)

        result = await vote_repo.delete(created_vote.id)
        assert result is True

        deleted_vote = await vote_repo.get_by_id(created_vote.id)
        assert deleted_vote is None

        # Check user-poll mapping was removed
        no_vote = await vote_repo.get_user_vote_for_poll(1, 1)
        assert no_vote is None
