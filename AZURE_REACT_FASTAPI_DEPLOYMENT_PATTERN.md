# Azure Deployment Pattern for React + FastAPI Projects

A comprehensive guide for deploying modern web applications with React frontend and FastAPI backend to Azure, using GitHub Actions for CI/CD.

## Table of Contents

1. [Project Architecture Overview](#project-architecture-overview)
2. [Frontend Configuration Design](#frontend-configuration-design)
3. [Backend Configuration Design](#backend-configuration-design)
4. [Azure Frontend Configuration](#azure-frontend-configuration)
5. [Azure Backend Configuration](#azure-backend-configuration)
6. [GitHub Actions CI/CD Setup](#github-actions-cicd-setup)
7. [Deployment Workflow](#deployment-workflow)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)
9. [Tips and Best Practices](#tips-and-best-practices)

## Project Architecture Overview

This guide covers deploying a **React frontend** and **FastAPI backend** to Azure with the following architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   Azure         │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • Static Files  │    │ • REST API      │    │ • Static Web    │
│ • Environment   │    │ • Environment   │    │   App           │
│   Variables     │    │   Variables     │    │ • App Service   │
│ • Build Process │    │ • Dependencies  │    │ • Databases     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Key Principles:**
- **Frontend**: Static files served by Azure Static Web Apps
- **Backend**: Python application running on Azure App Service
- **CI/CD**: Automatic deployment via GitHub Actions
- **Environment Management**: Separate configs for local vs. production

## Frontend Configuration Design

### Environment File Structure

Create a **hierarchical environment configuration** that automatically adapts to different deployment environments:

```
frontend-react/
├── .env.local          # Local development (localhost API)
├── .env.production     # Production builds (Azure API)
└── .env                # Fallback defaults
```

### Environment File Contents

#### `.env.local` (Local Development)
```bash
# Local development - connects to local backend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG=true
```

#### `.env.production` (Production)
```bash
# Production - connects to Azure backend
REACT_APP_API_URL=https://your-backend.azurewebsites.net
REACT_APP_ENVIRONMENT=production
REACT_APP_DEBUG=false
```

#### `.env` (Fallback)
```bash
# Fallback defaults
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG=true
```

### Environment Variable Precedence

**Critical Understanding**: React environment variables follow this precedence (highest to lowest):

1. **`.env.local`** - Overrides everything (highest priority)
2. **`.env.production`** - Only loaded during `npm run build`
3. **`.env`** - Fallback defaults (lowest priority)

**⚠️ Important**: `.env.local` will **always override** `.env.production`, even during production builds!

### API Service Configuration

Create a centralized API service that automatically uses the correct environment:

```javascript
// src/services/apiService.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Debug logging (remove in production)
console.log('API Base URL:', API_BASE_URL);
console.log('Environment:', process.env.NODE_ENV);

export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  // ... API call implementation
};
```

### Package.json Scripts

```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

**How it works:**
- `npm start` → Uses `.env.local` (development)
- `npm run build` → Uses `.env.production` (production)

## Backend Configuration Design

### Environment File Structure

Create a **production-ready environment configuration** for Azure deployment:

```
backend/
├── .env                # Local development
├── .env.production     # Production (Azure)
└── requirements.txt    # Python dependencies
```

### Environment File Contents

#### `.env` (Local Development)
```bash
# Database Configuration
DB_USERNAME=your_local_username
DB_PASSWORD=your_local_password
DB_HOST=localhost
DB_PORT=1433
DB_NAME=your_database

# API Keys
OPENAI_API_KEY=your_openai_key
JWT_SECRET_KEY=your_jwt_secret
FERNET_KEY=your_fernet_key

# Application Settings
APP_ENV=development
LOG_LEVEL=DEBUG
LOG_FORMAT=human
```

#### `.env.production` (Azure Production)
```bash
# Database Configuration (Azure SQL Database)
DB_USERNAME=your_azure_username
DB_PASSWORD=your_azure_password
DB_HOST=your-server.database.windows.net
DB_PORT=1433
DB_NAME=your_azure_database

# API Keys (same as local)
OPENAI_API_KEY=your_openai_key
JWT_SECRET_KEY=your_jwt_secret
FERNET_KEY=your_fernet_key

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### FastAPI Configuration

Create a configuration system that automatically loads the right environment:

```python
# backend/app/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# For production, also try to load .env.production
if os.getenv("APP_ENV") == "production":
    load_dotenv(".env.production")

class Settings:
    # Database settings
    db_username: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")
    db_host: str = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT", 1433))
    db_name: str = os.getenv("DB_NAME")
    
    # API keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    fernet_key: str = os.getenv("FERNET_KEY")
    
    # Application settings
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "human")

settings = Settings()
```

### Startup Script

Create a startup script that Azure can use:

```python
# backend/run_server.py
#!/usr/bin/env python3
"""
Production startup script for Azure App Service
"""
import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        log_level="info"
    )
```

### Requirements.txt

Ensure all dependencies are listed:

```txt
# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# Database
pyodbc>=4.0.39
pymongo>=4.5.0

# Security
python-jose[cryptography]>=3.3.0
cryptography>=41.0.0

# Utilities
python-dotenv>=1.0.0
python-multipart>=0.0.6
```

## Azure Frontend Configuration

### Azure Static Web Apps Setup

1. **Create Static Web App**
   - Go to Azure Portal → "Create a resource"
   - Search for "Static Web App"
   - Click "Create"

2. **Basic Configuration**
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Name**: `your-project-frontend`
   - **Region**: Choose closest to your users
   - **Build Preset**: **React** (Azure auto-detects)

3. **Build Configuration**
   - **App location**: `./frontend-react`
   - **API location**: Leave empty (no Azure Functions)
   - **Output location**: `build`
   - **Build command**: Leave default (Azure auto-generates)

4. **GitHub Integration**
   - **Source**: GitHub
   - **Repository**: Your GitHub repository
   - **Branch**: `main`
   - **Repository access**: Grant Azure access

### What Azure Creates Automatically

Azure will automatically create:
- **GitHub Actions workflow**: `.github/workflows/azure-static-web-apps-[random].yml`
- **Build configuration**: Optimized for React applications
- **Deployment pipeline**: Automatic on every push to main

### Environment Configuration

**Important**: Azure Static Web Apps **automatically** uses the correct environment:
- **Local development**: `npm start` uses `.env.local`
- **Production builds**: `npm run build` uses `.env.production`
- **Azure deployment**: Workflow runs `npm run build` automatically

## Azure Backend Configuration

### Azure App Service Setup

1. **Create App Service**
   - Go to Azure Portal → "Create a resource"
   - Search for "App Service"
   - Click "Create"

2. **Basic Configuration**
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Same as frontend
   - **Name**: `your-project-backend`
   - **Publish**: **Code**
   - **Runtime stack**: **Python 3.11**
   - **Operating System**: **Linux**
   - **Region**: Same as frontend

3. **App Service Plan**
   - **Plan**: Create new or use existing
   - **Name**: `your-project-plan`
   - **Sku and size**: **Basic B1** (start with basic, scale later)

### Environment Variables Configuration

1. **Go to App Service → Configuration → Application settings**
2. **Add each environment variable** from your `.env.production`:

```bash
# Database Configuration
DB_USERNAME=your_azure_username
DB_PASSWORD=your_azure_password
DB_HOST=your-server.database.windows.net
DB_PORT=1433
DB_NAME=your_azure_database

# API Keys
OPENAI_API_KEY=your_openai_key
JWT_SECRET_KEY=your_jwt_secret
FERNET_KEY=your_fernet_key

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
LOG_FORMAT=json
```

3. **Click "Save"** and wait for restart

### Startup Command Configuration

**Critical**: Set the startup command in Azure Portal:

1. **Go to App Service → Configuration → General settings**
2. **Startup Command**: 
   ```bash
   python -m pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

**⚠️ Why this is critical**: Azure creates fresh containers that don't have dependencies installed. The startup command must install dependencies first.

### Alternative Startup Commands

```bash
# Option 1: Direct uvicorn (requires dependency installation)
python -m pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 2: Using startup script (requires dependency installation)
python -m pip install -r requirements.txt && python run_server.py

# Option 3: Using startup script with explicit uvicorn
python -m pip install -r requirements.txt && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## GitHub Actions CI/CD Setup

### Backend Deployment Workflow

Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend to Azure

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        python -m pytest tests/ -v

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Azure App Service
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'your-project-backend'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: ./backend
```

### Frontend Deployment (Automatic)

**No manual workflow needed!** Azure Static Web Apps automatically creates:
- `.github/workflows/azure-static-web-apps-[random].yml`
- Automatic builds on every push to main
- Automatic deployment to Azure

### Required GitHub Secrets

1. **`AZURE_WEBAPP_PUBLISH_PROFILE`**
   - Get from Azure Portal → App Service → Get publish profile
   - Download the XML file
   - Copy entire content to GitHub secret

2. **`AZURE_STATIC_WEB_APPS_API_TOKEN_[RANDOM]`**
   - Azure automatically creates this
   - No manual configuration needed

## Deployment Workflow

### Complete Deployment Process

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **GitHub Actions Trigger**
   - **Backend**: Runs tests, then deploys to Azure App Service
   - **Frontend**: Azure Static Web Apps automatically builds and deploys

3. **Azure Services Update**
   - **Backend**: New code deployed to App Service
   - **Frontend**: New build deployed to Static Web App

### Expected Timeline

- **GitHub Actions**: 2-5 minutes
- **Backend deployment**: 3-5 minutes
- **Frontend deployment**: 2-3 minutes
- **Total**: 7-13 minutes

## Troubleshooting Common Issues

### Frontend Issues

#### Environment Variable Conflicts
**Problem**: Frontend connects to wrong backend URL
**Root Cause**: `.env.local` overriding `.env.production`
**Solution**: Remove `.env.local` before production builds

```bash
# Remove conflicting file
Remove-Item frontend-react/.env.local -Force

# Verify .env.production exists
Get-Content frontend-react/.env.production
```

#### Build Failures
**Problem**: `npm run build` fails
**Solution**: Check for ESLint errors, unused imports, or syntax issues

### Backend Issues

#### App Hanging During Startup
**Problem**: App shows "Connected!" but never responds
**Root Cause**: FastAPI hanging in `lifespan` function
**Solution**: Comment out blocking operations or add explicit completion

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    # Comment out blocking operations during startup
    # await test_database_connections()
    
    # Add explicit completion message
    logger.info("Application startup completed")
    
    yield
    
    logger.info("Application shutdown completed")
```

#### Startup Command Issues
**Problem**: "uvicorn: not found" or similar errors
**Root Cause**: Dependencies not installed on fresh containers
**Solution**: Always include dependency installation in startup command

```bash
# Correct startup command
python -m pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Never use just
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Environment Variable Issues
**Problem**: Backend can't find environment variables
**Solution**: Verify App Service Configuration settings

### Network Issues

#### CORS Errors
**Problem**: Browser shows CORS errors
**Solution**: Configure FastAPI CORS middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Database Connection Issues
**Problem**: Can't connect to Azure databases
**Solution**: 
1. Check firewall rules allow Azure App Service IPs
2. Verify connection strings in App Service Configuration
3. Test connections locally first

## Tips and Best Practices

### Environment Management

1. **Never commit `.env.local` to git**
   - Add to `.gitignore`
   - Use `.env.local` only for local development

2. **Use `.env.production` for Azure**
   - Commit this file to git
   - Contains production-ready configuration

3. **Environment variable precedence matters**
   - `.env.local` overrides everything
   - `.env.production` only loaded during production builds

### Azure Configuration

1. **Start with Basic App Service Plan**
   - Scale up later as needed
   - Basic B1 is sufficient for most development projects

2. **Always include dependency installation in startup command**
   - Azure creates fresh containers
   - Dependencies must be installed on each container start

3. **Use App Service Configuration for sensitive data**
   - Don't hardcode secrets in code
   - Use Azure Key Vault for production secrets

### Development Workflow

1. **Test locally first**
   - Ensure frontend connects to local backend
   - Verify all environment variables work locally

2. **Use PowerShell for Windows development**
   - Azure deployment works best with PowerShell
   - Avoid Bash commands in Windows environments

3. **Monitor GitHub Actions logs**
   - Check both backend and frontend workflows
   - Look for build errors or deployment failures

### Performance and Scaling

1. **Frontend optimization**
   - Use `npm run build` for production builds
   - Optimize bundle size with code splitting
   - Enable compression in Azure Static Web Apps

2. **Backend optimization**
   - Use connection pooling for databases
   - Implement proper logging and monitoring
   - Consider Azure Application Insights for production

3. **Database optimization**
   - Use Azure SQL Database for relational data
   - Consider Azure Cosmos DB for NoSQL needs
   - Implement proper indexing and query optimization

### Security Best Practices

1. **Environment variables**
   - Never commit secrets to git
   - Use Azure Key Vault for production secrets
   - Rotate keys regularly

2. **Network security**
   - Use Azure Private Endpoints for database access
   - Configure firewall rules appropriately
   - Enable HTTPS everywhere

3. **Authentication and authorization**
   - Implement proper JWT token management
   - Use secure token storage (httpOnly cookies)
   - Implement proper session management

### Monitoring and Debugging

1. **Azure Log Stream**
   - Monitor App Service logs in real-time
   - Use for debugging startup issues

2. **Application Insights**
   - Enable for production applications
   - Monitor performance and errors

3. **Health checks**
   - Implement `/health` endpoints
   - Use for monitoring and load balancer health checks

## Conclusion

This deployment pattern provides a robust, scalable foundation for React + FastAPI applications on Azure. The key success factors are:

1. **Proper environment configuration** with clear precedence rules
2. **Correct Azure startup commands** that include dependency installation
3. **Automated CI/CD** via GitHub Actions
4. **Environment-specific configuration** for local vs. production
5. **Proper troubleshooting procedures** for common issues

By following this pattern, you can create a deployment pipeline that automatically handles both frontend and backend updates, with minimal manual intervention and maximum reliability.

**Remember**: The most common issues are environment variable conflicts and missing dependency installation in startup commands. Always test locally first, and monitor the deployment logs carefully.
