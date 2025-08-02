# Propter-Optimis Sports Analytics Platform - Makefile
# Professional sports analytics platform development and deployment commands

.PHONY: help install dev build test clean deploy setup-env

# Default target
help:
	@echo "Propter-Optimis Sports Analytics Platform"
	@echo "=========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  setup-env     - Set up development environment"
	@echo "  install       - Install all dependencies"
	@echo "  dev           - Start development servers (backend + frontend)"
	@echo "  backend-dev   - Start Django development server"
	@echo "  frontend-dev  - Start React development server"
	@echo "  build         - Build production version"
	@echo "  test          - Run all tests"
	@echo "  test-backend  - Run Django tests"
	@echo "  test-frontend - Run React tests"
	@echo "  clean         - Clean build artifacts"
	@echo "  deploy        - Deploy to production"
	@echo "  migrate       - Run Django migrations"
	@echo "  collectstatic - Collect static files"
	@echo "  shell         - Open Django shell"
	@echo "  superuser     - Create Django superuser"
	@echo "  docker-build  - Build Docker images"
	@echo "  docker-up     - Start Docker containers"
	@echo "  docker-down   - Stop Docker containers"

setup-env:
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please update .env file with your configuration"

install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && pip3 install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd app && npm install

dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:5173"
	make -j2 backend-dev frontend-dev

backend-dev:
	@echo "Starting Django development server..."
	cd backend && python3 manage.py runserver 8000

frontend-dev:
	@echo "Starting React development server..."
	cd app && npm run dev

build: build-backend build-frontend

build-backend:
	@echo "Building backend for production..."
	cd backend && python manage.py collectstatic --noinput
	build-frontend:
	@echo "Building frontend for production..."
	cd app && npm run build

test: test-backend test-frontend

test-backend:
	@echo "Running Django tests..."
	cd backend && python manage.py test

test-frontend:
	@echo "Running React tests..."
	cd app && npm run test

migrate:
	@echo "Running Django migrations..."
	cd backend && python manage.py migrate

collectstatic:
	@echo "Collecting static files..."
	cd backend && python manage.py collectstatic --noinput

shell:
	@echo "Opening Django shell..."
	cd backend && python manage.py shell

superuser:
	@echo "Creating Django superuser..."
	cd backend && python manage.py createsuperuser

clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/staticfiles/
	rm -rf app/dist/
	rm -rf app/build/
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -name "node_modules" -type d -prune -exec rm -rf {} +

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

deploy: build
	@echo "Deploying to production..."
	@echo "Backend deployment:"
	@echo "1. Push to Railway/Render"
	@echo "2. Set environment variables"
	@echo "3. Run migrations"
	@echo ""
	@echo "Frontend deployment:"
	@echo "1. Deploy to Vercel/Netlify"
	@echo "2. Set environment variables"
	@echo "3. Configure domain"

# Development helpers
format:
	@echo "Formatting code..."
	cd backend && black .
	cd app && npm run format

lint:
	@echo "Linting code..."
	cd backend && flake8 .
	cd app && npm run lint

# Database helpers
reset-db:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd backend && python manage.py flush --noinput; \
		cd backend && python manage.py migrate; \
	fi

seed-db:
	@echo "Seeding database with sample data..."
	cd backend && python manage.py loaddata fixtures/sample_data.json

# Production helpers
production-check:
	@echo "Running production readiness checks..."
	cd backend && python manage.py check --deploy
	cd app && npm run build

backup-db:
	@echo "Creating database backup..."
	mkdir -p backups
	pg_dump $$DATABASE_URL > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
