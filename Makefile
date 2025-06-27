# IT Asset Manager - Docker Operations Makefile

.PHONY: help build up down logs test clean security performance deploy

# Default target
help: ## Show this help message
	@echo "IT Asset Manager - Docker Operations"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development commands
build: ## Build Docker images
	docker-compose build

up: ## Start development environment
	docker-compose up -d
	@echo "Application starting at http://localhost:5000"
	@echo "Nginx proxy at http://localhost:80"

down: ## Stop all services
	docker-compose down

logs: ## Show application logs
	docker-compose logs -f app-dev

shell: ## Access application shell
	docker-compose exec app-dev /bin/bash

db-shell: ## Access database shell
	docker-compose exec postgres-dev psql -U it_assets_user -d it_assets_dev

redis-shell: ## Access Redis shell
	docker-compose exec redis-dev redis-cli

# Production commands
prod-build: ## Build production images
	docker-compose -f docker-compose.prod.yml build

prod-up: ## Start production environment
	@if [ ! -f .env ]; then echo "Error: .env file not found. Copy .env.example to .env and configure it."; exit 1; fi
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production application starting at https://localhost"

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f

prod-scale: ## Scale production application (usage: make prod-scale REPLICAS=4)
	docker-compose -f docker-compose.prod.yml up -d --scale app=$(or $(REPLICAS),2)

# Monitoring commands
monitoring-up: ## Start with monitoring stack
	docker-compose -f docker-compose.prod.yml --profile monitoring up -d
	@echo "Grafana available at http://localhost:3000"
	@echo "Prometheus available at http://localhost:9090"

monitoring-down: ## Stop monitoring stack
	docker-compose -f docker-compose.prod.yml --profile monitoring down

# Testing commands
test: ## Run all tests
	docker-compose -f docker-compose.test.yml up --build app-test
	docker-compose -f docker-compose.test.yml down

test-unit: ## Run unit tests only
	docker-compose exec app-dev pytest tests/unit/ -v

test-integration: ## Run integration tests
	docker-compose -f docker-compose.test.yml up --build app-test
	docker-compose -f docker-compose.test.yml down

test-coverage: ## Run tests with coverage report
	docker-compose -f docker-compose.test.yml up --build app-test
	@echo "Coverage report available in htmlcov/index.html"

performance: ## Run performance tests
	docker-compose -f docker-compose.test.yml up -d app-dev
	docker-compose -f docker-compose.test.yml run --rm k6
	docker-compose -f docker-compose.test.yml down

security: ## Run security tests
	docker-compose -f docker-compose.test.yml up -d app-dev
	docker-compose -f docker-compose.test.yml run --rm zap
	docker-compose -f docker-compose.test.yml down
	@echo "Security report available in zap_results volume"

# Database commands
db-backup: ## Create database backup
	@if [ -f docker-compose.prod.yml ]; then \
		docker-compose -f docker-compose.prod.yml exec postgres-backup /backup.sh; \
	else \
		docker-compose exec postgres-dev pg_dump -U it_assets_user -d it_assets_dev > backup_$$(date +%Y%m%d_%H%M%S).sql; \
	fi

db-restore: ## Restore database from backup (usage: make db-restore BACKUP=backup_file.sql)
	@if [ -z "$(BACKUP)" ]; then echo "Error: Please specify BACKUP=filename"; exit 1; fi
	docker-compose exec postgres-dev psql -U it_assets_user -d it_assets_dev < $(BACKUP)

db-reset: ## Reset development database
	docker-compose down
	docker volume rm it-asset-manager_postgres_dev_data || true
	docker-compose up -d postgres-dev
	@echo "Waiting for database to be ready..."
	@sleep 10
	docker-compose up -d app-dev

# Maintenance commands
clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

clean-all: ## Clean up all Docker resources (including images)
	docker-compose down -v --rmi all
	docker system prune -af
	docker volume prune -f

update: ## Update Docker images
	docker-compose pull
	docker-compose -f docker-compose.prod.yml pull

health: ## Check application health
	@echo "Checking application health..."
	@curl -f http://localhost:5000/health || echo "Development app not responding"
	@curl -f http://localhost/health || echo "Nginx proxy not responding"

# SSL commands
ssl-generate: ## Generate self-signed SSL certificates
	mkdir -p docker/nginx/ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout docker/nginx/ssl/key.pem \
		-out docker/nginx/ssl/cert.pem \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
	@echo "Self-signed SSL certificates generated"

# Deployment commands
deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging..."
	git pull origin develop
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Staging deployment completed"

deploy-prod: ## Deploy to production environment
	@echo "Deploying to production..."
	@if [ -z "$(TAG)" ]; then echo "Error: Please specify TAG=version"; exit 1; fi
	git checkout $(TAG)
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production deployment completed"

# Development helpers
dev-setup: ## Setup development environment
	cp .env.example .env.dev
	docker-compose build
	docker-compose up -d
	@echo "Development environment setup completed"
	@echo "Application available at http://localhost:5000"
	@echo "Default login: admin / admin123"

dev-reset: ## Reset development environment
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Development environment reset completed"

# Utility commands
status: ## Show service status
	docker-compose ps

stats: ## Show resource usage
	docker stats --no-stream

inspect: ## Inspect application container
	docker-compose exec app-dev python -c "from it_asset_manager.core.app import create_app; app = create_app('development'); print('App created successfully')"

# Backup and restore commands
backup-all: ## Backup all data (database and volumes)
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	$(MAKE) db-backup
	docker run --rm -v it-asset-manager_sqlite_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/sqlite_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "Full backup completed"

restore-all: ## Restore all data (usage: make restore-all BACKUP_DIR=20231201_120000)
	@if [ -z "$(BACKUP_DIR)" ]; then echo "Error: Please specify BACKUP_DIR=directory"; exit 1; fi
	$(MAKE) db-restore BACKUP=$(PWD)/backups/$(BACKUP_DIR)/database.sql
	docker run --rm -v it-asset-manager_sqlite_data:/data -v $(PWD)/backups:/backup alpine tar xzf /backup/sqlite_backup_*.tar.gz -C /data
	@echo "Full restore completed"

# Documentation
docs: ## Generate documentation
	@echo "Documentation available at:"
	@echo "  - README.md - Main documentation"
	@echo "  - docs/DOCKER.md - Docker deployment guide"
	@echo "  - docs/ARCHITECTURE.md - Architecture documentation"
	@echo "  - docs/DEVELOPMENT.md - Development guide"
