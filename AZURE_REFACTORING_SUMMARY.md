# Azure Deployment Refactoring Summary

This document summarizes all the changes made to refactor the Ellipsoid Labs website for Azure deployment following the Azure React + FastAPI deployment pattern.

## Backend Changes

### 1. Environment Configuration Files Created
- `backend/env.local` - Local development environment with all actual secret values
- `backend/env.production` - Production environment (Azure) with same secret values but production settings
- Both files contain the actual values from the original `secrets.toml` file

### 2. Configuration System Refactored
- `backend/config/settings.py` - Updated to use environment variables instead of `secrets.toml`
- Added support for automatic environment detection (development vs production)
- Uses `python-dotenv` to load appropriate environment file
- Maintains backward compatibility with existing code

### 3. Dependencies Updated
- `requirements.txt` - Added `python-dotenv` dependency
- Kept `toml` dependency for backward compatibility

### 4. Azure Production Files Created
- `backend/run_server.py` - Production startup script for Azure App Service
- `backend/startup.txt` - Reference file with Azure startup commands

### 5. CORS Configuration Updated
- `backend/main.py` - Updated CORS middleware to allow Azure domains
- Added support for `*.azurestaticapps.net` and `*.azurewebsites.net`

### 6. GitHub Actions Workflow
- `.github/workflows/deploy-backend.yml` - New workflow for backend deployment to Azure App Service
- Includes testing and deployment steps
- Uses `ellipsoid-backend` as the Azure app name

## Frontend Changes

### 1. Environment Configuration Files Created
- `frontend/env.local` - Local development (localhost:8000)
- `frontend/env.production` - Production (Azure backend URL)
- `frontend/env` - Fallback defaults

### 2. API Service Centralization
- `frontend/src/services/apiService.js` - New centralized API service
- Automatically uses correct environment configuration
- Includes request/response interceptors for authentication
- Handles base URL configuration automatically

### 3. Component Updates
- All components updated to use the centralized API service instead of direct axios/fetch calls
- Components updated:
  - `AuthContext.js`
  - `Chatbot.js`
  - `RAGChatbot.js`
  - `About.js`
  - `Settings.js`

### 4. Package Configuration
- `frontend/package.json` - Removed proxy setting (no longer needed with environment variables)

## Azure Backend Configuration Required

### 1. App Service Configuration
- **App Name**: `ellipsoid-backend`
- **Startup Command**: 
  ```bash
  python -m pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000
  ```

### 2. Environment Variables in Azure Portal
Add these environment variables in Azure Portal → App Service → Configuration → Application settings:

```bash
# Database Configuration
DB_USERNAME=david
DB_PASSWORD=C0nnie97
DB_HOST=geog495db.database.windows.net
DB_PORT=1433
DB_NAME=EllipsoidLabs

# API Keys
OPENAI_API_KEY=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
AWS_ACCESS_KEY_ID=AKIA4N7SKOQHSHVHGR4L
AWS_SECRET_ACCESS_KEY=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
ESRI_API_KEY=AAPTxy8BH1VEsoebNVZXo8HurF89yH3U94of2tNjEtGqtHd_oOPwB6Hr-qkkjGSYglqlcPNZ0VCckRFM08AWdYsjNonYUEO27c0o5JX_sbSr8Uc6z49nfpUU9R9YXnwjObx6hGOpUhsJ6c_oa8bAS_fR3urXcvOj13NFnqaU9kwClmwOPV0FkyGImgJqG3DfUEMFESBYGB98_ttyyS6bNAv42iu5xggMftUElUE1kSZMaIs.AT1_5MNNtJR7-KZBGD1zaLOpJ8mFqcYsTj4iP-MoNd8DY0QK3a3rPFby9P6Hss_JYbKKc2MwLAm0uFr7YTX7tquTAdZE0xTsPHVSlHVbxzny8g_lJoh4kg9CTlx32HiatWjEmDYA8.AT1_5MNNtJR7
SHIPENGINE_API_KEY=TEST_ioChwePt81jYSvpcx+miyWf2Ubw9unDuMtEYUQgRAVo
FERNET_KEY=fC2eGa9S4aLXZgnkFyF2u-KVuHp4CjQjYxn7nci17vM=

# Azure AI Language credentials
AZURE_LANGUAGE_KEY=4pNETtbbESaQAErdspK5f7MNE8PVj8QjWHhXiQXTDYKrDpVXWUZmJQQJ99BHACYeBjFXJ3w3AAAaACOGbSDe
AZURE_LANGUAGE_ENDPOINT=https://ellipsoid-ner.cognitiveservices.azure.com/

# MongoDB
MONGO_CONNECTION_STRING=mongodb+srv://david:C0nnie97@bookshelf.ndy7bsv.mongodb.net/?retryWrites=true&w=majority&appName=bookshelf

# JWT settings
JWT_SECRET_KEY=your-secret-key-change-in-production

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Azure Frontend Configuration Required

### 1. Static Web App Configuration
- **App Name**: `ellipsoid-frontend` (or your preferred name)
- **Build Preset**: React
- **App location**: `./frontend`
- **Output location**: `build`
- **API location**: Leave empty (no Azure Functions)

### 2. Environment Variables
The frontend will automatically use the correct environment:
- **Local development**: `npm start` uses `env.local` (localhost:8000)
- **Production builds**: `npm run build` uses `env.production` (Azure backend)
- **Azure deployment**: Workflow runs `npm run build` automatically

## GitHub Secrets Required

### 1. Backend Deployment
- `AZURE_WEBAPP_PUBLISH_PROFILE` - Get from Azure Portal → App Service → Get publish profile

### 2. Frontend Deployment
- No manual secrets needed - Azure Static Web Apps automatically creates the required token

## Testing Instructions

### 1. Local Backend Testing
```powershell
cd backend
.\.venv\Scripts\activate
python -c "from config.settings import get_settings; print('Settings loaded successfully')"
```

### 2. Local Frontend Testing
```powershell
cd frontend
npm start
```
Verify that it connects to localhost:8000

### 3. Production Build Testing
```powershell
cd frontend
npm run build
```
Verify that the build uses the Azure backend URL

## Next Steps

1. **Test locally** to ensure all changes work correctly
2. **Configure Azure App Service** with the startup command and environment variables
3. **Configure Azure Static Web App** for the frontend
4. **Set up GitHub secrets** for the backend deployment
5. **Test deployment** by pushing to the main branch

## Files Modified

### Backend
- `backend/config/settings.py`
- `backend/main.py`
- `requirements.txt`
- `backend/env.local` (new)
- `backend/env.production` (new)
- `backend/run_server.py` (new)
- `backend/startup.txt` (new)

### Frontend
- `frontend/src/config.js` (already correct)
- `frontend/package.json`
- `frontend/env.local` (new)
- `frontend/env.production` (new)
- `frontend/env` (new)
- `frontend/src/services/apiService.js` (new)
- `frontend/src/contexts/AuthContext.js`
- `frontend/src/components/Chatbot.js`
- `frontend/src/components/RAGChatbot.js`
- `frontend/src/components/About.js`
- `frontend/src/components/Settings.js`

### GitHub Actions
- `.github/workflows/deploy-backend.yml` (new)
- `.github/workflows/main_ellipsoidlabs.yml` (updated)

## Notes

- All original secret values have been preserved and migrated to environment files
- The backend will automatically detect the environment and load the appropriate configuration
- The frontend will automatically use the correct backend URL based on the build environment
- CORS has been configured to allow both local development and Azure deployment
- The refactoring maintains backward compatibility while enabling Azure deployment
