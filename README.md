'''
.\.venv\Scripts\activate
'''
'''
# Create a virtual environment
python -m venv .venv

# On Windows
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
or for dev environment:
pip install -r reqdev_requirements.txt

#Set up your repo on GitHub (in the desired organization)
#Upon creating it, GitHub will give you the local git commands to run, e.g.,:
echo "# AmazingLabs" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/dwarthen/ellipsoid_website.git 
git push -u origin main
#note, I made a typo on dwarthen-organizatoin on github, but I'll just live with it.
'''

# Ellipsoid Labs Website - Frontend-Backend Architecture

This project has been refactored from a Streamlit application to a modern frontend-backend architecture with React frontend and FastAPI backend.

## Project Structure

```
website/
├── .venv/                    # Python virtual environment (root level)
├── backend/                  # FastAPI backend service
│   ├── main.py              # Main FastAPI application
│   ├── .env                 # Local development configuration
│   ├── .env.production      # Production configuration (Azure)
│   ├── .env.example         # Configuration template
│   ├── auth/                # Authentication services
│   ├── config/              # Configuration management
│   ├── models/              # Data models
│   ├── services/            # Business logic services
│   ├── APItests/            # API testing suite
│   └── start_backend.bat    # Windows startup script
├── frontend/                 # React frontend application
│   ├── src/                 # React source code
│   │   ├── components/      # React components
│   │   │   ├── Settings.js  # User settings management
│   │   │   └── ...          # Other components
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API service layer
│   │   └── config.js        # Frontend configuration
│   ├── env.local            # Local development environment
│   ├── env.production       # Production environment
│   ├── package.json         # Node.js dependencies
│   └── start_frontend.bat   # Windows startup script
├── geo_ner/                  # Geographic NER package (shared)
├── utils/                    # Utility tools (Streamlit-based)
├── tests/                    # Test programs and documentation
│   ├── README.md            # Testing overview
│   └── backend/             # Backend API testing
├── Docs/                     # Project documentation
│   ├── backend/             # Backend API documentation
│   └── frontend/            # Frontend documentation
├── .github/workflows/        # GitHub Actions CI/CD
├── requirements.txt          # Python dependencies (root level)
├── reqdev_requirements.txt   # Development dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.8+ with pip
- Node.js 14+ with npm
- SQL Server access (Azure)
- MongoDB Atlas access
- OpenAI API key
- AWS Bedrock access
- Azure AI Language Service (for geographic NER)

## Setup Instructions

### 1. Backend Setup

The backend uses the root-level virtual environment (`.venv`) for all Python dependencies.

**Option A: Using the batch script (Windows)**
```bash
# From the project root directory
backend\start_backend.bat
```

**Option B: Manual setup**
```bash
# From the project root directory
# Activate the virtual environment
.\.venv\Scripts\activate

# Install dependencies (from root directory)
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Start the backend
python main.py
```

### 2. Frontend Setup

**Option A: Using the batch script (Windows)**
```bash
# From the project root directory
frontend\start_frontend.bat
```

**Option B: Manual setup**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## Running the Application

1. **Start the backend first** (runs on http://localhost:8000)
2. **Start the frontend** (runs on http://localhost:3000)
3. **Access the application** at http://localhost:3000

## Features

- **User Authentication**: JWT-based login system with SQL Server
- **User Settings Management**: Persistent user preferences with real-time sessionStorage updates
  - ChatGIS salutation preferences
  - GeoRAG model selection (Amazon Nova Lite, Claude 3.5 Sonnet v2)
  - Areas of Interest filtering with configurable geographic bounds
  - Real-time settings synchronization across all frontend components
- **Chat History Persistence**: Advanced session management with browser navigation support
  - ChatGIS chat history preserved during page navigation and browser refresh
  - GeoRAG chat history and map state persistence across sessions
  - Automatic state cleanup on user logout for security
  - Saved chat loading with MongoDB integration
- **GIS Expert AI Chatbot**: OpenAI-powered geographic information system chatbot with **interactive map integration** and persistent state
- **RAG Chatbot**: AWS Bedrock-powered retrieval-augmented generation chatbot with **interactive map integration**
- **Interactive Maps**: Esri ArcGIS integration with topographic basemaps and location-based features for both ChatGIS and GeoRAG
- **Geographic Entity Recognition**: Clickable geographic links in chat messages that place markers on maps
- **Geographic Filtering**: Real-time Areas of Interest integration for enhanced location-based responses (ChatGIS and GeoRAG)
- **Geographic NER**: Integration with geo_ner package for location recognition with configurable areas of interest
- **API Testing**: Comprehensive test suite for all endpoints

## API Endpoints

- `POST /auth/login` - User authentication
- `POST /chat/gis` - GIS chatbot interactions with geographic entity recognition and map integration
- `POST /chat/rag` - RAG chatbot interactions with areas_of_interest support and map integration
- `GET /settings` - Retrieve user settings
- `POST /settings` - Create/update user settings
- `PUT /settings` - Update existing user settings
- `GET /chat/saved` - Retrieve saved chats
- `POST /chat/save` - Save chat history
- `DELETE /chat/{chat_id}` - Delete saved chat
- `GET /about` - About page information
- `GET /system-prompts` - Get system prompts for different AI services (requires authentication)

## User Settings

The application now supports persistent user settings stored in MongoDB:

### ChatGIS Settings
- **Salutation**: None, Sir, or Madam
- **Areas of Interest Filtering**: Enable/disable geographic filtering
- **Geographic Areas**: Up to 3 configurable areas with:
  - Minimum/maximum latitude and longitude (4-decimal precision)
  - Predefined presets (Oceanside CA, San Diego County, California, Texas, New York State)
  - Custom coordinate input

### GeoRAG Settings
- **Model Selection**: Amazon Nova Lite (default) or Claude 3.5 Sonnet v2
- **Areas of Interest Filtering**: Enable/disable geographic filtering
- **Geographic Areas**: Up to 3 configurable areas with:
  - Minimum/maximum latitude and longitude (4-decimal precision)
  - Predefined presets (Oceanside CA, San Diego County, Texas, New York State)
  - Custom coordinate input

Settings are automatically loaded on login, updated in real-time as users interact with the Settings page, and persist across sessions. All settings changes are immediately available to other frontend components via sessionStorage.

## Testing

The project includes comprehensive testing:

### Backend API Testing
```bash
# From the project root directory
.\.venv\Scripts\activate
cd backend/APItests
pytest
```

### Standalone Test Programs
Located in `tests/backend/`:
- `test_areas_of_interest.py` - Test areas_of_interest parameter functionality
- `test_frontend_integration.py` - Test frontend-backend integration
- `example_usage.py` - Usage examples and learning
- `debug_request.py` - Debug and troubleshooting
- `run_all_tests.py` - Complete test suite runner

### Test Status
- **Backend Tests**: ✅ Complete and working with new configuration system
- **Frontend Tests**: ❌ Not yet implemented (infrastructure available)
- **Known Issues**: areas_of_interest filtering logic needs backend investigation

## Configuration

The project now uses environment-based configuration instead of hardcoded secrets:

### Backend Configuration
- **Local Development**: Uses `backend/.env` file
- **Production**: Uses `backend/.env.production` file
- **Template**: `backend/.env.example` for reference
- **Automatic Loading**: Configuration loaded based on `APP_ENV` environment variable

### Frontend Configuration
- **Local Development**: Uses `frontend/env.local` file
- **Production**: Uses `frontend/env.production` file
- **Fallback**: Uses `frontend/env` file
- **API URL**: Configurable via `REACT_APP_API_URL` environment variable

### Environment Variables
- Database credentials (SQL Server, MongoDB)
- API keys (OpenAI, AWS, Azure, Esri, ShipEngine)
- JWT configuration
- Logging settings
- Application environment

### Logging Configuration
Backend logging priority level can be configured in `backend/config/settings.py`:
- `DEBUG` - Detailed debugging information
- `INFO` - General information (default)
- `WARNING` - Warning messages only
- `ERROR` - Error messages only

## Deployment

### Azure Deployment
- **Backend**: Azure App Service with Linux container
- **Frontend**: Azure Static Web Apps with environment-based configuration
- **CI/CD**: GitHub Actions for automatic deployment
- **Configuration**: Environment-based with `.env` files (no manual Azure environment variables needed)

### Backend Deployment Details
The backend is deployed to Azure App Service using GitHub Actions:

1. **GitHub Actions Workflow**: `.github/workflows/main_ellipsoid-backend.yml`
2. **Deployment Files**: Includes `requirements.txt`, `backend/`, and `geo_ner/` directories
3. **Startup Command** (Linux container):
   ```bash
   python -m pip install -r requirements.txt && cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. **Environment Configuration**: Uses `backend/environment.cfg` for development and `backend/environment_production.cfg` for production
5. **Health Check**: Available at `/health` endpoint

### Frontend Deployment Details
The frontend is deployed to Azure Static Web Apps:

1. **GitHub Actions Workflow**: `.github/workflows/azure-static-web-apps-orange-ground-0080e851e.yml`
2. **Build Process**: Automatic npm build with environment-specific configurations
3. **Environment Variables**: Uses `REACT_APP_API_URL` to point to backend
4. **Production URL**: Automatically generated by Azure Static Web Apps

### Environment Configuration
- **Local Development**: Uses `backend/.env` and `frontend/env.local`
- **Production**: Uses `backend/environment_production.cfg` and `frontend/env.production`
- **Template**: `backend/environment_example.cfg` provides configuration template

### GitHub Actions Workflows
- **Backend**: `main_ellipsoid-backend.yml` - Python app deployment to Azure App Service
- **Frontend**: `azure-static-web-apps-orange-ground-0080e851e.yml` - React build and deployment to Azure Static Web Apps
- **Testing**: Automated dependency installation and artifact creation
- **Deployment Triggers**: Automatic deployment on push to main branch

### Local vs Azure Environment Differences
- **Local Development** (Windows PowerShell): Use semicolon syntax
  ```powershell
  cd backend; uvicorn main:app --host 0.0.0.0 --port 8000
  ```
- **Azure Deployment** (Linux container): Use bash syntax
  ```bash
  python -m pip install -r requirements.txt && cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
  ```

## Troubleshooting

### General Issues
- **Backend won't start**: Ensure you're using the root `.venv` virtual environment
- **Configuration issues**: Check that `.env` files exist and contain required values
- **Frontend proxy errors**: Verify the backend is running on http://localhost:8000
- **Import errors**: Check that all dependencies are installed in the root `.venv`
- **Testing issues**: Ensure you're in the correct test directory when running tests
- **Settings not saving**: Check MongoDB connection and user authentication
- **Areas of Interest not working**: Known backend issue - filtering logic needs investigation

### Azure Deployment Issues
- **Startup Command Issues**: Use bash syntax (&&) for Azure, PowerShell syntax (;) for local development
- **Requirements.txt Not Found**: Ensure `requirements.txt` is in the deployment artifact (check GitHub Actions workflow)
- **Environment Files Not Deployed**: Azure may filter `.env*` files - use `environment*.cfg` format for production
- **Backend Not Responding**: Check Azure App Service logs for startup errors and verify health endpoint
- **Container Startup Timeout**: Backend startup may take time - wait for initialization to complete
- **Import Errors in Azure**: Ensure all required directories (`backend/`, `geo_ner/`) are included in deployment
- **Health Endpoint Timeout**: Backend may still be starting up - retry health check after a few minutes

## Development Notes

- The backend uses FastAPI with Uvicorn ASGI server
- Frontend uses React with React Router for navigation
- Authentication state is managed via React Context API
- All database operations are handled by the backend services
- User settings are stored in MongoDB with user isolation
- The geo_ner package supports configurable areas_of_interest for geographic filtering
- Utility tools remain in Streamlit for administrative purposes
- Configuration is now environment-based for better security and deployment
- **Local Development**: Windows PowerShell environment - use semicolon (;) syntax for commands
- **Azure Deployment**: Linux container environment - use bash (&&) syntax for startup commands
- **Environment Files**: Use `.env` format locally, `environment*.cfg` format for Azure deployment

## Recent Updates

- **Configuration System Refactoring**: Complete migration from `secrets.toml` to environment-based configuration
  - `.env` files for local development and production
  - Automatic environment detection and configuration loading
  - Azure-ready deployment with no manual environment variable setup
  - Secure configuration management for both development and production
- **Frontend Service Layer**: Centralized API service with axios instance
  - Single `apiService.js` for all API calls
  - Environment-based API URL configuration
  - Consistent error handling and authentication
  - Removed duplicate API URL definitions
- **Backend Environment Management**: Python-dotenv integration for configuration
  - Automatic loading of appropriate `.env` file based on environment
  - Support for both development and production configurations
  - No more hardcoded secrets in code
  - Azure App Service deployment ready
- **Chat History Persistence**: Complete implementation of sessionStorage-based chat history
  - ChatGIS and GeoRAG chat histories persist across page navigation and browser refresh
  - Map state persistence for both ChatGIS and GeoRAG components
  - Automatic cleanup on logout for security
  - Proper state restoration when returning to chat pages
- **Real-Time Settings Management**: Enhanced user settings with immediate sessionStorage updates
  - Settings changes are instantly available across all frontend components
  - No need to click "Save" for settings to be accessible by other modules
  - Robust loading and persistence logic with race condition prevention
- **Areas of Interest Integration**: Complete end-to-end Areas of Interest functionality
  - Settings page configuration correctly passed to ChatGIS and GeoRAG API calls
  - Fixed data structure mapping between Settings storage and API consumption
  - Only enabled areas with valid coordinates are sent to the backend
  - ChatGIS Areas of Interest filtering for enhanced geographic responses
- **Enhanced State Management**: Improved React component lifecycle management
  - Proper useEffect dependencies and useCallback optimization
  - Protected initial loading to prevent state overwrites
- **Navigation Persistence**: All user preferences maintained during navigation
  - Settings page values reload correctly when returning from other pages
  - Map state persistence in both GeoRAG and ChatGIS components
  - Authentication-aware state management
- **ChatGIS Geographic Enhancement**: Added comprehensive geographic capabilities to ChatGIS
  - Interactive map integration with same functionality as GeoRAG
  - Clickable geographic entities in chat messages that place markers on maps
  - Map state persistence and toggle functionality (minimize/intermediate/maximize)
  - Geo-XML processing for location recognition and tagging
  - SessionStorage management for chat history, map state, and GeoNER settings

## Documentation
For more detailed technical documentation, look in the docs folder.