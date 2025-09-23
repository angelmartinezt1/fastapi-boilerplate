# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
```bash
# Local development server (recommended)
python app/local_server.py

# Alternative with uvicorn directly
uvicorn app.main:app --reload

# Install dependencies for development
pip install -r requirements.txt
pip install -r requirements-local.txt
```

### Code Quality
```bash
# Format code with Black
black app/

# Lint with Flake8
flake8 app/

# Run tests
pytest tests/
```

### Database Setup (Required Before Deployment)
```bash
# Create MongoDB indexes (run once per environment)
python deployment/create_indexes.py
```

### AWS SAM Deployment
```bash
# Build SAM application
sam build

# Deploy to development
sam deploy --config-env default

# Deploy with parameters
sam deploy --parameter-overrides Environment=production
```

## Architecture

This is a FastAPI boilerplate designed for dual deployment: local development and AWS Lambda. The architecture follows a clean separation between environments.

### Core Components

**App Factory Pattern**: The application uses a factory pattern in `app/main.py` with `create_app()` function that returns a configured FastAPI instance. This enables consistent app creation across different entry points.

**Dual Entry Points**:
- `app/local_server.py` - Local development with uvicorn and hot reload
- `app/lambda_handler.py` - AWS Lambda handler using Mangum adapter

**Configuration System**: Located in `app/config/`, uses Pydantic settings with environment-based configuration:
- `app/config/base.py` - Base configuration class
- `app/config/app.py` - Application-specific settings with environment detection
- `app/config/database.py` - Database configuration for MongoDB
- `app/config/settings.py` - Singleton configuration instance

**Performance Configuration**:
- `ENABLE_DOCS=false` - Disable OpenAPI/Swagger docs in production for faster cold starts
- Database indexes are pre-created via deployment script (not at runtime)

**Lambda Detection**: The app automatically detects Lambda environment using `AppConfig.is_lambda` property that checks for AWS Lambda environment variables.

### Deployment Strategy

**AWS SAM Framework**: Uses AWS SAM (Serverless Application Model) for infrastructure as code:
- `template.yaml` - Production CloudFormation template with HTTP API Gateway v2
- `template.local.yaml` - Local development template
- `samconfig.toml` - SAM deployment configuration

**Multi-Environment Support**:
- Development and production environments with different configurations
- Environment-specific variables and secrets via GitHub Actions
- VPC support (optional) with conditional CloudFormation logic

**Dependencies Management**:
- `requirements.txt` - Core dependencies for all environments
- `requirements-local.txt` - Additional development tools (black, flake8, pytest)

The Lambda function uses Mangum to adapt FastAPI for AWS Lambda, with automatic CORS configuration and CloudWatch logging.

### GitHub Integration

**Automated Setup**: `scripts/github-setup.sh` and `github-env.json` provide automated GitHub environment, variables, and secrets configuration for CI/CD.

**GitHub Actions**: `.github/workflows/sam.yml` contains SAM deployment workflow for automated deployments.

### Development Workflow

The codebase supports path resolution from project root, enabling imports like `from app.config.settings import app_config` to work consistently across local and Lambda environments. VSCode settings include Black formatting, Flake8 linting, and pytest configuration optimized for FastAPI development.