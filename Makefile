.PHONY: help install test lint format clean docker-build docker-run

help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run all linters"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Remove build artifacts"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest

test-cov:
	pytest --cov=docstring_agent --cov-report=html --cov-report=term

lint:
	flake8 docstring_agent --max-line-length=100
	mypy docstring_agent --ignore-missing-imports

format:
	black docstring_agent tests
	isort docstring_agent tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t docstring-agent .

docker-run:
	docker run --rm -v $(PWD):/code docstring-agent
