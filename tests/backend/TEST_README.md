# Areas of Interest API Testing

This directory contains comprehensive test programs to validate the new `areas_of_interest` parameter in the chat/rag API endpoint and ensure compatibility with the new `.env` configuration system.

## Overview

The backend has been refactored to:
1. **Remove hardcoded California areas of interest** from `RAGService`
2. **Make areas_of_interest configurable** via the API request
3. **Pass the parameter through** the entire call chain to the geo_ner package
4. **Use the new .env configuration system** for environment management
5. **Support multiple areas of interest** with OR logic

## Files

- `test_areas_of_interest.py` - Main comprehensive test program
- `example_usage.py` - Simple usage examples and learning
- `test_frontend_integration.py` - Frontend integration testing
- `debug_request.py` - Debug and troubleshooting script
- `run_all_tests.py` - Test runner for complete test suite
- `test_requirements.txt` - Python dependencies for testing
- `TEST_README.md` - This file

## Setup

1. **Install test dependencies:**
   ```bash
   pip install -r test_requirements.txt
   ```

2. **Ensure the new configuration system is working:**
   - Backend should be using `.env` or `.env.production` files
   - No more `secrets.toml` dependency
   - Environment variables loaded automatically

3. **Get an authentication token:**
   - Log in through the frontend (username: david, password: Connie97)
   - Or use the auth endpoint to get a token
   - Update `AUTH_TOKEN` in `example_usage.py` if needed

4. **Ensure the backend is running:**
   ```bash
   # In backend directory
   python main.py
   # Or use uvicorn
   uvicorn main:app --reload --port 8000
   ```

## Running the Tests

### Complete Test Suite
```bash
python run_all_tests.py
```
- Runs all test files in sequence
- Provides comprehensive summary of results
- Automatic timeout handling (5 minutes per test)
- Clear pass/fail status for each test

### Comprehensive Testing
```bash
python test_areas_of_interest.py
```
- Tests 5 different scenarios
- Provides detailed analysis of enhancement results
- Uses emojis for clear visual feedback
- Automatic enhancement validation

### Usage Examples
```bash
python example_usage.py
```
- Shows 5 different usage patterns
- Step-by-step enhancement analysis
- Learning-focused examples
- Clear expected vs. actual results

### Frontend Integration Testing
```bash
python test_frontend_integration.py
```
- Tests single area filtering
- Tests multiple areas filtering
- Tests no filtering scenarios
- Validates frontend can use the API correctly

### Debug and Troubleshooting
```bash
python debug_request.py
```
- Tests minimal requests
- Tests areas_of_interest requests
- Tests invalid payloads
- Detailed error analysis

## Test Scenarios

### Test 1: No areas_of_interest
- **Purpose**: Verify that when no filtering is applied, all geographic entities are processed
- **Expected**: All locations (San Francisco, Los Angeles, New York City, Boston, etc.) should be enhanced
- **Configuration**: `areas_of_interest: null`

### Test 2: California only
- **Purpose**: Verify that only California locations are enhanced
- **Expected**: San Francisco, Los Angeles should be enhanced; other locations should not
- **Coordinates**: 32.50° to 42.10° lat, -124.50° to -114.10° lon
- **Configuration**: Single area in areas_of_interest

### Test 3: California + New York
- **Purpose**: Verify that locations in either California OR New York are enhanced
- **Expected**: San Francisco, Los Angeles, New York City, Boston should be enhanced
- **Coordinates**: 
  - California: 32.50° to 42.10° lat, -124.50° to -114.10° lon
  - New York: 40.4774° to 40.9176° lat, -74.2591° to -73.7004° lon
- **Configuration**: Multiple areas in areas_of_interest (OR logic)

### Test 4: Three areas (California + New York + Florida)
- **Purpose**: Verify that locations in any of the three areas are enhanced
- **Expected**: Locations in California, New York, or Florida should be enhanced
- **Coordinates**: 
  - Florida: 24.3963° to 31.0000° lat, -87.6348° to -79.9743° lon
- **Configuration**: Three areas in areas_of_interest (OR logic)

### Test 5: Edge cases
- **Purpose**: Test boundary conditions and edge cases
- **Examples**: 
  - San Diego (southern California boundary)
  - Eureka (northern California boundary)
  - Tijuana (just outside California)
  - Reno (just east of California)

## Expected Behavior

### With areas_of_interest specified:
- **Inside areas**: Geographic entities should be enhanced with Geo-XML tags
- **Outside areas**: Geographic entities should remain as plain text (not enhanced)
- **Multiple areas**: OR logic applies (entity in ANY area gets enhanced)

### Without areas_of_interest:
- **All entities**: All geographic entities should be enhanced regardless of location

## New Configuration System Benefits

### Environment Management
- **Local development**: Uses `.env` file
- **Production**: Uses `.env.production` file
- **Automatic loading**: No manual environment variable configuration needed
- **Azure ready**: Works seamlessly with Azure App Service

### Secret Management
- **No more secrets.toml**: Replaced with standard .env files
- **Secure deployment**: Secrets deployed with application code
- **Environment isolation**: Different configs for different environments

### Deployment
- **Azure App Service**: No environment variables to configure
- **GitHub Actions**: Automatic deployment with secrets included
- **Zero manual configuration**: Fully automated deployment

## Validation

The test programs will show:
1. **Input text** being tested
2. **API response** from the backend
3. **Enhanced user message** showing which entities were processed
4. **Automatic analysis** of enhancement results
5. **Clear success/failure indicators** with emojis
6. **Any errors** that occur during testing

## Troubleshooting

### Common Issues:

1. **Authentication Error (401)**
   - Ensure backend is using correct credentials from .env files
   - Check if Azure API keys are valid and active
   - Token may have expired - get a new one

2. **Connection Error**
   - Ensure backend is running on port 8000
   - Check if the URL in the test program matches your backend
   - Verify .env configuration is loading correctly

3. **Timeout Errors**
   - The geo_ner processing can take time (increased timeout to 60s)
   - Check if Azure NER API is responding
   - Verify Azure API keys are active

4. **No Geographic Entities Detected**
   - Check if Azure NER API keys are configured in .env files
   - Verify the geo_ner package is working correctly
   - Check backend logs for configuration loading issues

5. **Configuration Loading Issues**
   - Ensure .env files are in the correct location (backend directory)
   - Check file permissions and syntax
   - Verify APP_ENV is set correctly

## API Changes Made

### Backend Refactoring:

1. **ChatRequest Model** (`models/chat_models.py`)
   - Added `areas_of_interest: Optional[List[Dict[str, float]]] = None`

2. **RAGService** (`services/rag_service.py`)
   - Removed hardcoded `CALIFORNIA_AREAS_OF_INTEREST` constant
   - Updated `_geo_enhance_text()` to accept `areas_of_interest` parameter
   - Updated `chat()` method to accept and pass through `areas_of_interest`

3. **Main API** (`main.py`)
   - Updated `/chat/rag` endpoint to pass `areas_of_interest` to RAG service

4. **Configuration System** (`config/settings.py`)
   - Replaced `secrets.toml` with `.env` file loading
   - Added support for `.env.production` for Azure deployment
   - Automatic environment detection and file loading

### Parameter Format:

```python
areas_of_interest = [
    {
        'min_lat': 32.50,    # Southern boundary
        'max_lat': 42.10,    # Northern boundary
        'min_lon': -124.50,  # Western boundary
        'max_lon': -114.10,  # Eastern boundary
    }
]
```

## Test Output Format

All test programs now use a consistent emoji-based output format:

- ✅ **Success indicators**
- ❌ **Error indicators** 
- 🎯 **Target/expected results**
- 🚫 **Excluded/blocked results**
- 📝 **Text/content display**
- 🤖 **AI/automated responses**
- 🧪 **Testing indicators**
- ⚠️ **Warning indicators**

## Test Suite Runner

The `run_all_tests.py` script provides:

- **Automated execution** of all test files
- **Sequential testing** with proper isolation
- **Timeout handling** (5 minutes per test)
- **Comprehensive reporting** with pass/fail status
- **Error capture** and detailed output
- **Success rate calculation** and summary

## Notes

- The `areas_of_interest` parameter is **optional** - if not provided, no geographic filtering is applied
- Multiple areas use **OR logic** - entities in ANY area are enhanced
- The filtering happens in the **geo_ner package** after geocoding but before HTML transformation
- All geographic entity types are normalized to **LOC tags** before filtering
- **Increased timeouts** to 60 seconds for GeoNER processing
- **Enhanced error handling** with detailed response analysis
- **Automatic enhancement analysis** for better validation
- **Configuration compatibility** with new .env system
- **Complete test suite** available for automated testing
