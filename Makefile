VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

up: venv
	mkdir -p data/mongodb
	mkdir -p config
	podman-compose up -d

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install pandas basyx-python-sdk openpyxl pyecma376-2 requests podman-compose

down:
	podman-compose down

logs:
	podman-compose logs -f

clean:
	podman-compose down -v

fclean: clean
	podman-compose down --rmi all -v --remove-orphans
	sudo rm -rf data
	sudo rm -rf $(VENV)

# Docker-specific commands
up-docker: venv
	mkdir -p data/mongodb
	mkdir -p config
	docker-compose up -d

down-docker:
	docker compose down

logs-docker:
	docker compose logs -f

clean-docker:
	docker compose down -v

fclean-docker: clean-docker
	docker compose down --rmi all -v --remove-orphans
	sudo rm -rf data
	sudo rm -rf $(VENV)

run: venv
	$(PYTHON) main.py

.PHONY: up venv down logs clean fclean run up-docker down-docker logs-docker clean-docker fclean-docker