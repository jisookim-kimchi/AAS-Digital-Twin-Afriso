import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP", "localhost")
KEYCLOAK_URL = f"http://{SERVER_IP}:9999/realms/basyx/protocol/openid-connect/token"
GATEWAY_URL = f"http://{SERVER_IP}:8080"

USER_NAME = os.getenv("KEYCLOAK_TEST_USER_NAME", "testuser")
USER_PASSWORD = os.getenv("KEYCLOAK_TEST_USER_PASSWORD", "1234")
ADMIN_NAME = os.getenv("KEYCLOAK_TEST_ADMIN_NAME", "admin")
ADMIN_PASSWORD = os.getenv("KEYCLOAK_TEST_ADMIN_PASSWORD", "1234")


def get_token(username, password):
    data = {
        "grant_type": "password",
        "client_id": "basyx-client",
        "username": username,
        "password": password,
    }
    try:
        r = requests.post(KEYCLOAK_URL, data=data, timeout=5)
        if r.status_code == 200:
            return r.json().get("access_token")
        print(f"Keycloak authentication failed for '{username}': {r.status_code}")
        return None
    except Exception as e:
        print(f"Error connecting to Keycloak: {e}")
        return None


def test_access(username, password, role):
    token = get_token(username, password)
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{GATEWAY_URL}/shells", headers=headers)
    print(f"User: {username} ({role}) -> Token: OK | GET /shells -> {r.status_code}")


if __name__ == "__main__":
    test_access(USER_NAME, USER_PASSWORD, "aas-user")
    test_access(ADMIN_NAME, ADMIN_PASSWORD, "aas-admin")
