import time

import streamlit as st
import requests
from datetime import datetime, timedelta

# API configuration
API_URL = "http://127.0.0.1:8000"

# Configure requests session
session = requests.Session()
session.trust_env = False  # Disable proxy settings


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if not st.session_state.token:
        st.session_state.num_options = 2


def login(email: str, password: str) -> bool:
    """Authenticate user with provided credentials.
    Returns True if login successful, False otherwise.
    """
    try:
        # Create the request data
        request_data = {
            "username": email,
            "password": password
        }

        # Try to make the request
        try:
            # Make the login request
            response = session.post(
                f"{API_URL}/auth/login",
                data=request_data,  # Using data instead of json for form data
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                timeout=5,
                proxies={'http': None, 'https': None}
            )
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return False

        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            # Get user info
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            user_response = session.get(
                f"{API_URL}/users/me",
                headers=headers,
                proxies={'http': None, 'https': None}
            )

            if user_response.status_code == 200:
                st.session_state.user = user_response.json()
                st.success("Login successful!")
                return True
            else:
                st.error("Failed to get user information after login")
                return False
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"Login failed: {error_detail}")
            except ValueError:
                st.error(f"Login failed with status code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error during login: {str(e)}")
        return False


def register(email: str, username: str, password: str) -> bool:
    """Register a new user account.
    Returns True if registration successful, False otherwise.
    """
    try:
        # Validate input
        if len(username) < 3 or len(username) > 50:
            st.error("Username must be between 3 and 50 characters")
            return False

        if len(password) < 8:
            st.error("Password must be at least 8 characters")
            return False

        # Create the request data with proper JSON formatting
        request_data = {
            "email": email,
            "username": username,
            "password": password
        }

        # Try to make the request
        try:
            # Make the registration request
            response = session.post(
                f"{API_URL}/auth/register",
                json=request_data,
                headers={"Accept": "application/json"},
                timeout=5,
                proxies={'http': None, 'https': None}
            )
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return False

        if response.status_code == 201:
            st.success("Registration successful! Please login.")
            time.sleep(3)
            return True
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"Registration failed: {error_detail}")
            except ValueError:
                st.error(f"Registration failed with status code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error during registration: {str(e)}")
        return False


def create_poll(title: str, description: str, options: list, is_multiple_choice: bool, closing_date: datetime = None):
    """Create a new poll with the provided details.
    Returns True if poll created successfully, False otherwise.
    """
    try:
        # Create the request data
        data = {
            "title": title,
            "description": description,
            "options": [{"text": opt} for opt in options if opt],
            "is_multiple_choice": is_multiple_choice,
            "closing_date": closing_date.isoformat() if closing_date else None
        }

        # Make the request
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = session.post(
                f"{API_URL}/polls/",
                json=data,
                headers=headers,
                timeout=5,
                proxies={'http': None, 'https': None}
            )

            if response.status_code == 201:
                st.success("Poll created successfully! Refreshing the page...")
                return True
            else:
                try:
                    error_detail = response.json().get("detail")[0]['msg']
                    st.error(error_detail)
                except ValueError:
                    st.error(f"Failed to create poll with status code: {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return False
    except Exception as e:
        st.error(f"Error creating poll: {str(e)}")
        return False


def close_poll(poll_id: int):
    """Close an active poll.
    Returns True if poll closed successfully, False otherwise.
    """
    try:
        # Create the request data
        data = {
            "poll_id": poll_id
        }

        # Make the request
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = session.post(
                f"{API_URL}/polls/{poll_id}/close",
                json=data,
                headers=headers,
                timeout=5,
                proxies={'http': None, 'https': None}
            )

            if response.status_code == 200:
                st.success("Poll closed successfully! Refreshing the page...")
                return True
            else:
                try:
                    st.error(response.json())
                    error_detail = response.json().get("detail")[0]['msg']
                    st.error(error_detail)
                except ValueError:
                    st.error(f"Failed to close the poll with status code: {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return False
    except Exception as e:
        st.error(f"Error closing poll: {str(e)}")
        return False


def get_my_id():
    """Get the current user's ID.
    Returns user ID or False if request fails.
    """
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = session.get(
                f"{API_URL}/users/me",
                headers=headers,
                timeout=5,
                proxies={'http': None, 'https': None}
            )

            if response.status_code == 200:
                return response.json().get('id')
            else:
                st.error(f"Getting information about the current user error: {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return False
    except Exception as e:
        st.error(f"Error closing poll: {str(e)}")
        return False


def vote_in_poll(poll_id: int, option_ids: list):
    """Submit a vote for selected option(s) in a poll.
    Returns True if vote recorded successfully, False otherwise.
    """
    try:
        # Create the request data
        data = {
            "poll_id": poll_id,
            "option_ids": option_ids
        }

        # Make the request
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = session.post(
                f"{API_URL}/polls/{poll_id}/vote",
                json=data,
                headers=headers,
                timeout=5,
                proxies={'http': None, 'https': None}
            )

            if response.status_code == 200:
                st.success("Vote recorded successfully!")
                return True
            else:
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"Failed to record vote: {error_detail}")
                except ValueError:
                    st.error(f"Failed to record vote with status code: {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return False
    except Exception as e:
        st.error(f"Error voting: {str(e)}")
        return False


def get_polls():
    """Fetch all available polls.
    Returns list of polls or empty list if request fails.
    """
    try:
        data = {
            "limit": 1_000_000  # Fetch a large number of polls
        }
        # Make the request
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Accept": "application/json"
        }

        try:
            response = session.get(
                f"{API_URL}/polls/",
                params=data,
                headers=headers,
                timeout=5,
                proxies={'http': None, 'https': None}
            )

            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"Failed to fetch polls: {error_detail}")
                except ValueError:
                    st.error(f"Failed to fetch polls with status code: {response.status_code}")
                return []
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return []
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return []
    except Exception as e:
        st.error(f"Error fetching polls: {str(e)}")
        return []


def get_poll_results(poll_id: int):
    """Fetch results for a specific poll.
    Returns poll results or None if request fails.
    """
    try:
        # Make the request
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Accept": "application/json"
        }

        try:
            response = session.get(
                f"{API_URL}/polls/{poll_id}/results",
                headers=headers,
                timeout=5,
                proxies={'http': None, 'https': None}
            )

            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"Failed to fetch poll results: {error_detail}")
                except ValueError:
                    st.error(f"Failed to fetch poll results with status code: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            st.error("Request timed out. The server might be down or not responding.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error fetching poll results: {str(e)}")
        return None


def main():
    """Main application function that sets up the Streamlit UI."""
    st.title("Voting System")
    init_session_state()

    # Sidebar for authentication
    with st.sidebar:
        if st.session_state.token is None:
            st.subheader("Login")
            login_tab, register_tab = st.tabs(["Login", "Register"])

            with login_tab:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                if st.button("Login"):
                    if login(email, password):
                        st.rerun()

            with register_tab:
                reg_email = st.text_input("Email", key="reg_email")
                reg_username = st.text_input("Username", key="reg_username")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                if st.button("Register"):
                    if register(reg_email, reg_username, reg_password):
                        st.rerun()
        else:
            st.write(f"Welcome, {st.session_state.user['username']}!")
            if st.button("Logout"):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()

    # Main content
    if st.session_state.token:
        tab1, tab2, tab3 = st.tabs(["Available Polls", "Create Poll", "Poll Results"])

        with tab1:
            st.subheader("Available Polls")
            polls = get_polls()
            if polls:
                for poll in polls:
                    with st.expander(f"{poll['title']}"):
                        st.write(f"Description: {poll['description']}")
                        st.write(f"Multiple choice: {'Yes' if poll['is_multiple_choice'] else 'No'}")
                        if poll['closing_date']:
                            st.write(f"Closes at: {poll['closing_date']}")

                        if poll['is_active']:
                            options = poll['options']
                            # For multiple choice polls, use multiselect
                            if poll['is_multiple_choice']:
                                selected_options = st.multiselect(
                                    "Choose options:",
                                    options=[(opt['id'], opt['text']) for opt in options],
                                    format_func=lambda x: x[1]
                                )
                                selected_ids = [opt[0] for opt in selected_options]
                            # For single choice polls, use selectbox
                            else:
                                option = st.selectbox(
                                    "Choose an option:",
                                    options=[(opt['id'], opt['text']) for opt in options],
                                    format_func=lambda x: x[1],
                                    key=poll['id']
                                )
                                selected_ids = [option[0]] if option else []

                            if st.button("Vote", key=f"vote_{poll['id']}", type='secondary'):
                                if selected_ids:
                                    vote_in_poll(poll['id'], selected_ids)
                                else:
                                    st.warning("Please select at least one option")
                            # Only poll creator can close the poll
                            if get_my_id() == poll['creator_id']:
                                if st.button('Close poll', key=f'close_poll_{poll["id"]}', type='primary'):
                                    close_poll(poll['id'])
                                    time.sleep(3)
                                    st.rerun()
                        else:
                            st.warning("This poll is closed")
            else:
                st.info("No polls available. Create one to get started!")

        with tab2:
            st.subheader("Create New Poll")
            title = st.text_input("Poll Title")
            description = st.text_area("Poll Description")
            is_multiple_choice = st.checkbox("Allow Multiple Choices")

            # Dynamic poll options
            options = []
            for i in range(st.session_state.num_options):
                option = st.text_input(f"Option {i + 1}", key=f"option_{i}")
                if option:
                    options.append(option)
            if st.button('➕ Add Option'):
                st.session_state.num_options += 1
                st.rerun()

            # Optional closing date setup
            use_closing_date = st.checkbox("Set Closing Date")
            closing_date = None
            if use_closing_date:
                closing_date = st.date_input(
                    "Closing Date",
                    min_value=datetime.now().date(),
                    value=datetime.now().date() + timedelta(days=1)
                )
                closing_time = st.time_input("Closing Time", value=datetime.now())
                if closing_date and closing_time:
                    closing_date = datetime.combine(closing_date, closing_time)

            if st.button("Create Poll"):
                if len(options) < 2:
                    st.error("Please add at least 2 options")
                else:
                    if create_poll(title, description, options, is_multiple_choice, closing_date):
                        time.sleep(3)
                        st.rerun()

        with tab3:
            st.subheader("Poll Results")
            polls = get_polls()
            if polls:
                selected_poll = st.selectbox(
                    "Select a poll to view results:",
                    options=[(poll['id'], poll['title']) for poll in polls],
                    format_func=lambda x: x[1]
                )
                if selected_poll:
                    poll_id = selected_poll[0]
                    results = get_poll_results(poll_id)
                    if results:
                        st.write("### Results")
                        total_votes = results['total_votes']
                        if total_votes > 0:
                            # Display results with progress bars
                            poll = next((p for p in polls if p['id'] == poll_id), None)
                            if poll:
                                for option in poll['options']:
                                    option_id = option['id']
                                    vote_count = results['results'].get(str(option_id), 0)
                                    percentage = (vote_count / total_votes) * 100 if total_votes > 0 else 0
                                    st.write(f"**{option['text']}**: {vote_count} votes ({percentage:.1f}%)")
                                    st.progress(percentage / 100)
                        else:
                            st.info("No votes have been cast yet")
            else:
                st.info("No polls available to show results")


if __name__ == "__main__":
    main()
