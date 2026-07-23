#!/usr/bin/env bash
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

ADMIN_NAME=${KEYCLOAK_TEST_ADMIN_NAME:-admin}
ADMIN_PASSWORD=${KEYCLOAK_TEST_ADMIN_PASSWORD:-1234}
TARGET_IP=${1:-${SERVER_IP:-localhost}}

RESPONSE=$(curl -s --connect-timeout 5 -d "client_id=basyx-client" \
  -d "username=${ADMIN_NAME}" \
  -d "password=${ADMIN_PASSWORD}" \
  -d "grant_type=password" \
  http://${TARGET_IP}:9999/realms/basyx/protocol/openid-connect/token)

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
  echo "=== KEYCLOAK ADMIN TOKEN (${TARGET_IP}) ==="
  echo "$TOKEN"
else
  echo "[-] Failed to acquire admin token from ${TARGET_IP}."
  echo "$RESPONSE"
fi
