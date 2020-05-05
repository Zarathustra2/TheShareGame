
BINARYNAME=main

all: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


runserver: ## Run the dev server
	@go run .
test: ## Run all tests
	@go test -v ./...

cov: ## Run all tests and create coverage
	@go test -race -coverprofile=coverage.txt -covermode=atomic

build: ## Build the chat
	@go build -o $(BINARYNAME) -v

deps: ## Download all dependencies
	@go mod download

fmt: ## Format all files
	@go fmt ./...

lint: ## Check if all files have been formated
	@invalidFiles=$$(gofmt -l . 2>&1); \
	if [ "$$invalidFiles" ]; then \
		echo "The following files have not been formated, please run 'go fmt' on them:"; \
		echo $$invalidFiles; \
		exit 1; \
	fi;

clean: ## Remove all created files
	@rm $(BINARYNAME)

