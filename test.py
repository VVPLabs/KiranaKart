import requests
import schemathesis

# Define API Schema
schema = schemathesis.from_uri("http://127.0.0.1:8000/openapi.json")

def get_auth_token():
    url = "http://127.0.0.1:8000/auth/login"
    credentials = {"username": "JohnDoe_99", "password": "StrongPass@1"}
    response = requests.post(url, json=credentials)
    token = response.json().get("access_token", "")

    if not token:
        print("❌ Failed to get token:", response.json())
    else:
        print("✅ Auth token received:", token)

    return token

@schema.parametrize()  # This generates multiple test cases
def test_api(case):
    token = get_auth_token()
    if not token:
        print("❌ Skipping test: No auth token")
        return

    case.headers = {"Authorization": f"Bearer {token}"}
    response = case.call()

    print(f"✅ Running test for: {case.method} {case.path}")
    print(f"Response: {response.status_code} {response.text}")

    case.validate_response(response)
