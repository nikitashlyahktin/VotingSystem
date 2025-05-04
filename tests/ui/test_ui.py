# import pytest
# import time
# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.edge.options import Options
# from selenium.webdriver.edge.service import Service
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# import platform

# # Mark all tests in this module as UI tests
# pytestmark = pytest.mark.ui


# class TestUI:
#     """Test suite for UI testing with Selenium"""

#     @pytest.fixture(scope="class")
#     def browser(self):
#         """Fixture for browser setup"""
#         edge_options = Options()

#         # Better configuration for Edge headless mode
#         if platform.system() == "Windows":
#             # Different headless approach for Windows
#             edge_options.use_chromium = True
#             edge_options.add_argument("--headless=new")
#         else:
#             edge_options.add_argument("--headless")

#         # Common options
#         edge_options.add_argument("--no-sandbox")
#         edge_options.add_argument("--disable-dev-shm-usage")
#         edge_options.add_argument("--disable-gpu")
#         edge_options.add_argument("--disable-extensions")
#         edge_options.add_argument("--disable-notifications")
#         edge_options.add_argument("--disable-infobars")
#         edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         edge_options.add_experimental_option("useAutomationExtension", False)

#         try:
#             # Setup Edge WebDriver
#             service = Service(EdgeChromiumDriverManager().install())
#             driver = webdriver.Edge(service=service, options=edge_options)
#             driver.maximize_window()

#             # Set page load timeout
#             driver.set_page_load_timeout(30)

#             yield driver

#         except Exception as e:
#             pytest.fail(f"Failed to initialize Edge WebDriver: {str(e)}")
#         finally:
#             # Cleanup
#             try:
#                 driver.quit()
#             except BaseException:
#                 pass

#     @pytest.fixture(scope="class")
#     def base_url(self):
#         """Base URL for frontend tests"""
#         # Get from environment or use default
#         return os.environ.get("FRONTEND_URL", "http://localhost:8501")

#     def test_home_page_loads(self, browser, base_url):
#         """Test that the home page loads successfully"""
#         try:
#             browser.get(base_url)

#             # Wait for page to load (Streamlit app should have the title)
#             WebDriverWait(browser, 20).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "h1"))
#             )

#             # If title check is causing issues, focus on page content instead
#             page_source = browser.page_source
#             assert "Voting System" in page_source or "Welcome" in page_source

#         except TimeoutException:
#             pytest.fail(f"Home page failed to load within timeout. URL: {base_url}")
#         except Exception as e:
#             pytest.fail(f"Error loading home page: {str(e)}")

#     def test_login_form_visible(self, browser, base_url):
#         """Test that the login form is visible"""
#         browser.get(base_url)

#         # Wait for the login form to appear
#         try:
#             # First look for the login section
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[contains(text(), 'Login') or contains(text(), 'Sign In')]")))

#             # Then check for username/email and password fields
#             username_field = browser.find_element(
#                 By.XPATH, "//input[@type='text' or @aria-label='Username']")
#             password_field = browser.find_element(
#                 By.XPATH, "//input[@type='password' or @aria-label='Password']")

#             assert username_field.is_displayed()
#             assert password_field.is_displayed()

#         except TimeoutException:
#             pytest.fail("Login form not found within timeout")
#         except Exception as e:
#             pytest.fail(f"Error finding login form: {str(e)}")

#     def test_register_flow(self, browser, base_url):
#         """Test user registration flow"""
#         browser.get(base_url)

#         try:
#             # Find and click "Register" or "Sign Up" link/button
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//button[contains(text(), 'Register') or contains(text(), 'Sign Up')]"))).click()

#             # Wait for registration form
#             WebDriverWait(browser, 10).until(EC.presence_of_element_located(
#                 (By.XPATH, "//div[contains(text(), 'Register') or contains(text(), 'Sign Up')]")))

#             # Fill in registration details
#             username = f"selenium_test_{int(time.time())}"
#             email = f"{username}@example.com"
#             password = "SeleniumTest123!"

#             # Find and fill out the registration form
#             username_field = browser.find_element(
#                 By.XPATH, "//input[@aria-label='Username' or @placeholder='Username']")
#             email_field = browser.find_element(
#                 By.XPATH, "//input[@aria-label='Email' or @placeholder='Email']")
#             password_field = browser.find_element(By.XPATH, "//input[@type='password']")

#             username_field.send_keys(username)
#             email_field.send_keys(email)
#             password_field.send_keys(password)

#             # Submit registration form
#             submit_button = browser.find_element(
#                 By.XPATH,
#                 "//button[contains(text(), 'Register') or contains(text(), 'Sign Up') or contains(text(), 'Submit')]")
#             submit_button.click()

#             # Wait for successful registration notification or redirect
#             WebDriverWait(
#                 browser,
#                 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH,
#                      "//div[contains(text(), 'Registration successful') or contains(text(), 'Account created')]")))

#             assert True  # If we get here, the test passes

#         except TimeoutException:
#             pytest.fail("Registration form or confirmation not found within timeout")
#         except Exception as e:
#             pytest.fail(f"Error during registration flow: {str(e)}")

#     def test_login_flow(self, browser, base_url):
#         """Test user login flow"""
#         browser.get(base_url)

#         try:
#             # Wait for the login form
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[contains(text(), 'Login') or contains(text(), 'Sign In')]")))

#             # Use pre-created test account for login
#             username = "testuser"  # Should match fixture in conftest.py
#             password = "password123"

#             # Find and fill out login form
#             username_field = browser.find_element(
#                 By.XPATH, "//input[@type='text' or @aria-label='Username']")
#             password_field = browser.find_element(
#                 By.XPATH, "//input[@type='password' or @aria-label='Password']")

#             username_field.send_keys(username)
#             password_field.send_keys(password)

#             # Submit login form
#             submit_button = browser.find_element(
#                 By.XPATH,
#                 "//button[contains(text(), 'Login') or contains(text(), 'Sign In') or contains(text(), 'Submit')]")
#             submit_button.click()

#             # Wait for successful login (look for dashboard or polls list)
#             WebDriverWait(browser, 10).until(EC.presence_of_element_located(
#                 (By.XPATH, "//div[contains(text(), 'Polls') or contains(text(), 'Dashboard')]")))

#             # Verify login success
#             page_source = browser.page_source
#             assert username in page_source  # Username should appear somewhere after login

#         except TimeoutException:
#             pytest.fail("Login form or dashboard not found within timeout")
#         except Exception as e:
#             pytest.fail(f"Error during login flow: {str(e)}")

#     def test_create_poll_flow(self, browser, base_url):
#         """Test poll creation flow (requires login)"""
#         # First login
#         self.test_login_flow(browser, base_url)

#         try:
#             # Find and click "Create Poll" button/link
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//button[contains(text(), 'Create Poll') or contains(text(), 'New Poll')]"))).click()

#             # Wait for poll creation form
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[contains(text(), 'Create Poll') or contains(text(), 'New Poll')]")))

#             # Fill in poll details
#             poll_title = f"Selenium Test Poll {int(time.time())}"
#             poll_description = "This is a poll created by Selenium test"

#             # Fill out the form
#             title_field = browser.find_element(
#                 By.XPATH, "//input[@aria-label='Title' or @placeholder='Title']")
#             description_field = browser.find_element(
#                 By.XPATH, "//textarea[@aria-label='Description' or @placeholder='Description']")

#             title_field.send_keys(poll_title)
#             description_field.send_keys(poll_description)

#             # Add options (assuming there are at least 2 option fields)
#             option_fields = browser.find_elements(
#                 By.XPATH, "//input[contains(@aria-label, 'Option') or contains(@placeholder, 'Option')]")
#             if len(option_fields) >= 2:
#                 option_fields[0].send_keys("Option 1")
#                 option_fields[1].send_keys("Option 2")
#             else:
#                 # If options UI is different, try to find by index or other means
#                 option1 = browser.find_element(
#                     By.XPATH, "(//input[not(@type='password') and not(@type='checkbox')])[3]")
#                 option2 = browser.find_element(
#                     By.XPATH, "(//input[not(@type='password') and not(@type='checkbox')])[4]")
#                 option1.send_keys("Option 1")
#                 option2.send_keys("Option 2")

#             # Submit the form
#             submit_button = browser.find_element(
#                 By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Submit')]")
#             submit_button.click()

#             # Wait for confirmation or redirect to polls list
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[contains(text(), 'Poll created') or contains(text(), 'Success')]")))

#             # Verify poll was created by checking it appears in the list
#             assert poll_title in browser.page_source

#         except TimeoutException:
#             pytest.fail("Poll creation form or confirmation not found within timeout")
#         except Exception as e:
#             pytest.fail(f"Error during poll creation: {str(e)}")

#     def test_vote_in_poll(self, browser, base_url):
#         """Test voting in a poll (requires login)"""
#         # First login if not already logged in
#         if "Polls" not in browser.page_source and "Dashboard" not in browser.page_source:
#             self.test_login_flow(browser, base_url)

#         try:
#             # Find and click on a poll to vote in
#             # This assumes there's at least one poll available
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//div[contains(@class, 'poll') or contains(@class, 'card')]//a"))).click()

#             # Wait for poll details to load
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[contains(text(), 'Options') or contains(text(), 'Vote')]")))

#             # Select an option (choose the first one)
#             option_selector = browser.find_element(
#                 By.XPATH, "//input[@type='radio' or @type='checkbox']")
#             option_selector.click()

#             # Click vote button
#             vote_button = browser.find_element(
#                 By.XPATH, "//button[contains(text(), 'Vote') or contains(text(), 'Submit')]")
#             vote_button.click()

#             # Wait for vote confirmation
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[contains(text(), 'Vote recorded') or contains(text(), 'Success')]")))

#             # Verify vote was recorded
#             assert "Vote recorded" in browser.page_source or "Success" in browser.page_source

#         except TimeoutException:
#             pytest.fail("Poll details or vote confirmation not found within timeout")
#         except Exception as e:
#             pytest.fail(f"Error during voting: {str(e)}")

#     def test_logout_flow(self, browser, base_url):
#         """Test user logout flow"""
#         # First login if not already logged in
#         if "Polls" not in browser.page_source and "Dashboard" not in browser.page_source:
#             self.test_login_flow(browser, base_url)

#         try:
#             # Find and click logout button/link
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//button[contains(text(), 'Logout') or contains(text(), 'Sign Out')]"))).click()

#             # Wait for confirmation of logout or return to login page
#             WebDriverWait(
#                 browser, 10).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[contains(text(), 'Login') or contains(text(), 'Sign In')]")))

#             # Verify we're logged out by checking login form is visible
#             assert "Login" in browser.page_source or "Sign In" in browser.page_source

#         except TimeoutException:
#             pytest.fail("Logout button or login page not found within timeout")
#         except Exception as e:
#             pytest.fail(f"Error during logout flow: {str(e)}")
