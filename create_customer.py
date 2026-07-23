#!/usr/bin/env python3
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP", "localhost")
KEYCLOAK_URL = f"http://{SERVER_IP}:9999"
REALM = "basyx"

ADMIN_USER = os.getenv("KEYCLOAK_ADMIN", "keycloack")
ADMIN_PASS = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "1234")


def get_admin_token():
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": ADMIN_USER,
        "password": ADMIN_PASS,
    }
    r = requests.post(url, data=data)
    if r.status_code == 200:
        return r.json().get("access_token")
    print(f"Admin login failed: {r.status_code} - {r.text}")
    return None


def create_customer(username, password, role="aas-user"):
    token = get_admin_token()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    user_payload = {
        "username": username,
        "email": f"{username}@customer.com",
        "firstName": username,
        "lastName": "Customer",
        "enabled": True,
        "emailVerified": True,
        "requiredActions": [],
        "credentials": [
            {
                "type": "password",
                "value": password,
                "temporary": False,
            }
        ],
    }

    create_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    r_create = requests.post(create_url, json=user_payload, headers=headers)

    if r_create.status_code == 409:
        print(f"User '{username}' already exists.")
    elif r_create.status_code not in [201, 204]:
        print(f"Failed to create user '{username}': {r_create.status_code} - {r_create.text}")
        return

    get_user_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users?username={username}"
    r_user = requests.get(get_user_url, headers=headers)
    if r_user.status_code != 200 or not r_user.json():
        print(f"Could not find user ID for '{username}'")
        return
    user_id = r_user.json()[0]["id"]

    get_roles_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/roles/{role}"
    r_role = requests.get(get_roles_url, headers=headers)
    if r_role.status_code != 200:
        print(f"Role '{role}' not found in realm '{REALM}'")
        return
    role_data = [r_role.json()]

    map_role_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm"
    r_map = requests.post(map_role_url, json=role_data, headers=headers)
    if r_map.status_code in [200, 204]:
        print(f"User '{username}' created successfully with role '{role}'")
    else:
        print(f"Failed to assign role '{role}': {r_map.status_code} - {r_map.text}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_customer.py <username> <password> [role]")
        sys.exit(1)

    c_user = sys.argv[1]
    c_pass = sys.argv[2]
    c_role = sys.argv[3] if len(sys.argv) > 3 else "aas-user"

    create_customer(c_user, c_pass, c_role)
