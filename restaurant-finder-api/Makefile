.PHONY: help install dev test format lint clean docker-build docker-run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -e .

dev:  ## Start local development server
	python -m src.api

test:  ## Run tests
	python -m src.main

test-interactive:  ## Run interactive mode
	python -m src.main interactive

test-streaming:  ## Test streaming
	python -m src.main streaming

test-guardrails:  ## Test guardrails
	python -m src.main guardrails

format:  ## Format code (if using ruff/black)
	@echo "Format tool not configured yet"

lint:  ## Lint code (if using ruff/pylint)
	@echo "Lint tool not configured yet"

docker-build:  ## Build Docker image
	docker build -t restaurant-finder-agent .

docker-run:  ## Run Docker container
	docker run -p 8080:8080 --env-file .env restaurant-finder-agent

clean:  ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +