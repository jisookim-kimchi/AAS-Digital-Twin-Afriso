#!/usr/bin/env python3
import sys
import requests


def request_partner_data(partner_ip, username, password):
    keycloak_url = f"http://{partner_ip}:9999/realms/basyx/protocol/openid-connect/token"
    gateway_url = f"http://{partner_ip}:8080/shells"

    token_payload = {
        "client_id": "basyx-client",
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    try:
        r_token = requests.post(keycloak_url, data=token_payload, timeout=5)
        if r_token.status_code != 200:
            print(f"Token error from {partner_ip}: {r_token.status_code}")
            return
        #get token 
        partner_token = r_token.json().get("access_token")
        #get data
        headers = {"Authorization": f"Bearer {partner_token}"}

        r_data = requests.get(gateway_url, headers=headers, timeout=5)
        if r_data.status_code == 200:
            print(f"Partner ({partner_ip}) Data:")
            print(r_data.json())
        else:
            print(f"Gateway error from {partner_ip}: {r_data.status_code}")

    except Exception as e:
        print(f"Connection error to {partner_ip}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: make request-partner IP=<partner_ip> USER=<username> PASSWORD=<password>")
        sys.exit(1)

    request_partner_data(sys.argv[1], sys.argv[2], sys.argv[3])
