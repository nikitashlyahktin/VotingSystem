import requests
from requests.exceptions import ConnectionError, Timeout, RequestException


def test_connection(url: str) -> bool:
    """Check if the given URL is reachable."""
    print(f"🔌 Testing connection to {url} ...")
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Connected — Status code: {response.status_code}")
        print(f"Preview: {response.text[:200]}...\n")
        return True
    except ConnectionError:
        print(f"❌ Connection error: Unable to reach {url}\n")
    except Timeout:
        print(f"⏳ Timeout while trying to reach {url}\n")
    except Exception as e:
        print(f"⚠️ Unexpected error while testing connection: {str(e)}\n")
    return False


def send_registration_request(base_url: str):
    """Send a test registration request to the given base URL."""
    register_url = f"{base_url}/register"
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"📤 Sending registration request to {register_url}")
    print(f"📦 Payload: {data}")

    try:
        response = requests.post(register_url, json=data, headers=headers, timeout=5)
        print(f"📬 Response status: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        print(f"📝 Body: {response.text}\n")
        print(f"Request URL: {response.request.url}")
        print(f"Request body: {response.request.body}")
        print(f"Request headers: {response.request.headers}")

    except Timeout:
        print("⏱️ Registration request timed out\n")
    except ConnectionError:
        print("🚫 Could not connect to the server\n")
    except RequestException as e:
        print(f"❗ Request failed: {str(e)}\n")


def test_registration_on_ports():
    """Try registration on multiple local ports."""
    ports = [8000, 8001, 8002]
    base_url_template = "http://127.0.0.1:{}"

    for port in ports:
        print(f"\n=== 🔍 Testing port {port} ===")
        url = base_url_template.format(port)

        if test_connection(f"{url}/docs"):
            send_registration_request(url)
        else:
            print(f"➡️ Skipping registration attempt on port {port} due to connection failure.\n")


if __name__ == "__main__":
    test_registration_on_ports()
