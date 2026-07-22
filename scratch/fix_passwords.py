import requests

token_res = requests.post(
    "http://localhost:9999/realms/master/protocol/openid-connect/token",
    data={
        "client_id": "admin-cli",
        "username": "keycloack",
        "password": "1234",
        "grant_type": "password",
    },
)
token = token_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

users = requests.get("http://localhost:9999/admin/realms/basyx/users", headers=headers).json()

for u in users:
    res = requests.put(
        f"http://localhost:9999/admin/realms/basyx/users/{u['id']}/reset-password",
        headers=headers,
        json={"type": "password", "value": "1234", "temporary": False},
    )
    print(f"Reset password for {u['username']}: {res.status_code}")
