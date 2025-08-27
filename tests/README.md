# Testing Directory

This directory contains all testing files and programs for the Ellipsoid Labs website project.

## Directory Structure

```
tests/
├── README.md                    # This file - overview of testing structure
├── backend/                     # Backend API testing
│   ├── test_areas_of_interest.py    # Comprehensive test program for areas_of_interest
│   ├── example_usage.py             # Simple usage examples
│   ├── test_frontend_integration.py # Frontend integration testing
│   ├── debug_request.py             # Debug and troubleshooting script
│   ├── run_all_tests.py             # Test runner for complete test suite
│   ├── test_requirements.txt        # Python dependencies for testing
│   ├── TEST_README.md              # Detailed testing documentation
│   └── REFACTORING_SUMMARY.md      # Summary of backend refactoring changes
└── [future test directories]   # Other testing areas (frontend, integration, etc.)
```

## Current Testing Status

### ✅ **Backend Tests (Complete)**
- **Location**: `tests/backend/`
- **Status**: Fully updated and working with new `.env` configuration system
- **Coverage**: Comprehensive testing of areas_of_interest parameter and API endpoints
- **Issues**: Known issue with areas_of_interest filtering logic (locations outside specified areas are still being enhanced)

### ❌ **Frontend Tests (Not Implemented)**
- **Location**: None exist
- **Status**: No frontend test files found
- **Infrastructure**: Testing libraries installed (`@testing-library/react`, etc.) but no tests written
- **Recommendation**: Create frontend tests for React components and user interactions

## Backend Testing

The `backend/` subdirectory contains comprehensive testing for the backend API, specifically for the new configurable `areas_of_interest` parameter feature and the updated `.env` configuration system.

### Quick Start

1. **Navigate to the backend test directory:**
   ```bash
   cd tests/backend
   ```

2. **Install test dependencies:**
   ```bash
   pip install -r test_requirements.txt
   ```

3. **Run the complete test suite:**
   ```bash
   python run_all_tests.py
   ```

4. **Or run individual tests:**
   ```bash
   python test_areas_of_interest.py
   python example_usage.py
   python test_frontend_integration.py
   python debug_request.py
   ```

### What's Tested

- **Geographic entity filtering** with different areas of interest
- **API parameter handling** for the new configurable feature
- **Backward compatibility** for existing API clients
- **Edge cases** and boundary conditions
- **Multiple area configurations** (single, multiple, none)
- **Frontend integration** with the new API
- **Configuration system** compatibility (.env files)
- **Error handling** and validation

### New Features Tested

- **areas_of_interest parameter**: Configurable geographic filtering
- **Multiple area support**: OR logic for multiple geographic regions
- **Enhanced error handling**: Better debugging and troubleshooting
- **Configuration compatibility**: Works with new .env system
- **Frontend integration**: Simulates real frontend requests

### Known Issues

- **areas_of_interest filtering**: The backend receives the parameter correctly but doesn't filter geographic entities as expected
- **All locations enhanced**: Currently, all geographic entities are enhanced regardless of areas_of_interest settings
- **Backend logic issue**: The filtering logic in the backend needs investigation and fixing

### Prerequisites

- Backend server running on port 8000
- Valid authentication token (username: david, password: Connie97)
- Python with required dependencies installed
- New .env configuration system properly configured

## Test Files Overview

### `test_areas_of_interest.py`
- **Purpose**: Comprehensive testing of the areas_of_interest parameter
- **Tests**: 5 different scenarios with detailed analysis
- **Output**: Enhanced with emojis and clear success/failure indicators
- **Analysis**: Automatic enhancement result analysis
- **Status**: Working but reveals backend filtering issue

### `example_usage.py`
- **Purpose**: Simple examples for developers
- **Examples**: 5 different usage patterns
- **Learning**: Shows how to use the new API features
- **Analysis**: Step-by-step enhancement analysis
- **Status**: Working correctly

### `test_frontend_integration.py`
- **Purpose**: Test frontend integration scenarios
- **Scenarios**: Single area, multiple areas, no filtering
- **Validation**: Ensures frontend can properly use the API
- **Output**: Clear integration test results
- **Status**: Working but reveals backend filtering issue

### `debug_request.py`
- **Purpose**: Debug and troubleshoot API issues
- **Tests**: Minimal, areas_of_interest, and invalid payloads
- **Debugging**: Detailed error analysis and response inspection
- **Validation**: Tests error handling and validation
- **Status**: Working correctly

### `run_all_tests.py`
- **Purpose**: Run complete test suite in sequence
- **Execution**: Automatically runs all test files
- **Summary**: Provides comprehensive test results
- **Reporting**: Clear pass/fail status for each test
- **Status**: Working correctly

## Frontend Testing Status

### Current State
- **No test files exist** in the frontend directory
- **Testing infrastructure available** (React Testing Library, Jest)
- **Test script configured** (`npm test` command available)

### What Should Be Tested
- **React components**: Chatbot, RAGChatbot, Settings, Login, etc.
- **User interactions**: Form submissions, authentication, settings changes
- **State management**: Context API, sessionStorage, authentication state
- **API integration**: Frontend-backend communication
- **Configuration**: Environment variable handling

### Recommended Next Steps
1. Create `tests/frontend/` directory
2. Add component test files (e.g., `App.test.js`, `Chatbot.test.js`)
3. Add integration test files
4. Update this README with frontend testing documentation

## Future Testing Areas

This directory structure is designed to accommodate future testing needs:

- **Frontend testing** - React component testing (not yet implemented)
- **Integration testing** - End-to-end workflows
- **Performance testing** - Load and stress testing
- **Security testing** - Authentication and authorization
- **Configuration testing** - Environment and deployment testing

## Contributing

When adding new tests:

1. Create appropriate subdirectories for test categories
2. Include clear documentation and README files
3. Provide requirements files for dependencies
4. Add examples and usage documentation
5. Update this main README with new sections
6. Follow the emoji-based output format for consistency
7. Include proper error handling and debugging capabilities
8. Add new tests to the `run_all_tests.py` runner (for backend tests)

## Notes

- All backend test files are designed to be run independently
- Documentation includes troubleshooting guides
- Examples show both basic and advanced usage patterns
- Test programs include proper error handling and user feedback
- Updated for the new .env configuration system
- Enhanced with better visual feedback and analysis
- Increased timeouts for GeoNER processing
- Comprehensive validation of areas_of_interest functionality
- Complete test suite runner available for automated testing
- **Known issue**: areas_of_interest filtering not working in backend
- **Frontend tests**: Need to be created from scratch
