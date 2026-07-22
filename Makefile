VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

# Start services using podman-compose
up: venv
	mkdir -p data/mongodb
	mkdir -p config
	podman-compose up -d

# Create Python virtual environment and install dependencies
venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install pandas basyx-python-sdk openpyxl pyecma376-2 requests podman-compose

# Stop podman-compose services
down:
	podman-compose down

# Tail podman-compose logs
logs:
	podman-compose logs -f

# Remove containers and volumes (podman)
clean:
	podman-compose down -v

# Deep clean including volumes, images, data, and venv (podman)
fclean: clean
	podman-compose down --rmi all -v --remove-orphans
	sudo rm -rf data
	sudo rm -rf $(VENV)

# Start services using Docker Compose
up-docker: venv
	mkdir -p data/mongodb
	mkdir -p config
	docker-compose up -d

# Tail Docker Compose logs filtered for errors/warnings
logs-docker:
	docker compose logs -f | grep --line-buffered -iE "warn|error|fail" || true

# Stop Docker Compose services
down-docker:
	docker compose down

# Remove Docker containers and volumes
clean-docker:
	docker compose down -v

# Deep clean including volumes, images, data, and venv (Docker)
fclean-docker: clean-docker
	docker compose down --rmi all -v --remove-orphans
	sudo rm -rf data
	sudo rm -rf $(VENV)

# Convert Excel data to AASX packages and upload to BaSyx servers
run: venv
	$(PYTHON) main.py

# Check MongoDB health status
check-mongo:
	@docker exec mongo mongosh -u mongoAdmin -p mongoPassword --authenticationDatabase admin --eval "db.adminCommand('ping')" >/dev/null 2>&1 && echo "MongoDB is RUNNING! (OK)" || echo "MongoDB is DOWN!"

# Check Nginx Gateway health status
check-nginx:
	@curl -s http://localhost:8080/actuator/health | grep -q "UP" && echo "Nginx is RUNNING! (OK)" || echo "Nginx-Proxy is DOWN!"

# Check Keycloak IAM server health status
check-keycloak:
	@curl -s http://localhost:9999/realms/basyx | grep -q "realm" && echo "Keycloak is RUNNING! (OK)" || echo "Keycloak-Auth is DOWN!"

# Check Machine1 AAS server health status
check-aas:
	@curl -s http://localhost:8081/actuator/health | grep -q "UP" && echo "Machine1 is RUNNING! (OK)" || echo "Machine1-AAS is DOWN!"

# Check Machine2 AAS server health status
check-aas2:
	@curl -s http://localhost:8082/actuator/health | grep -q "UP" && echo "Machine2 is RUNNING! (OK)" || echo "Machine2-AAS is DOWN!"

# Check AAS Registry health status
check-aas-registry:
	@curl -s http://localhost:8083/actuator/health | grep -q "UP" && echo "AAS-Registry is RUNNING! (OK)" || echo "AAS-Registry is DOWN!"

# Check Submodel Registry health status
check-sm:
	@curl -s http://localhost:8084/actuator/health | grep -q "UP" && echo "Submodel-Registry is RUNNING! (OK)" || echo "Submodel-Registry is DOWN!"

# Run comprehensive system health check report
check-all:
	@bash health/health.sh
	
# Test Keycloak authentication and Nginx Gateway access
check-token:
	$(PYTHON) check_token.py

# Extract JWT access token for aas-user (Read-Only)
get-user-token:
	@bash get_user_token.sh

# Extract JWT access token for aas-admin (Full Access)
get-admin-token:
	@bash get_admin_token.sh

# Issue a new customer account in Keycloak
add-customer:
	$(PYTHON) create_customer.py $(USER) $(PASSWORD) $(ROLE)

# Request AAS data from external partner server (Direction 2)
request-partner:
	$(PYTHON) request_partner_data.py $(IP) $(USER) $(PASSWORD)

# View Nginx GET access logs (Read events)
check-logs-get:
	@echo "Nginx Gateway GET Access Logs"
	@docker logs nginx 2>&1 | grep "GET" | tail -n 20 || echo "(No GET logs found)"

# View Nginx POST access logs (Write events)
check-logs-post:
	@echo "Nginx Gateway POST Access Logs"
	@docker logs nginx 2>&1 | grep "POST" | tail -n 20 || echo "(No POST logs found)"

# View Nginx 401/403 security blocked logs
check-logs-blocked:
	@echo "Nginx Gateway Security Blocked Logs"
	@docker logs nginx 2>&1 | grep -E "401|403" | tail -n 20 || echo "(No blocked logs found)"



.PHONY: up venv down logs clean fclean run up-docker logs-docker down-docker clean-docker fclean-docker check-mongo check-nginx check-keycloak check-aas check-aas2 check-aas-registry check-sm check-ui check-all check-token get-user-token get-admin-token add-customer request-partner check-logs-get check-logs-post check-logs-blocked