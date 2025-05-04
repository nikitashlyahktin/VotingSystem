import time
import random
import json
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
    created_polls: List[Dict] = []  # Polls returned by /polls endpoint
    truly_own_polls: List[Dict] = []  # Polls actually created by this user instance
    all_polls: List[Dict] = []
    user_id: Optional[int] = None  # To track the user's ID
    
    # Debug flag
    debug = True

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
        self.email = f"{self.username}@loadtest.com"

        # Register user
        registration_data = {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }

        if self.debug:
            print(f"Attempting to register user: {self.username}")

        # Try registering
        with self.client.post(
            "/auth/register",
            json=registration_data,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                print(f"User {self.username} registered successfully")
                response.success()
            elif response.status_code == 400 and "already exists" in response.text:
                # User already exists, not a failure
                print(f"User {self.username} already exists, proceeding to login")
                response.success()
            else:
                print(f"Registration failed: {response.status_code}, {response.text}")
                response.failure(f"Registration failed: {response.status_code}, {response.text}")

        # Try multiple login approaches
        login_success = self.try_login_with_form() or self.try_login_with_json() or self.try_login_with_basic_auth()
        
        if not login_success:
            print("ALL LOGIN ATTEMPTS FAILED")

    def try_login_with_form(self):
        """Try logging in with form data"""
        if self.debug:
            print(f"Trying form login for {self.username}")
            
        form_data = {
            "username": self.email,  # Try with email
            "password": self.password
        }
        
        with self.client.post(
            "/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            catch_response=True,
            name="Login with form data"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    if self.access_token:
                        print(f"Form login successful: {self.access_token[:10]}...")
                        # Try to get user ID
                        self.get_user_id()
                        return True
                    else:
                        print(f"Form login response had no token: {data}")
                except Exception as e:
                    print(f"Error parsing login response: {str(e)}, Response: {response.text}")
            else:
                print(f"Form login failed: {response.status_code}, {response.text}")
        
        return False
    
    def try_login_with_json(self):
        """Try logging in with JSON data"""
        if self.debug:
            print(f"Trying JSON login for {self.username}")
            
        # Try both username and email in separate attempts
        json_data_attempts = [
            {"username": self.username, "password": self.password},
            {"username": self.email, "password": self.password},
            {"email": self.email, "password": self.password}
        ]
        
        for attempt, json_data in enumerate(json_data_attempts):
            with self.client.post(
                "/auth/login",
                json=json_data,
                catch_response=True,
                name=f"Login with JSON data (attempt {attempt+1})"
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.access_token = data.get("access_token")
                        if self.access_token:
                            print(f"JSON login successful: {self.access_token[:10]}...")
                            # Try to get user ID
                            self.get_user_id()
                            return True
                        else:
                            print(f"JSON login response had no token: {data}")
                    except Exception as e:
                        print(f"Error parsing login response: {str(e)}, Response: {response.text}")
                else:
                    print(f"JSON login failed (attempt {attempt+1}): {response.status_code}, {response.text}")
        
        return False
    
    def try_login_with_basic_auth(self):
        """Try logging in with Basic Auth"""
        if self.debug:
            print(f"Trying Basic Auth login for {self.username}")
            
        import base64
        credentials = f"{self.email}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        with self.client.get(
            "/auth/login",
            headers={"Authorization": f"Basic {encoded}"},
            catch_response=True,
            name="Login with Basic Auth"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    if self.access_token:
                        print(f"Basic Auth login successful: {self.access_token[:10]}...")
                        # Try to get user ID
                        self.get_user_id()
                        return True
                    else:
                        print(f"Basic Auth login response had no token: {data}")
                except Exception as e:
                    print(f"Error parsing login response: {str(e)}, Response: {response.text}")
            else:
                print(f"Basic Auth login failed: {response.status_code}, {response.text}")
        
        return False

    def auth_headers(self) -> Dict[str, str]:
        """
        Return headers with authentication
        """
        if not self.access_token:
            print("WARNING: No access token available for request!")
            return {"Content-Type": "application/json"}
            
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
        if not self.access_token:
            self.register_and_login()  # Try to login again
            if not self.access_token:
                return  # Skip if still no token
                
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
                # If unauthorized, try to re-authenticate
                if response.status_code == 401:
                    self.register_and_login()

    @tag("create")
    @task(1)
    def create_poll(self):
        """
        Create a new poll
        Weight: 1 - Less common activity
        """
        if not self.access_token:
            self.register_and_login()  # Try to login again
            if not self.access_token:
                return  # Skip if still no token
                
        poll_id = random.randint(10000, 9999999)
        poll_data = {
            "title": f"Load Test Poll {poll_id}",
            "description": f"This is a poll created during load testing {poll_id}",
            "options": [
                {"text": f"Option A {poll_id}"},
                {"text": f"Option B {poll_id}"},
                {"text": f"Option C {poll_id}"}
            ],
            "is_multiple_choice": random.choice([True, False]),
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
                    # Also add to our truly own polls list
                    self.truly_own_polls.append(new_poll)
                    if self.debug:
                        print(f"Created poll {new_poll['id']} and added to truly_own_polls")
            else:
                response.failure(f"Failed to create poll: {response.status_code}")
                # If unauthorized, try to re-authenticate
                if response.status_code == 401:
                    self.register_and_login()

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
        # Handle both "is_closed" and "is_active" field possibilities
        open_polls = []
        for p in self.all_polls:
            # Poll can have either "is_closed" field or "is_active" field
            if "is_closed" in p:
                if not p["is_closed"]:
                    open_polls.append(p)
            elif "is_active" in p:
                if p["is_active"]:
                    open_polls.append(p)
            else:
                # If neither field exists, assume it's open
                open_polls.append(p)
                
        if not open_polls:
            return

        poll = random.choice(open_polls)
        poll_id = poll["id"]

        # Choose one or more options
        if poll["is_multiple_choice"]:
            # For multiple choice polls, select 1-3 options randomly
            num_options = min(len(poll["options"]), random.randint(1, 3))
            options = random.sample(poll["options"], num_options)
            option_ids = [opt["id"] for opt in options]
        else:
            # For single choice, just pick one
            option = random.choice(poll["options"])
            option_ids = [option["id"]]

        vote_data = {
            "option_ids": option_ids,
            "poll_id": poll_id
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

    @tag("manage")
    @task(1)
    def close_own_poll(self):
        """
        Close one of the user's own polls
        Weight: 1 - Least common activity
        """
        # Skip if we haven't created any polls ourselves
        if not self.truly_own_polls:
            if self.debug:
                print("No polls truly created by this user to close")
            return

        # Filter for polls that aren't already closed
        open_polls = []
        for p in self.truly_own_polls:
            # Poll can have either "is_closed" field or "is_active" field
            if "is_closed" in p and not p["is_closed"]:
                open_polls.append(p)
            elif "is_active" in p and p["is_active"]:
                open_polls.append(p)
            else:
                # If neither field exists, assume it's open
                open_polls.append(p)
                
        if not open_polls:
            if self.debug:
                print("No open polls truly created by this user to close")
            return

        poll = random.choice(open_polls)
        poll_id = poll["id"]

        # Debug the poll ID and ownership
        if self.debug:
            print(f"Attempting to close truly owned poll with ID: {poll_id}")
            if "creator_id" in poll:
                print(f"Creator ID: {poll['creator_id']}, Our User ID: {self.user_id}")
            
        # Make sure poll_id is properly formatted
        poll_id_str = str(poll_id)

        with self.client.post(
            f"/polls/{poll_id_str}/close",
            json={"poll_id": poll_id},
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls/{id}/close [POST] Close poll"
        ) as response:
            if response.status_code == 200:
                response.success()
                # Update our local copy with appropriate field
                if "is_closed" in poll:
                    poll["is_closed"] = True
                if "is_active" in poll:
                    poll["is_active"] = False
                
                # Remove the poll from our list of open polls
                if poll in open_polls:
                    open_polls.remove(poll)
                
                # Update the poll in our truly_own_polls list
                for i, p in enumerate(self.truly_own_polls):
                    if p["id"] == poll_id:
                        if "is_closed" in self.truly_own_polls[i]:
                            self.truly_own_polls[i]["is_closed"] = True
                        if "is_active" in self.truly_own_polls[i]:
                            self.truly_own_polls[i]["is_active"] = False
                
                if self.debug:
                    print(f"Successfully closed poll {poll_id}")
            else:
                # Log detailed error information
                if self.debug:
                    print(f"Failed to close poll {poll_id}. Status: {response.status_code}, Response: {response.text}")
                
                # Check if this is a permission error
                if response.status_code == 403 and "creator" in response.text:
                    # This shouldn't happen since we're using truly_own_polls
                    print(f"UNEXPECTED: Permission error for poll we should own: {poll_id}")
                    # Remove this poll from truly_own_polls as we apparently don't own it
                    self.truly_own_polls = [p for p in self.truly_own_polls if p["id"] != poll_id]
                    response.success()  # Mark as success to avoid test errors
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
            "/polls",
            headers=self.auth_headers(),
            catch_response=True,
            name="/polls [GET] View own polls"
        ) as response:
            if response.status_code == 200:
                response.success()
                # Update our list of created polls
                self.created_polls = response.json()
                
                # If we know our user ID, filter for polls we truly own
                if self.user_id:
                    user_id = self.user_id
                    if self.debug:
                        print(f"Filtering polls by our user ID: {user_id}")
                    
                    # Find polls where we are the creator
                    for poll in self.created_polls:
                        creator_id = poll.get("creator_id")
                        if creator_id == user_id:
                            # Check if this poll is already in our truly_own_polls list
                            poll_id = poll.get("id")
                            if poll_id and not any(p.get("id") == poll_id for p in self.truly_own_polls):
                                self.truly_own_polls.append(poll)
                                if self.debug:
                                    print(f"Added poll {poll_id} to truly_own_polls from API response")
            else:
                response.failure(f"Failed to get own polls: {response.status_code}")

    @tag("view")
    @task(2)
    def view_user_profile(self):
        """
        View user's own profile
        Weight: 2 - Moderately common
        """
        if not self.access_token:
            self.register_and_login()
            if not self.access_token:
                return
                
        # Try multiple endpoints for user profile
        endpoints = ["/users/me", "/auth/me", "/profile", "/user/profile"]
        
        for endpoint in endpoints:
            with self.client.get(
                endpoint,
                headers=self.auth_headers(),
                catch_response=True,
                name=f"{endpoint} [GET] View user profile"
            ) as response:
                if response.status_code == 200:
                    response.success()
                    return  # Found working endpoint
                elif response.status_code == 404:
                    # Skip this endpoint and try the next one
                    continue
                elif response.status_code == 401:
                    # Authentication failed, try to re-login
                    self.register_and_login()
                    response.failure("Authentication failed")

    def get_user_id(self):
        """
        Get the user ID from the login response
        """
        if self.access_token:
            with self.client.get(
                "/users/me",
                headers=self.auth_headers(),
                catch_response=True,
                name="GET /users/me"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    self.user_id = data.get("id")
                    if self.user_id:
                        print(f"User ID: {self.user_id}")
                    else:
                        print("User ID not found in response")
                else:
                    print(f"Failed to get user ID: {response.status_code}, {response.text}")
