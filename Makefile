# Makefile for Image Analysis with CLIP and LLM

.PHONY: help install test test-unit test-integration lint format clean setup run-example

# Default target
help:
	@echo "🖼️  Image Analysis with CLIP and LLM - Development Commands"
	@echo "=========================================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup          - Initial setup and configuration"
	@echo "  install        - Install dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run linting checks"
	@echo "  format         - Format code with black"
	@echo "  type-check     - Run type checking with mypy"
	@echo ""
	@echo "Development:"
	@echo "  run-example    - Run example analysis"
	@echo "  clean          - Clean generated files"
	@echo "  docs           - Generate documentation"

# Setup and installation
setup:
	@echo "🚀 Setting up Image Analysis system..."
	python src/utils/installer.py

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "🔧 Installing development dependencies..."
	pip install -e ".[dev]"

# Testing
test:
	@echo "🧪 Running all tests..."
	python tests/run_tests.py

test-unit:
	@echo "🧪 Running unit tests..."
	python tests/run_tests.py unit

test-integration:
	@echo "🔗 Running integration tests..."
	python tests/run_tests.py integration

test-coverage:
	@echo "📊 Running tests with coverage..."
	pytest --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	@echo "🔍 Running linting checks..."
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
	pylint src/ --disable=C0114,C0116

format:
	@echo "🎨 Formatting code..."
	black src/ tests/ --line-length=100
	isort src/ tests/

type-check:
	@echo "🔍 Running type checks..."
	mypy src/ --ignore-missing-imports

# Development tasks
run-example:
	@echo "🎯 Running example analysis..."
	python examples/basic_usage.py

clean:
	@echo "🧹 Cleaning generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	rm -rf Output/*.json

docs:
	@echo "📚 Generating documentation..."
	# Add documentation generation commands here if needed

# Quick development workflow
dev-setup: install-dev setup
	@echo "✅ Development environment ready!"

quick-test: format lint test-unit
	@echo "✅ Quick test cycle complete!"

# Docker commands (if needed in the future)
docker-build:
	@echo "🐳 Building Docker image..."
	# docker build -t image-analysis-clip-llm .

docker-run:
	@echo "🐳 Running Docker container..."
	# docker run -it image-analysis-clip-llm 