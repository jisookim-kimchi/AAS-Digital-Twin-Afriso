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

    if curl -s "$url" | grep -q "$match"; then
        echo -e "$name ----> ${BLUE}UP (OK)${NC}"
    else
        echo -e "$name ----> ${RED}DOWN${NC}"
    fi
}

# 1. Nginx Proxy
check_service "Nginx Proxy (8080)" "http://localhost:8080/actuator/health" "UP"

# 2. Keycloak Auth
check_service "Keycloak Auth (9999)" "http://localhost:9999/realms/basyx" "realm"

# 3. Machine1 AAS
check_service "Machine1 AAS (8081)" "http://localhost:8081/actuator/health" "UP"

# 4. Machine2 AAS
check_service "Machine2 AAS (8082)" "http://localhost:8082/actuator/health" "UP"

# 5. AAS Registry
check_service "AAS Registry (8083)" "http://localhost:8083/actuator/health" "UP"

# 6. Submodel Registry
check_service "Submodel Registry (8084)" "http://localhost:8084/actuator/health" "UP"

# 7. AAS Web UI
check_service "AAS Web UI (3000)" "http://localhost:3000/" "UP"

# 8. MongoDB Ping
if [ "$(docker inspect -f '{{.State.Health.Status}}' mongo 2>/dev/null)" = "healthy" ]; then
    echo -e "MongoDB (27017)------> ${BLUE}UP (OK)${NC}"
else
    echo -e "MongoDB (27017)------> ${RED}DOWN${NC}"
fi
