# IT Asset Manager - Development Makefile
# Author: Deepak Nemade
# LinkedIn: https://www.linkedin.com/in/deepak-nemade/

.PHONY: help install dev prod test lint security-check clean backup restore

# Default target
help: ## Show this help message
	@echo "IT Asset Manager - Development Commands"
	@echo "======================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation and Setup
install: ## Install dependencies and setup environment
	@echo "🔧 Installing dependencies..."
	pip install -r requirements-dev.txt
	@echo "✅ Dependencies installed"

dev-setup: ## Setup development environment
	@echo "🚀 Setting up development environment..."
	./dev-setup.sh

# Development Environment
dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started at http://localhost:5000"

dev-build: ## Build development containers
	@echo "🔨 Building development containers..."
	docker-compose -f docker-compose.dev.yml build

dev-logs: ## View development logs
	docker-compose -f docker-compose.dev.yml logs -f

dev-shell: ## Access development container shell
	docker-compose -f docker-compose.dev.yml exec app bash

dev-stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down

dev-restart: ## Restart development environment
	@echo "🔄 Restarting development environment..."
	docker-compose -f docker-compose.dev.yml restart

# Production Environment
prod: ## Start production environment
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production environment started at http://localhost"

prod-build: ## Build production containers
	@echo "🔨 Building production containers..."
	docker-compose -f docker-compose.prod.yml build

prod-logs: ## View production logs
	docker-compose -f docker-compose.prod.yml logs -f

prod-stop: ## Stop production environment
	@echo "🛑 Stopping production environment..."
	docker-compose -f docker-compose.prod.yml down

# Testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v --cov=it_asset_manager --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	python -m pytest tests/integration/ -v

test-coverage: ## Generate test coverage report
	@echo "📊 Generating coverage report..."
	python -m pytest tests/ --cov=it_asset_manager --cov-report=html
	@echo "📊 Coverage report generated in htmlcov/"

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	python -m pytest tests/ -f

# Code Quality
lint: ## Run code linting
	@echo "🔍 Running code linting..."
	flake8 it_asset_manager/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	black --check it_asset_manager/ tests/
	isort --check-only it_asset_manager/ tests/

format: ## Format code
	@echo "✨ Formatting code..."
	black it_asset_manager/ tests/
	isort it_asset_manager/ tests/
	@echo "✅ Code formatted"

# Security
security-check: ## Run security checks
	@echo "🔒 Running security checks..."
	bandit -r it_asset_manager/ -f json -o security-report.json || true
	safety check --json --output safety-report.json || true
	@echo "🔒 Security reports generated"

security-scan-docker: ## Scan Docker images for vulnerabilities
	@echo "🔍 Scanning Docker images..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PWD):/root/.cache/ aquasec/trivy image it-asset-manager:latest

# Database
db-migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	python migrate_database.py

db-seed: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	python add_sample_data.py

db-reset: ## Reset database (WARNING: Deletes all data)
	@echo "⚠️ Resetting database..."
	@read -p "Are you sure? This will delete all data (y/N): " confirm && [ "$$confirm" = "y" ]
	rm -f instance/it_assets.db
	python app.py &
	sleep 5
	pkill -f "python app.py"

# Backup and Restore
backup: ## Create database backup
	@echo "💾 Creating backup..."
	./backup.sh

restore: ## Restore from backup
	@echo "📥 Restoring from backup..."
	@read -p "Enter backup file path: " backup_file && \
	cp "$$backup_file" instance/it_assets.db

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	sphinx-build -b html docs/ docs/_build/

docs-serve: ## Serve documentation locally
	@echo "🌐 Serving documentation..."
	cd docs/_build && python -m http.server 8080

# Cleanup
clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f security-report.json safety-report.json
	@echo "✅ Cleanup complete"

clean-docker: ## Clean up Docker resources
	@echo "🧹 Cleaning Docker resources..."
	docker system prune -f
	docker volume prune -f

# Performance
performance-test: ## Run performance tests
	@echo "⚡ Running performance tests..."
	locust -f tests/performance/locustfile.py --headless -u 10 -r 2 -t 60s --host=http://localhost:5000

# Utilities
logs: ## View application logs
	tail -f logs/app.log

shell: ## Start Python shell with app context
	@echo "🐍 Starting Python shell..."
	python -c "from app import app; app.app_context().push(); import IPython; IPython.embed()"

update-deps: ## Update dependencies
	@echo "📦 Updating dependencies..."
	pip-compile requirements.in
	pip-compile requirements-dev.in

check-deps: ## Check for dependency vulnerabilities
	@echo "🔍 Checking dependencies..."
	safety check

# Git hooks
pre-commit: ## Run pre-commit checks
	@echo "🔍 Running pre-commit checks..."
	pre-commit run --all-files

install-hooks: ## Install git hooks
	@echo "🪝 Installing git hooks..."
	pre-commit install

# Docker utilities
docker-stats: ## Show Docker container stats
	docker stats

docker-inspect: ## Inspect Docker containers
	docker-compose -f docker-compose.dev.yml ps

# Environment info
env-info: ## Show environment information
	@echo "Environment Information:"
	@echo "======================"
	@echo "Python version: $$(python --version)"
	@echo "Docker version: $$(docker --version)"
	@echo "Docker Compose version: $$(docker-compose --version)"
	@echo "Git version: $$(git --version)"
	@echo "Current branch: $$(git branch --show-current)"
	@echo "Working directory: $$(pwd)"

# Quick start
quick-start: dev-setup dev ## Quick start development environment
	@echo "🎉 Development environment is ready!"
	@echo "Access the application at: http://localhost:5000"
	@echo "Login with: admin / admin123"
