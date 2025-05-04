import time
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from locust import HttpUser, task, tag, between


class VotingSystemUser(HttpUser):
    """
    A Locust user class that simulates real user behavior on the voting system.
    It performs common user actions like:
    - Registration and login
    - Creating polls
    - Voting in polls
    - Viewing poll results
    """

    # Wait time between tasks
    wait_time = between(1, 3)

    # User state
    access_token: Optional[str] = None
    username: Optional[str] = None
    password: str = "Password123!"
    created_polls: List[Dict] = []
    all_polls: List[Dict] = []

    def on_start(self):
        """
        Initialize the user by registering and logging in
        """
        self.register_and_login()

    def register_and_login(self):
        """
        Register a new user and then log in
        """
        # Create a unique username
        user_id = random.randint(1000, 9999999)
        self.username = f"loadtest_user_{user_id}"

        # Register user
        registration_data = {
            "username": self.username,
            "email": f"{self.username}@loadtest.com",
            "password": self.password
        }

        with self.client.post(
            "/auth/register",
            json=registration_data,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 400 and "already exists" in response.text:
                # User already exists, not a failure
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}, {response.text}")

        # Login
        login_data = {
            "username": self.username,
            "password": self.password
        }

        with self.client.post(
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}, {response.text}")

    def auth_headers(self) -> Dict[str, str]:
        """
        Return headers with authentication
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    @tag("view")
    @task(5)
    def view_all_polls(self):
        """
        View all available polls
        Weight: 5 - Common activity
        """
        start_time = time.time()
        with self.client.get(
            "/polls/",
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/ [GET] View all polls"
        ) as response:
            if response.status_code == 200:
                request_time = time.time() - start_time
                if request_time > 1.0:  # More than 1 second is slow
                    response.failure(f"Getting polls too slow: {request_time:.2f}s")
                else:
                    response.success()
                    self.all_polls = response.json()
            else:
                response.failure(f"Failed to get polls: {response.status_code}")

    @tag("create")
    @task(1)
    def create_poll(self):
        """
        Create a new poll
        Weight: 1 - Less common activity
        """
        poll_id = random.randint(10000, 9999999)
        poll_data = {
            "title": f"Load Test Poll {poll_id}",
            "description": f"This is a poll created during load testing {poll_id}",
            "options": [
                f"Option A {poll_id}",
                f"Option B {poll_id}",
                f"Option C {poll_id}"
            ],
            "multiple_choice": random.choice([True, False]),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat()
        }

        start_time = time.time()
        with self.client.post(
            "/polls/",
            json=poll_data,
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/ [POST] Create poll"
        ) as response:
            if response.status_code == 201:
                request_time = time.time() - start_time
                if request_time > 0.5:  # More than 0.5 second is slow for creation
                    response.failure(f"Poll creation too slow: {request_time:.2f}s")
                else:
                    response.success()
                    new_poll = response.json()
                    self.created_polls.append(new_poll)
            else:
                response.failure(f"Failed to create poll: {response.status_code}")

    @tag("view")
    @task(3)
    def view_specific_poll(self):
        """
        View a specific poll (either one created by this user or another)
        Weight: 3 - Common activity
        """
        # Get list of all polls if needed
        if not self.all_polls:
            self.view_all_polls()

        # Skip if no polls found
        if not self.all_polls:
            return

        # Choose a random poll
        poll = random.choice(self.all_polls)
        poll_id = poll["id"]

        start_time = time.time()
        with self.client.get(
            f"/polls/{poll_id}",
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/{id} [GET] View specific poll"
        ) as response:
            if response.status_code == 200:
                request_time = time.time() - start_time
                if request_time > 0.3:  # More than 0.3 second is slow
                    response.failure(f"Getting poll details too slow: {request_time:.2f}s")
                else:
                    response.success()
            else:
                response.failure(f"Failed to get poll details: {response.status_code}")

    @tag("vote")
    @task(2)
    def vote_in_poll(self):
        """
        Vote in a random poll
        Weight: 2 - Less common than viewing, more common than creating
        """
        # Get list of all polls if needed
        if not self.all_polls:
            self.view_all_polls()

        # Skip if no polls found
        if not self.all_polls:
            return

        # Choose a random poll that isn't closed
        open_polls = [p for p in self.all_polls if not p["is_closed"]]
        if not open_polls:
            return

        poll = random.choice(open_polls)
        poll_id = poll["id"]

        # Choose one or more options
        if poll["multiple_choice"]:
            # For multiple choice polls, select 1-3 options randomly
            num_options = min(len(poll["options"]), random.randint(1, 3))
            options = random.sample(poll["options"], num_options)
            option_ids = [opt["id"] for opt in options]
        else:
            # For single choice, just pick one
            option = random.choice(poll["options"])
            option_ids = [option["id"]]

        vote_data = {
            "option_ids": option_ids
        }

        start_time = time.time()
        with self.client.post(
            f"/polls/{poll_id}/vote",
            json=vote_data,
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/{id}/vote [POST] Vote in poll"
        ) as response:
            if response.status_code == 200:
                request_time = time.time() - start_time
                if request_time > 0.3:  # More than 0.3 second is slow for voting
                    response.failure(f"Voting too slow: {request_time:.2f}s")
                else:
                    response.success()
            elif response.status_code == 400 and "already closed" in response.text.lower():
                # Poll was closed between when we checked and when we tried to vote
                # This is a legitimate race condition, not a failure
                response.success()
            else:
                response.failure(f"Failed to vote: {response.status_code}, {response.text}")

    @tag("manage")
    @task(1)
    def update_own_poll(self):
        """
        Update one of the user's own polls
        Weight: 1 - Less common activity
        """
        # Skip if no polls created
        if not self.created_polls:
            return

        # Choose a random poll created by this user
        poll = random.choice(self.created_polls)
        poll_id = poll["id"]

        # Prepare update data
        update_data = {
            "title": f"Updated: {poll['title']}",
            "description": f"Updated: {poll['description']}"
        }

        with self.client.patch(
            f"/polls/{poll_id}",
            json=update_data,
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/{id} [PATCH] Update poll"
        ) as response:
            if response.status_code == 200:
                response.success()
                # Update our local copy
                poll["title"] = update_data["title"]
                poll["description"] = update_data["description"]
            else:
                response.failure(f"Failed to update poll: {response.status_code}")

    @tag("manage")
    @task(1)
    def close_own_poll(self):
        """
        Close one of the user's own polls
        Weight: 1 - Least common activity
        """
        # Skip if no polls created
        if not self.created_polls:
            return

        # Choose a random poll that's not already closed
        open_polls = [p for p in self.created_polls if not p["is_closed"]]
        if not open_polls:
            return

        poll = random.choice(open_polls)
        poll_id = poll["id"]

        with self.client.post(
            f"/polls/{poll_id}/close",
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/{id}/close [POST] Close poll"
        ) as response:
            if response.status_code == 200:
                response.success()
                # Update our local copy
                poll["is_closed"] = True
            else:
                response.failure(f"Failed to close poll: {response.status_code}")

    @tag("view")
    @task(4)
    def view_own_polls(self):
        """
        View the user's own created polls
        Weight: 4 - Common activity
        """
        with self.client.get(
            "/polls/me",
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/me [GET] View own polls"
        ) as response:
            if response.status_code == 200:
                response.success()
                # Update our list of created polls
                self.created_polls = response.json()
            else:
                response.failure(f"Failed to get own polls: {response.status_code}")

    @tag("view")
    @task(2)
    def view_user_profile(self):
        """
        View user's own profile
        Weight: 2 - Moderately common
        """
        with self.client.get(
            "/auth/me",
            headers=self.auth_headers(),
            catch_response=True,
            name="/auth/me [GET] View user profile"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get user profile: {response.status_code}")
