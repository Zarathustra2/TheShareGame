all: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

deps: ## Install all dependencies
	@npm install 

fmt: ## Format all files
	@npm run lint --fix

lint: ## Check if all files have been formatted
	@npm run lint

build: ## Build the frontend
	@npm run build

test: ## Run all unit tests
	@npm run test:unit -- --collectCoverage=false

cov: ## Run all unit tests with coverage
	@npm run test:unit

runserver: ## Run the dev server
	@npm run serve

runserver-live-backend: ## Run the dev server and connect with the thesharegame.com backend
	@npm run serve -- --mode liveBackend

open-cov: ## Opens the browser with the coverage report
	@open coverage/lcov-report/index.html
