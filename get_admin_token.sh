#!/usr/bin/env bash
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

ADMIN_NAME=${KEYCLOAK_TEST_ADMIN_NAME:-admin}
ADMIN_PASSWORD=${KEYCLOAK_TEST_ADMIN_PASSWORD:-1234}

RESPONSE=$(curl -s -d "client_id=basyx-client" \
  -d "username=${ADMIN_NAME}" \
  -d "password=${ADMIN_PASSWORD}" \
  -d "grant_type=password" \
  http://localhost:9999/realms/basyx/protocol/openid-connect/token)

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
  echo "=== KEYCLOAK ADMIN TOKEN (aas-admin / Full Control) ==="
  echo "$TOKEN"
else
  echo "[-] Failed to acquire admin token."
  echo "$RESPONSE"
fi
