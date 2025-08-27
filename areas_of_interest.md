# Areas of Interest Parameter Documentation

## Overview

The `areas_of_interest` parameter is an optional spatial filtering mechanism used in the geo_ner package's main entry point functions. It allows you to spatially filter geographic entities based on latitude/longitude boundaries, keeping only entities that fall within specified geographic regions.

## Parameter Details

### Type and Structure
- **Type**: `Optional[List[Dict[str, float]]]`
- **Default**: `None` (no filtering applied)
- **Format**: List of dictionaries, where each dictionary defines a rectangular geographic area

### Required Dictionary Keys
Each area-of-interest dictionary must contain these four required keys:

| Key | Type | Description |
|-----|------|-------------|
| `'min_lat'` | `float` | Minimum latitude (southern boundary) |
| `'max_lat'` | `float` | Maximum latitude (northern boundary) |
| `'min_lon'` | `float` | Minimum longitude (western boundary) |
| `'max_lon'` | `float` | Maximum longitude (eastern boundary) |

### Validation Rules
- `min_lat` must be less than `max_lat`
- `min_lon` must be less than `max_lon`
- All values must be valid floating-point numbers
- Invalid areas are logged and skipped, processing continues with valid areas

## How It Works

### Filtering Logic
1. **Inclusive OR Logic**: An entity is kept if it falls within **ANY** of the specified areas (not all areas)
2. **Processing Stage**: Applied after geocoding but before HTML transformation
3. **Coordinate Validation**: Entities that failed to geocode (marked with "none" coordinates) are automatically removed
4. **Graceful Degradation**: If no valid areas are provided, the original text is returned unchanged

### Pipeline Integration
The filtering is integrated into the geocoding pipeline at this stage:
1. Named Entity Recognition (NER) - detect geographic entities
2. Geocoding - add latitude/longitude coordinates to entities
3. **Areas-of-Interest Filtering** - remove entities outside specified bounds
4. HTML Transformation - convert to clickable map links (if using hypertext functions)

## Supported Functions

The `areas_of_interest` parameter is available in these four main entry point functions:

### With HTML Transformation
- `text_list_to_geocoded_hypertext()` - Process multiple texts, return HTML hyperlinks
- `text_to_geocoded_hypertext()` - Process single text, return HTML hyperlinks

### Without HTML Transformation  
- `text_list_to_geotagged_text()` - Process multiple texts, return XML tags
- `text_to_geotagged_text()` - Process single text, return XML tags

## Usage Examples

### No Areas of Interest Example
```python
from geo_ner import text_to_geocoded_hypertext

# Process text without spatial filtering (default behavior)
result = text_to_geocoded_hypertext(
    text_input="I visited New York City and Los Angeles",
    api_keys={'esri': 'your_esri_api_key'}
    # areas_of_interest parameter omitted - no filtering applied
)

# Result: "I visited <a href="...">New York City</a> and <a href="...">Los Angeles</a>"
# (Both entities are kept since no filtering is applied)

# Alternatively, explicitly set to None (same behavior)
result = text_to_geocoded_hypertext(
    text_input="I visited New York City and Los Angeles",
    api_keys={'esri': 'your_esri_api_key'},
    areas_of_interest=None  # Explicitly set to None - no filtering applied
)
```

### Basic Example - Single Region
```python
from geo_ner import text_to_geocoded_hypertext

# Define area of interest (New York metropolitan area)
areas_of_interest = [{
    'min_lat': 40.4774,   # Southern boundary
    'max_lat': 40.9176,   # Northern boundary  
    'min_lon': -74.2591,  # Western boundary
    'max_lon': -73.7004   # Eastern boundary
}]

# Process text with spatial filtering
result = text_to_geocoded_hypertext(
    text_input="I visited New York City and Los Angeles",
    api_keys={'esri': 'your_esri_api_key'},
    areas_of_interest=areas_of_interest
)

# Result: "I visited <a href="...">New York City</a> and Los Angeles"
# (Los Angeles is filtered out as it's outside the NYC area)
```

### Multiple Regions Example
```python
# Define multiple areas of interest
areas_of_interest = [
    {
        'min_lat': 40.0, 'max_lat': 45.0,
        'min_lon': -75.0, 'max_lon': -70.0
    },  # East Coast region
    {
        'min_lat': 32.0, 'max_lat': 38.0,
        'min_lon': -125.0, 'max_lon': -115.0
    },  # West Coast region
    {
        'min_lat': 25.0, 'max_lat': 31.0,
        'min_lon': -85.0, 'max_lon': -79.0
    }   # Florida region
]

# Process multiple texts
results = text_list_to_geocoded_hypertext(
    text_inputs=[
        "I traveled from Boston to Miami",
        "Then I went to Los Angeles and Seattle",
        "Finally visited Denver and Chicago"
    ],
    api_keys={'esri': 'your_esri_api_key'},
    areas_of_interest=areas_of_interest
)

# Only entities within East Coast, West Coast, or Florida regions will be kept
```

### Batch Processing Example
```python
# Process multiple texts without HTML transformation
results = text_list_to_geotagged_text(
    text_inputs=[
        "Meeting in San Francisco tomorrow",
        "Conference in Austin next week", 
        "Vacation in Hawaii planned"
    ],
    api_keys={'esri': 'your_esri_api_key'},
    areas_of_interest=[{
        'min_lat': 37.0, 'max_lat': 38.0,
        'min_lon': -123.0, 'max_lon': -122.0
    }]  # San Francisco Bay Area only
)

# Returns list of tuples: (geotagged_text, has_entities, text_info)
```

## Error Handling and Validation

### Invalid Area Handling
```python
# Example of invalid areas (will be logged and skipped)
invalid_areas = [
    {'min_lat': 45.0, 'max_lat': 40.0},  # Missing lon keys, min > max
    {'min_lat': 'invalid'},              # Non-numeric values
    "not_a_dict",                        # Wrong type
    {}                                   # Missing required keys
]

# Valid areas will still be processed, invalid ones are skipped
```

### Validation Messages
The system provides detailed logging for validation issues:
- Missing required keys: `"Invalid area format at index X. Required keys: ['min_lat', 'max_lat', 'min_lon', 'max_lon']. Skipping area."`
- Invalid bounds: `"Invalid area bounds at index X: min values must be less than max values. Skipping area."`
- Type errors: `"Invalid area format at index X. Expected dict, got <type>. Skipping area."`

## Best Practices

### 1. Coordinate System
- Use WGS84 decimal degrees (standard GPS coordinates)
- Latitude range: -90 to +90 (negative = South, positive = North)
- Longitude range: -180 to +180 (negative = West, positive = East)


## Integration Notes

### API Key Requirements
- Areas-of-interest filtering requires successful geocoding
- Ensure valid Esri API key is provided in the `api_keys` parameter
- Without geocoding, entities won't have coordinates for filtering

### Compatibility
- Works with all supported NER systems (SpaCy, Azure, ShipEngine)
- Compatible with both single-text and batch processing functions

### Output Format
- Filtered entities are completely removed (returned as plain text)
- Remaining entities retain their full geocoding information
- HTML transformation (if used) only applies to entities within areas-of-interest


## See Also

- [API Documentation](geo_ner/README.md) - Detailed function specifications
- [Configuration Guide](geo_ner/config.py) - API key and system configuration
