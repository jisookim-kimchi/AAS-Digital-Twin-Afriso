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
	rm -rf data/mongodb
	rm -rf $(VENV)

run: venv
	$(PYTHON) main.py

.PHONY: up venv down logs clean fclean run