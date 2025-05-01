import requests
import time
import sys
import logging
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_server():
    base_url = "http://127.0.0.1:8000"
    
    logger.info("Testing server connection...")
    logger.info("Python version: %s", sys.version)
    logger.info("Current working directory: %s", sys.path[0])
    
    # Create a session with retry logic
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    
    # Configure session to not use proxy
    session.trust_env = False
    
    try:
        # Test root endpoint
        logger.info("Testing root endpoint...")
        response = session.get(
            f"{base_url}/",
            timeout=5,
            proxies={'http': None, 'https': None}
        )
        logger.info(f"Root endpoint response: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        # Test registration endpoint
        logger.info("Testing registration endpoint...")
        test_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
        response = session.post(
            f"{base_url}/auth/register",
            json=test_data,
            headers={"Accept": "application/json"},
            timeout=5,
            proxies={'http': None, 'https': None}
        )
        logger.info(f"Registration endpoint response: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        logger.error("Could not connect to the server. Make sure it's running.")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_server() 