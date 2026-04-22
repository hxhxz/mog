COMPOSE := docker compose -f infra/docker-compose.yml --env-file infra/env/.env

.PHONY: up down logs ps build rebuild test fmt migrate seed clean

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build

rebuild:
	$(COMPOSE) build --no-cache

test:
	$(COMPOSE) exec api pytest -q
	$(COMPOSE) exec web pnpm test || true

fmt:
	$(COMPOSE) exec api ruff format app tests
	$(COMPOSE) exec web pnpm fmt || true

migrate:
	$(COMPOSE) exec api alembic upgrade head

seed:
	$(COMPOSE) exec api python -m scripts.seed

clean:
	$(COMPOSE) down -v
