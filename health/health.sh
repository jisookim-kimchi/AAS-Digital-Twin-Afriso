#!/usr/bin/env bash

BLUE='\033[1;36m' 
RED='\033[0;31m'
NC='\033[0m' 


echo "Digital Twins System Health Check"

check_service()
{
    local name="$1"
    local url="$2"
    local match="$3"

    if curl --connect-timeout 2 -s "$url" | grep -qE "$match"; then
        echo -e "$name ----> ${BLUE}UP (OK)${NC}"
    else
        echo -e "$name ----> ${RED}DOWN${NC}"
    fi
}

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

SERVER_HOST=${HEALTH_CHECK_HOST:-127.0.0.1}

# 1. Nginx Proxy
check_service "Nginx Proxy (80)" "http://${SERVER_HOST}:80/" "301|302|html|Moved|nginx|Found"

# 2. Keycloak Auth
check_service "Keycloak Auth (9999)" "http://${SERVER_HOST}:9999/realms/basyx" "realm"

# 3. Machine1 AAS
check_service "Machine1 AAS (8081)" "http://${SERVER_HOST}:8081/actuator/health" "UP"

# 4. Machine2 AAS
check_service "Machine2 AAS (8082)" "http://${SERVER_HOST}:8082/actuator/health" "UP"

# 5. AAS Registry
check_service "AAS Registry (8083)" "http://${SERVER_HOST}:8083/actuator/health" "UP"

# 6. Submodel Registry
check_service "Submodel Registry (8084)" "http://${SERVER_HOST}:8084/actuator/health" "UP"

# 7. AAS Web UI
check_service "AAS Web UI (3001)" "http://${SERVER_HOST}:3001/" "301|302|html|Found|Moved|200"

# 8. MongoDB Ping
if [ "$(docker inspect -f '{{.State.Health.Status}}' mongo 2>/dev/null)" = "healthy" ]; then
    echo -e "MongoDB (27017)------> ${BLUE}UP (OK)${NC}"
else
    echo -e "MongoDB (27017)------> ${RED}DOWN${NC}"
fi
