up:
	mkdir -p data/mongodb
	mkdir -p config
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v

fclean: clean
	docker compose down --rmi all -v --remove-orphans
	sudo rm -rf data/mongodb

.PHONY: up down logs clean fclean run

run:
	python3 main.py

#need to change podman version