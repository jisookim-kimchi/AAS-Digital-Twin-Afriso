#!/usr/bin/env bash
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

USER_NAME=${KEYCLOAK_TEST_USER_NAME:-user}
USER_PASSWORD=${KEYCLOAK_TEST_USER_PASSWORD:-1234}

RESPONSE=$(curl -s -d "client_id=basyx-client" \
  -d "username=${USER_NAME}" \
  -d "password=${USER_PASSWORD}" \
  -d "grant_type=password" \
  http://localhost:9999/realms/basyx/protocol/openid-connect/token)

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
  echo "=== KEYCLOAK USER TOKEN (aas-user / Read-Only) ==="
  echo "$TOKEN"
else
  echo "[-] Failed to acquire user token."
  echo "$RESPONSE"
fi
