# GeoNER Package - Developer Quick Start

A Python package for Named Entity Recognition (NER) and geocoding of geographical entities in text.   This is a concise Quick Start guide for developers who plan to 
use the geo_ner module in their projects.

## What it does

The `geo_ner` package processes text to:
1. **Extract geographical entities** using configurable NER systems (Azure NER + SpaCy + ShipEngine)
2. **Normalize all entity types** to standardized LOC tags (GPE, address → LOC)
3. **Geocode locations** using Esri's geocoding service
4. **Generate interactive map links** or tagged XML output

## Installation & Setup

### 1. Install Dependencies
```bash
pip install spacy requests toml
# Download SpaCy English model (default: en_core_web_lg)
python -m spacy download en_core_web_lg
```

### 2. Get API Keys
- **Azure Language API Key**: Sign up at [Azure Portal](https://portal.azure.com/) (**required** for current default configuration)
- **Esri API Key**: Sign up at [developers.arcgis.com](https://developers.arcgis.com) (required for geocoding)
- **ShipEngine API Key**: Sign up at [shipengine.com](https://www.shipengine.com/) (optional when enabled, improves address parsing)

## Processing Pipeline

The `geo_ner` package processes text through these steps:

1. **Named Entity Recognition (NER)**: 
   - **Azure NER Service** (default): Detects Location and Address entities using Microsoft's AI
   - **SpaCy**: Detects GPE and LOC entities (when enabled)
   - **ShipEngine**: Parses address entities (when enabled)
   - Entities are wrapped in XML tags (`<Location>`, `<Address>`, `<GPE>`, `<LOC>`, `<address>`)

2. **Entity Normalization** (Automatic & Fixed):
   - All geographic entity types are converted to standardized LOC tags
   - `<Location>Seattle</Location>` → `<LOC>Seattle</LOC>` (Azure NER)
   - `<Address>123 Main St</Address>` → `<LOC>123 Main St</LOC>` (Azure NER)
   - `<GPE>New York</GPE>` → `<LOC>New York</LOC>` (SpaCy)
   - `<address>123 Main St</address>` → `<LOC>123 Main St</LOC>` (ShipEngine)
   - This step ensures consistency for downstream processing
   - **Note**: Normalization is a fixed processing step that always occurs and cannot be disabled via configuration

3. **Geocoding**: 
   - LOC tags are enriched with latitude/longitude coordinates
   - Results: `<LOC lat="40.7128" lon="-74.006" zoom_level="10">New York</LOC>`

4. **Output Generation**:
   - XML format: Geocoded LOC tags with coordinates
   - HTML format: Interactive map links using Esri Online Map Viewer

## Configuration

The package behavior is controlled via `geo_ner/geo_ner.cfg`:

```ini
# Enable/disable NER systems (Current Default Configuration)
ENABLED_SYSTEMS = "AZURE_NER"

# SpaCy configuration (when enabled)
ENABLE_SPACY_NER = true
SPACY_MODEL = "en_core_web_lg"
SPACY_TARGET_ENTITIES = "GPE,LOC"

# ShipEngine configuration (when enabled)
ENABLE_SHIPENGINE_ADDRESS = false

# Azure NER configuration (default enabled)
ENABLE_AZURE_NER = true
AZURE_TARGET_ENTITIES = "Location,Address"
AZURE_CONFIDENCE_THRESHOLD = "0.8"

# Nested tag handling
ENABLE_PLACEHOLDER_STRATEGY = true
ENABLE_NESTED_TAG_REMOVAL = true
```

## API Reference

### Import
```python
from geo_ner import (
    text_to_geocoded_hypertext,         # Single text → HTML with map links
    text_list_to_geocoded_hypertext,    # Text list → HTML with map links  
    text_to_geotagged_text,             # Single text → XML tagged entities
    text_list_to_geotagged_text,        # Text list → XML tagged entities
    normalize_geo_entities,              # Normalize entity types to LOC tags
    normalize_geo_entities_in_batch     # Batch normalization
)
```

### Entry Points

#### 1. Full Pipeline (HTML with Interactive Map Links)

**Single Text Processing:**
```python
result = text_to_geocoded_hypertext(
    text_input="Visit us at 123 Main St, Boston, MA",
    api_keys={
        "shipengine": "your_shipengine_key",  # Optional
        "esri": "your_esri_key",             # Required
        "azure_language_key": "your_azure_key",      # Optional
        "azure_language_endpoint": "your_azure_endpoint"  # Optional
    },
    areas_of_interest=[                       # Optional: areas-of-interest filter
        {
            'min_lat': 40.0, 'max_lat': 45.0,    # New England area
            'min_lon': -75.0, 'max_lon': -70.0   # Longitude bounds  
        }
    ]
)
# Returns: str (HTML with clickable map links)
```

**Batch Text Processing:**
```python
results = text_list_to_geocoded_hypertext(
    text_inputs=["Text 1 with NYC", "Text 2 with LA"],
    api_keys={
        "shipengine": "your_shipengine_key",  # Optional  
        "esri": "your_esri_key",             # Required
        "azure_language_key": "your_azure_key",      # Optional
        "azure_language_endpoint": "your_azure_endpoint"  # Optional
    },
    areas_of_interest=[                       # Optional: areas-of-interest filter
        {
            'min_lat': 35.0, 'max_lat': 45.0,    # Keep East Coast entities only
            'min_lon': -80.0, 'max_lon': -70.0
        }
    ]
)
# Returns: List[Tuple[str, bool, str]] 
# Each tuple: (html_text, has_entities, text_info)
```

#### 2. Partial Pipeline (XML Tagged Entities Only)

**Single Text Processing:**
```python
result = text_to_geotagged_text(
    text_input="Visit us at 123 Main St, Boston, MA",
    api_keys={
        "shipengine": "your_shipengine_key",  # Optional
        "esri": "your_esri_key",             # Required
        "azure_language_key": "your_azure_key",      # Optional
        "azure_language_endpoint": "your_azure_endpoint"  # Optional
    },
    areas_of_interest=[                       # Optional: areas-of-interest filter
        {
            'min_lat': 40.0, 'max_lat': 45.0,    # Only return entities in this region
            'min_lon': -75.0, 'max_lon': -70.0
        }
    ]
)
# Returns: str (XML with geo tags including lat/lon attributes)
```

**Batch Text Processing:**
```python
results = text_list_to_geotagged_text(
    text_inputs=["Text 1 with NYC", "Text 2 with LA"],
    api_keys={
        "shipengine": "your_shipengine_key",  # Optional
        "esri": "your_esri_key",             # Required
        "azure_language_key": "your_azure_key",      # Optional
        "azure_language_endpoint": "your_azure_endpoint"  # Optional
    },
    areas_of_interest=[                       # Optional: areas-of-interest filter
        {
            'min_lat': 32.0, 'max_lat': 49.0,    # Keep West Coast entities only
            'min_lon': -125.0, 'max_lon': -115.0
        }
    ]
)
# Returns: List[Tuple[str, bool, str]]
# Each tuple: (tagged_text, has_entities, text_info)
```

## Quick Examples

### Basic Usage
```python
from geo_ner import text_to_geocoded_hypertext

# Process text with locations (requires Azure NER for current default configuration)
result = text_to_geocoded_hypertext(
    text_input="Our office is in San Francisco, CA at 123 Market Street.",
    api_keys={
        "esri": "your_esri_key",
        "azure_language_key": "your_azure_key",
        "azure_language_endpoint": "your_azure_endpoint"
    }
)

print(result)  # HTML with clickable map links
```

### Azure NER Enhanced Detection
```python
from geo_ner import text_to_geotagged_text

# Process text with Azure NER for enhanced location detection
result = text_to_geotagged_text(
    text_input="I visited Microsoft headquarters in Seattle, Washington last week.",
    api_keys={
        "esri": "your_esri_key",
        "azure_language_key": "your_azure_key",
        "azure_language_endpoint": "your_azure_endpoint"
    }
)

print(result)  # XML with enhanced location detection from Azure NER
```

### Batch Processing
```python
from geo_ner import text_list_to_geocoded_hypertext

texts = [
    "Conference in Boston, MA",
    "Meeting at 456 Oak Ave, Seattle, WA", 
    "Visit our NYC headquarters"
]

# Define areas-of-interest (East Coast and West Coast)
multi_region_areas_of_interest = [
    {   # East Coast
        'min_lat': 35.0, 'max_lat': 45.0,
        'min_lon': -80.0, 'max_lon': -70.0
    },
    {   # West Coast  
        'min_lat': 32.0, 'max_lat': 49.0,
        'min_lon': -125.0, 'max_lon': -115.0
    }
]

results = text_list_to_geocoded_hypertext(
    text_inputs=texts,
    api_keys={
        "shipengine": "your_shipengine_key",
        "esri": "your_esri_key",
        "azure_language_key": "your_azure_key",
        "azure_language_endpoint": "your_azure_endpoint"
    },
    areas_of_interest=multi_region_areas_of_interest  # East Coast OR West Coast entities
)

for html_text, has_entities, text_info in results:
    if has_entities:
        print(f"{text_info}: {html_text}")
```

## Key Features

### Multi-NER System Integration
- **Azure NER Service**: Microsoft's AI-powered location and address detection
- **SpaCy NER**: Advanced NLP-based entity recognition for GPE and LOC entities
- **ShipEngine API**: Specialized address parsing and validation
- **Configurable Execution**: Enable/disable systems independently via `geo_ner.cfg`
- **Seamless Coordination**: All systems work together without conflicts

### Entity Normalization
- **Automatic Standardization**: All geographic entity types (GPE, LOC, address) are automatically normalized to LOC tags
- **Fixed Processing Step**: Normalization occurs after NER detection but before geocoding
- **Consistent Output**: Ensures all downstream processing works with a single entity type
- **Standalone Functions**: Available as `normalize_geo_entities()` and `normalize_geo_entities_in_batch()` for custom workflows

### API Key Management
- **Azure Language API Key**: **Required** for current default configuration (Azure NER only)
- **Azure Language Endpoint**: **Required** with Azure key for API access
- **Esri API Key**: Required for geocoding. Without it, functions will fail gracefully
- **ShipEngine API Key**: Optional when enabled. If not provided, uses fallback address parsing
- **Unified API**: Pass all API keys in a single `api_keys` dictionary

**Note**: With the current default configuration (`ENABLED_SYSTEMS = "AZURE_NER"`), Azure API keys are required for NER functionality. Without valid Azure keys, no entity detection will occur.

### Areas-of-Interest Filtering
The optional `areas_of_interest` parameter (list of area dictionaries):
- **Filters entities** to specific geographical regions
- **Resolves ambiguous named entities** by selecting the best candidate within any of the areas
- **Supports multiple regions** - entities matching ANY area are kept (OR logic)
- **Priority-based selection** - areas earlier in the list have higher priority for candidate selection
- **Improves accuracy** for locations with multiple possible matches

**Format**: List of dictionaries, each with `min_lat`, `max_lat`, `min_lon`, `max_lon` keys.

```python
# Example: Resolve "Springfield" ambiguity with multiple possible areas
result = text_to_geocoded_hypertext(
    text_input="Ship to Springfield office",
    api_keys={
        "esri": "your_key",
        "azure_language_key": "your_azure_key",
        "azure_language_endpoint": "your_azure_endpoint"
    },
    areas_of_interest=[
        {
            'min_lat': 39.0, 'max_lat': 43.0,     # Illinois region
            'min_lon': -91.5, 'max_lon': -87.0
        },
        {
            'min_lat': 41.0, 'max_lat': 43.0,     # Massachusetts region
            'min_lon': -73.5, 'max_lon': -71.0
        }
    ]
)
# Returns Springfield entities within either IL OR MA areas (prioritizes first area in list)
```

### Nested Tag Prevention
The package automatically prevents and removes nested XML tags:
- **Placeholder strategy**: Prevents nesting during NER processing
- **Post-processing cleanup**: Removes any remaining nested tags
- **Configurable**: Both features can be enabled/disabled in `geo_ner.cfg`

### Output Formats
- **HTML**: Interactive map links with Esri Online Map Viewer
- **XML**: Tagged entities with latitude/longitude coordinates (all normalized to LOC tags)
- **Batch processing**: Handle multiple texts efficiently
- **Normalized Entities**: All geographic entities use consistent LOC tags regardless of original detection type

## Error Handling

- **Missing API keys**: Functions fail gracefully with logged debugging information
- **Invalid API keys**: Underlying API calls fail naturally with clear error messages
- **Network issues**: Appropriate exception handling for geocoding failures
- **Empty input**: Graceful handling of empty or None text inputs
- **Azure NER failures**: Falls back to other NER systems if Azure is unavailable

## Configuration Options

### NER Systems
- **Azure NER**: Microsoft's AI service for Location and Address detection
  - Configurable target entities (`Location`, `Address`)
  - Adjustable confidence thresholds (0.0 to 1.0)
  - Automatic fallback if service unavailable
- **SpaCy**: Configurable models (`en_core_web_sm`, `en_core_web_md`, `en_core_web_lg`, `en_core_web_trf`)
- **ShipEngine**: Address parsing with fallback to regex-based detection
- **Execution order**: Configurable via `ENABLED_SYSTEMS` in `geo_ner.cfg`

### Tag Handling
- **Placeholder strategy**: Prevents nested tags during processing
- **Nested tag removal**: Cleans up any remaining nested tags
- **Entity types**: Configurable target entities for SpaCy (default: GPE, LOC) and Azure NER (default: Location, Address)
- **Normalization**: All entity types are automatically converted to LOC tags after detection

## Support

For detailed documentation, examples, and troubleshooting, see the main project README.md in the parent directory.
