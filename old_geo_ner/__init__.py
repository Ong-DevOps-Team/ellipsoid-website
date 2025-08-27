#!/usr/bin/env python3
"""
GeoNER Package - Named Entity Recognition and Geocoding

This package provides functionality for:
- Named Entity Recognition (NER) using modular approach with multiple systems
- Geocoding of detected entities using Esri's service
- Transformation of XML tags to HTML hyperlinks

Main modules:
- text_to_geocode: Main processing pipeline
- ner_modular: Modular NER processor with multiple systems
- ner_base: Base interface for NER systems
- ner_systems: Individual NER system implementations
- address_parser: Address parsing using ShipEngine API
- geocode: Geocoding functionality using Esri API
- tagged_text_to_geotext: XML to HTML transformation
- logging_config: Logging configuration
- config: Configuration management

Note: API key management is the responsibility of the calling program.
"""

from .text_to_geocode import text_list_to_geocoded_hypertext, text_to_geocoded_hypertext, text_list_to_geotagged_text, text_to_geotagged_text
from .ner_modular import ModularNERProcessor

__version__ = "2.0.0"
__author__ = "Ellipsoid Labs"

# Make main functionality easily accessible
__all__ = [
    'text_list_to_geocoded_hypertext',
    'text_to_geocoded_hypertext',
    'text_list_to_geotagged_text',
    'text_to_geotagged_text',
    'ModularNERProcessor'  # For testing/debugging only - NOT part of public API
]

# Document the testing-only nature of ModularNERProcessor
ModularNERProcessor.__doc__ = """
ModularNERProcessor - For Testing and Debugging Only

This class is exposed for testing purposes and internal debugging.
It is NOT part of the public API and should not be used in production code.

Use the main functions instead:
- text_to_geocoded_hypertext()
- text_list_to_geocoded_hypertext()  
- text_to_geotagged_text()
- text_list_to_geotagged_text()

For testing, you can import this directly:
    from geo_ner.ner_modular import ModularNERProcessor
"""
