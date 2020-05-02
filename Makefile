all: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

define BANNER
 _____ ____   ____
|_   _/ ___| / ___|
  | | \___ \| |  _
  | |  ___) | |_| |
  |_| |____/ \____|
endef

.PHONY: build
build: ## Build all services
	
	# Build the frontend so nginx can pick up all the html files from the frontend/dist folder
	@$(MAKE) -C frontend build
	
	# Build the docs for the subdomain docs.thesharegame.com
	@$(MAKE) -C docs html

	@docker-compose build

.PHONY: logs
logs: ## Display log output of all services
	@docker-compose logs

.PHONY: ps
ps: ## List all containers
	@docker-compose ps

.PHONY: up
up: ## Starts all services
	@docker-compose up

.ONESHELL:
.PHONY: test
test: ## Run all tests for the whole project
	@$(MAKE) -C backend lint
	@$(MAKE) -C backend test

	@$(MAKE) -C backend/chat lint
	@$(MAKE) -C backend/chat test

	@$(MAKE) -C frontend lint
	@$(MAKE) -C frontend test

.PHONY: fmt
fmt: ## Format all files in the whole project
	@$(MAKE) -C backend fmt
	@$(MAKE) -C backend/chat fmt
	@$(MAKE) -C frontend fmt

.PHONY: deps
deps: ## Install all dependencies for the whole project and create the database
	@$(MAKE) -C backend deps
	@$(MAKE) -C backend/chat deps
	@$(MAKE) -C frontend deps
	@$(MAKE) -C docs deps
	make db_setup

.PHONY: db_setup
db_setup: ## Creates the database and the user for the postgres database
	@psql -U postgres -f scripts/db_setup.sql || echo 'If u are on mac and installed postgres via homebrew, please run: /usr/local/opt/postgres/bin/createuser -s postgres' 

.PHONY: banner
banner:
	$(info $(BANNER))

