# Backend Refactoring Summary: Configurable Areas of Interest

## Overview

The backend has been successfully refactored to remove hardcoded California areas of interest and make the `areas_of_interest` parameter configurable via the API. This allows users to specify custom geographic regions for entity filtering on a per-request basis.

## Changes Made

### 1. **ChatRequest Model** (`models/chat_models.py`)
- **Added**: `areas_of_interest: Optional[List[Dict[str, float]]] = None`
- **Type**: List of dictionaries, each containing `min_lat`, `max_lat`, `min_lon`, `max_lon`
- **Default**: `None` (no geographic filtering applied)

### 2. **RAGService** (`services/rag_service.py`)
- **Removed**: Hardcoded `CALIFORNIA_AREAS_OF_INTEREST` constant
- **Updated**: `_geo_enhance_text()` method signature to accept `areas_of_interest` parameter
- **Updated**: `chat()` method signature to accept and pass through `areas_of_interest`
- **Added**: Import for `List` and `Dict` types from `typing`

### 3. **Main API** (`main.py`)
- **Updated**: `/chat/rag` endpoint to extract `areas_of_interest` from request
- **Updated**: Call to `rag_service.chat()` to pass through the parameter

## Parameter Format

The `areas_of_interest` parameter follows the format expected by the geo_ner package:

```python
areas_of_interest = [
    {
        'min_lat': 32.50,    # Southern boundary
        'max_lat': 42.10,    # Northern boundary
        'min_lon': -124.50,  # Western boundary
        'max_lon': -114.10,  # Eastern boundary
    },
    # Additional areas can be specified...
]
```

## API Usage Examples

### No Geographic Filtering
```python
# All geographic entities will be processed
payload = {
    "message": "I visited San Francisco and New York City",
    "chat_history": [],
    # areas_of_interest omitted or set to None
}
```

### Single Area of Interest
```python
# Only California locations will be processed
california_area = [{
    'min_lat': 32.50, 'max_lat': 42.10,
    'min_lon': -124.50, 'max_lon': -114.10,
}]

payload = {
    "message": "I visited San Francisco and New York City",
    "chat_history": [],
    "areas_of_interest": california_area
}
```

### Multiple Areas of Interest
```python
# Locations in California OR New York will be processed
california_area = [{'min_lat': 32.50, 'max_lat': 42.10, 'min_lon': -124.50, 'max_lon': -114.10}]
newyork_area = [{'min_lat': 40.4774, 'max_lat': 40.9176, 'min_lon': -74.2591, 'max_lon': -73.7004}]

payload = {
    "message": "I visited San Francisco and New York City",
    "chat_history": [],
    "areas_of_interest": california_area + newyork_area
}
```

## Behavior Changes

### Before Refactoring
- **Hardcoded**: California area of interest was always applied
- **Fixed**: Geographic filtering could not be changed without code modification
- **Limited**: Only California locations were processed

### After Refactoring
- **Configurable**: Areas of interest can be specified per request
- **Flexible**: Multiple areas can be specified with OR logic
- **Optional**: No filtering applied when parameter is omitted
- **Extensible**: Easy to add new geographic regions

## Testing

### Test Files Created
1. **`test_areas_of_interest.py`** - Comprehensive testing program
2. **`example_usage.py`** - Simple usage examples
3. **`test_requirements.txt`** - Python dependencies
4. **`TEST_README.md`** - Testing documentation
5. **`REFACTORING_SUMMARY.md`** - This summary document

### Test Scenarios
1. **No filtering** - Verify all entities are processed
2. **Single area** - Verify only specified area entities are processed
3. **Multiple areas** - Verify OR logic works correctly
4. **Edge cases** - Test boundary conditions
5. **Error handling** - Verify graceful degradation

## Backward Compatibility

- **Existing clients**: Will continue to work (no areas_of_interest = no filtering)
- **New functionality**: Available for clients that specify areas_of_interest
- **API contract**: No breaking changes to existing endpoints

## Benefits

1. **Flexibility**: Support for any geographic region, not just California
2. **Scalability**: Easy to add new regions without code changes
3. **User Control**: Clients can specify their own areas of interest
4. **Maintainability**: No hardcoded constants to maintain
5. **Testing**: Easier to test different geographic scenarios

## Implementation Notes

- **Parameter passing**: Flows through entire call chain: API → RAGService → geo_ner package
- **Type safety**: Uses proper typing with Optional and List[Dict]
- **Error handling**: Graceful fallback when parameter is invalid
- **Performance**: No additional overhead when parameter is not specified

## Future Enhancements

- **Validation**: Add coordinate validation in the API layer
- **Caching**: Cache common area-of-interest configurations
- **Presets**: Provide common geographic region presets
- **UI Integration**: Frontend controls for area selection
