# CastCore developer shortcuts (optional — requires `make`).
# On Windows without make, use the raw `docker compose` commands in docs/LOCAL_DEV.md.

.PHONY: up down build logs ps migrate test fe-dev

up:          ## Build + start the full stack
	docker compose up -d --build

down:        ## Stop (keep data volumes)
	docker compose down

build:       ## Rebuild images
	docker compose build

logs:        ## Follow backend + process-manager logs
	docker compose logs -f backend process-manager

ps:          ## Service status
	docker compose ps

migrate:     ## Run DB migrations manually (normally automatic on backend start)
	docker compose exec backend alembic upgrade head

test:        ## Run backend unit tests in an ephemeral container
	docker compose run --rm --no-deps backend sh -c "pip install -q '.[dev]' && pytest -q"

fe-dev:      ## Frontend dev server (needs Node 20 locally)
	cd frontend && npm install && npm run dev
