#!/usr/bin/env python3
"""
Text to Geocode Processing Module

This module handles the complete pipeline of processing text:
1. Named Entity Recognition (NER) using SpaCy
2. Geocoding of detected entities using Esri's service
3. Transformation of XML tags to HTML hyperlinks

This module consolidates the processing logic that was previously scattered
across multiple modules and the main app.py file.

Implementation Note:
- NER model selection is encapsulated within this package and not exposed to callers
- This allows for future refactoring (e.g., replacing SpaCy) without breaking the public API
- Geocoding is the primary purpose - this module always performs geocoding when entities are found
"""

from typing import List, Tuple, Optional, Dict, Union
from .ner_modular import process_text_inputs
from .geocode import process_text_with_geocoding
from .config import get_enabled_systems
from .tagged_text_to_geotext import process_geocoded_text
from .logging_config import get_logger
from .entity_normalizer import normalize_geo_entities_in_batch
import re

# Get logger for this module
logger = get_logger(__name__)


def filter_entities_by_areas_of_interest(tagged_text: str, areas_of_interest: Optional[List[Dict[str, float]]] = None) -> str:
    """
    Filter XML geo-tagged entities based on areas-of-interest bounds.
    
    Removes XML geo tags that fall outside ALL specified latitude/longitude bounds.
    An entity is kept if it falls within ANY of the specified areas.
    
    Args:
        tagged_text (str): Text with XML geo tags containing lat/lon attributes
        areas_of_interest (List[Dict[str, float]], optional): List of area-of-interest bounds, each with keys:
            - 'min_lat': Minimum latitude (float)
            - 'max_lat': Maximum latitude (float) 
            - 'min_lon': Minimum longitude (float)
            - 'max_lon': Maximum longitude (float)
            
    Returns:
        str: Text with out-of-bounds geo tags removed (entities return to plain text)
        
    Example:
        areas_of_interest = [
            {'min_lat': 40.0, 'max_lat': 45.0, 'min_lon': -75.0, 'max_lon': -70.0},  # East Coast
            {'min_lat': 32.0, 'max_lat': 38.0, 'min_lon': -125.0, 'max_lon': -115.0}  # West Coast
        ]
        # Keeps entities within either East Coast OR West Coast areas, removes others
    """
    if not areas_of_interest:
        return tagged_text
    
    # Validate areas_of_interest is a list
    if not isinstance(areas_of_interest, list):
        logger.warning(f"Invalid areas_of_interest format. Expected list, got {type(areas_of_interest)}")
        return tagged_text
    
    # Validate each area and collect valid areas
    required_keys = ['min_lat', 'max_lat', 'min_lon', 'max_lon']
    valid_areas = []
    
    for area_idx, area in enumerate(areas_of_interest):
        if not isinstance(area, dict):
            logger.warning(f"Invalid area format at index {area_idx}. Expected dict, got {type(area)}. Skipping area.")
            continue
            
        if not all(key in area for key in required_keys):
            logger.warning(f"Invalid area format at index {area_idx}. Required keys: {required_keys}. Skipping area.")
            continue
        
        # Extract and validate bounds
        try:
            min_lat, max_lat = area['min_lat'], area['max_lat']
            min_lon, max_lon = area['min_lon'], area['max_lon']
            
            if min_lat >= max_lat or min_lon >= max_lon:
                logger.warning(f"Invalid area bounds at index {area_idx}: min values must be less than max values. Skipping area.")
                continue
                
            valid_areas.append({
                'min_lat': min_lat, 'max_lat': max_lat,
                'min_lon': min_lon, 'max_lon': max_lon,
                'index': area_idx
            })
        except (KeyError, TypeError, ValueError):
            logger.warning(f"Invalid area bounds at index {area_idx}. Skipping area.")
            continue
    
    if not valid_areas:
        logger.warning("No valid areas found in areas_of_interest. Returning original text.")
        return tagged_text
    
    def is_within_any_area(lat: float, lon: float) -> bool:
        """Check if coordinates are within any of the valid areas"""
        for area in valid_areas:
            if (area['min_lat'] <= lat <= area['max_lat'] and 
                area['min_lon'] <= lon <= area['max_lon']):
                return True
        return False
    
    # Pattern to match XML geo tags with lat/lon attributes (both new and legacy formats)
    # New format: <LOC lat="40.7128" lon="-74.006" zoom_level="10">New York</LOC>
    # Legacy format: <LOC lat="37.7749" lon="-122.4194">San Francisco</LOC>
    pattern_new = r'<LOC\s+lat="([^"]+)"\s+lon="([^"]+)"\s+zoom_level="([^"]+)"[^>]*>(.*?)</LOC>'
    pattern_legacy = r'<LOC\s+lat="([^"]+)"\s+lon="([^"]+)"[^>]*>(.*?)</LOC>'
    
    def check_entity_bounds_new(match):
        lat_str, lon_str, zoom_level_str, entity_text = match.groups()
        
        # Handle "none" coordinates (entities that failed to geocode)
        if lat_str == "none" or lon_str == "none" or zoom_level_str == "none":
            # Remove the tag for entities that couldn't be geocoded
            logger.debug(f"Removing entity '{entity_text}' - no valid coordinates (geocoding failed)")
            return entity_text
        
        try:
            lat, lon = float(lat_str), float(lon_str)
            
            # Check if coordinates are within any of the areas
            if is_within_any_area(lat, lon):
                # Keep the entity tag - it's within at least one area
                logger.debug(f"Keeping entity '{entity_text}' at ({lat}, {lon}) with zoom level {zoom_level_str} - within areas-of-interest bounds")
                return match.group(0)
            else:
                # Remove the tag - return just the entity text
                logger.debug(f"Removing entity '{entity_text}' at ({lat}, {lon}) - outside all areas-of-interest bounds")
                return entity_text
        except ValueError:
            # Invalid coordinates (unexpected format) - remove the tag
            logger.warning(f"Invalid coordinates in entity tag: lat='{lat_str}', lon='{lon_str}'")
            return entity_text
    
    def check_entity_bounds_legacy(match):
        lat_str, lon_str, entity_text = match.groups()
        
        # Handle "none" coordinates (entities that failed to geocode)
        if lat_str == "none" or lon_str == "none":
            # Remove the tag for entities that couldn't be geocoded
            logger.debug(f"Removing legacy entity '{entity_text}' - no valid coordinates (geocoding failed)")
            return entity_text
        
        try:
            lat, lon = float(lat_str), float(lon_str)
            
            # Check if coordinates are within any of the areas
            if is_within_any_area(lat, lon):
                # Keep the entity tag - it's within at least one area
                logger.debug(f"Keeping legacy entity '{entity_text}' at ({lat}, {lon}) - within areas-of-interest bounds")
                return match.group(0)
            else:
                # Remove the tag - return just the entity text
                logger.debug(f"Removing legacy entity '{entity_text}' at ({lat}, {lon}) - outside all areas-of-interest bounds")
                return entity_text
        except ValueError:
            # Invalid coordinates (unexpected format) - remove the tag
            logger.warning(f"Invalid coordinates in legacy entity tag: lat='{lat_str}', lon='{lon_str}'")
            return entity_text
    
    # Apply the filter - first try new format, then legacy format
    filtered_text = re.sub(pattern_new, check_entity_bounds_new, tagged_text)
    filtered_text = re.sub(pattern_legacy, check_entity_bounds_legacy, filtered_text)
    
    return filtered_text


def process_inputs_with_ner(text_inputs: List[str], api_keys: Optional[Dict[str, str]] = None) -> List[Tuple[str, bool, str]]:
    """
    Perform Named Entity Recognition on text inputs using hybrid approach.
    
    Args:
        text_inputs (List[str]): List of text inputs to process
        api_keys (Optional[Dict[str, str]]): Dictionary of API keys:
            - 'shipengine': ShipEngine API key for address parsing
        
    Returns:
        List[Tuple[str, bool, str]]: List of (tagged_text, has_entities, text_info) tuples
    """
    logger.debug(f"Starting NER processing for {len(text_inputs)} text inputs")
    results = process_text_inputs(text_inputs, api_keys)
    entities_found = sum(1 for _, has_entities, _ in results if has_entities)
    logger.debug(f"NER processing complete. Found entities in {entities_found} out of {len(text_inputs)} inputs")
    
    # Step 1.5: Normalize all geographic entity types to LOC tags
    if entities_found > 0:
        logger.debug("Normalizing geographic entity types to LOC tags")
        tagged_texts = [result[0] for result in results]
        normalized_texts = normalize_geo_entities_in_batch(tagged_texts)
        
        # Update results with normalized text and check if normalization found entities
        updated_results = []
        for i, (_, original_has_entities, text_info) in enumerate(results):
            normalized_text, normalized_has_entities = normalized_texts[i]
            # Keep the original has_entities flag since normalization doesn't add new entities
            updated_results.append((normalized_text, original_has_entities, text_info))
        
        results = updated_results
        logger.debug("Entity normalization complete")
    
    return results


def process_inputs_with_geocoding(inputs_with_entities: List[Tuple[str, bool, str]], 
                                 esri_api_key: str,
                                 areas_of_interest: Optional[List[Dict[str, float]]] = None) -> List[Tuple[str, bool, str]]:
    """
    Step 2: Geocode the named entities in the text inputs and apply area-of-interest filtering.
    
    Takes XML-tagged entities and enriches them with geocoding information.
    Optionally filters entities based on area-of-interest bounds.
    
    Args:
        inputs_with_entities (List[Tuple[str, bool, str]]): List of (tagged_text, has_entities, text_info) tuples
        esri_api_key (str): The Esri API key for geocoding
        areas_of_interest (List[Dict[str, float]], optional): List of area-of-interest bounds for filtering entities
        
    Returns:
        List[Tuple[str, bool, str]]: List of inputs with geocoded XML tags (filtered by area-of-interest if specified)
        
    Raises:
        Exception: If geocoding fails for reasons other than invalid API key
    """
    logger.debug(f"Starting geocoding processing for {len(inputs_with_entities)} inputs")
    
    if areas_of_interest:
        logger.debug(f"Applying areas-of-interest filtering: {areas_of_interest}")
    
    geocoded_inputs = []
    
    for i, (tagged_text, has_entities, text_info) in enumerate(inputs_with_entities):
        logger.debug(f"Processing input {i+1}/{len(inputs_with_entities)}: {text_info}")
        
        if has_entities:
            try:
                logger.debug(f"Geocoding entities in: {text_info}")
                # Geocode the entities (adds coordinate information to XML tags)
                geocoded_text = process_text_with_geocoding(tagged_text, esri_api_key, areas_of_interest=areas_of_interest)
                
                # Apply area-of-interest filtering if specified
                if areas_of_interest:
                    filtered_text = filter_entities_by_areas_of_interest(geocoded_text, areas_of_interest)
                    # Check if any entities remain after filtering (all entities are now LOC tags)
                    has_entities_after_filter = '<LOC' in filtered_text
                    geocoded_inputs.append((filtered_text, has_entities_after_filter, text_info))
                    if not has_entities_after_filter:
                        logger.debug(f"All entities filtered out by area-of-interest for: {text_info}")
                else:
                    geocoded_inputs.append((geocoded_text, has_entities, text_info))
                
                logger.debug(f"Successfully geocoded {text_info}")
                
            except ValueError as e:
                # Handle invalid API key - log error clearly for system administrators/DevOps/engineers
                if "Invalid or expired API key" in str(e):
                    logger.error(f"CRITICAL: Invalid Esri API key detected for {text_info}. Geocoding will fail for all entities. Error: {e}")
                    logger.error(f"System administrators, DevOps engineers, and software engineers should check the Esri API key configuration.")
                    # Continue processing - entities will be tagged but not geocoded, then stripped out later
                    geocoded_inputs.append((tagged_text, has_entities, text_info))
                else:
                    # Re-raise other ValueError exceptions
                    logger.error(f"Geocoding error for {text_info}: {e}")
                    raise Exception(f"Error during geocoding: {e}")
                    
            except Exception as e:
                logger.error(f"Geocoding error for {text_info}: {e}")
                raise Exception(f"Error during geocoding: {e}")
        else:
            # No entities found, pass through unchanged
            logger.debug(f"No entities to geocode in: {text_info}")
            geocoded_inputs.append((tagged_text, has_entities, text_info))
    
    return geocoded_inputs


def process_inputs_with_html_transformation(geocoded_inputs: List[Tuple[str, bool, str]]) -> List[Tuple[str, bool, str]]:
    """
    Step 3: Transform geocoded XML tags into HTML hyperlinks.
    
    Converts XML tags with geocoding information into clickable map links.
    
    Args:
        geocoded_inputs (List[Tuple[str, bool, str]]): List of (geocoded_text, has_entities, text_info) tuples
        
    Returns:
        List[Tuple[str, bool, str]]: List of inputs with HTML hyperlinks
        
    Raises:
        Exception: If HTML transformation fails
    """
    logger.debug(f"Starting HTML transformation for {len(geocoded_inputs)} inputs")
    
    html_inputs = []
    
    for i, (geocoded_text, has_entities, text_info) in enumerate(geocoded_inputs):
        logger.debug(f"Transforming input {i+1}/{len(geocoded_inputs)}: {text_info}")
        
        try:
            # Transform XML tags to HTML hyperlinks
            html_text = process_geocoded_text(geocoded_text)
            html_inputs.append((html_text, has_entities, text_info))
            logger.debug(f"Successfully transformed {text_info} to HTML")
        except Exception as e:
            logger.error(f"HTML transformation error for {text_info}: {e}")
            raise Exception(f"Error during HTML transformation: {e}")
    
    return html_inputs


def filter_inputs_with_entities(results: List[Tuple[str, bool, str]]) -> List[Tuple[str, bool, str]]:
    """
    Filter results to only include inputs that contain entities.
    
    Args:
        results (List[Tuple[str, bool, str]]): List of (tagged_text, has_entities, text_info) tuples
        
    Returns:
        List[Tuple[str, bool, str]]: Filtered list containing only inputs with entities
    """
    return [result for result in results if result[1]]


def text_list_to_geocoded_hypertext(text_inputs: List[str], 
                          api_keys: Optional[Dict[str, str]] = None,
                          areas_of_interest: Optional[List[Dict[str, float]]] = None) -> List[Tuple[str, bool, str]]:
    """
    Complete 3-step pipeline for processing text inputs through NER, geocoding, and HTML transformation.
    
    Pipeline Steps:
    1. Named Entity Recognition: Detect geographical entities and wrap in XML tags
    2. Geocoding: Enrich XML tags with coordinate information using Esri API
    3. Area-of-Interest Filtering: Remove entities outside specified area-of-interest (if provided)
    4. HTML Transformation: Convert geocoded XML tags to clickable map hyperlinks
    
    Args:
        text_inputs (List[str]): List of text inputs to process
        api_keys (Optional[Dict[str, str]]): Dictionary of API keys:
            - 'shipengine': ShipEngine API key for address parsing
            - 'esri': Esri API key for geocoding
        areas_of_interest (List[Dict[str, float]], optional): List of area-of-interest bounds for filtering entities.
            Each area should contain keys: 'min_lat', 'max_lat', 'min_lon', 'max_lon'.
            Only entities within any of these areas will be returned.
        
    Returns:
        List[Tuple[str, bool, str]]: List of tuples containing:
            - processed_text (str): Text with entities converted to HTML hyperlinks for map viewing
            - has_entities (bool): True if geographical entities were found in the text, False otherwise
            - text_info (str): Sequential identifier in format "Text N" (e.g., "Text 1", "Text 2", etc.)
                              where N is the position of the input text in the original input list.
                              Used for logging, debugging, and tracking individual texts in batch processing.
        
        Example return value for one entry:
            ('I visited <a href="https://www.arcgis.com/apps/mapviewer/index.html?center=-74.006,40.7128&level=10">New York City</a> last summer.', 
            True, 'Text 1')
        
    Raises:
        Exception: If processing fails
    """
    # Steps 1 & 2: NER + Geocoding using the new reusable function
    geocoded_results = text_list_to_geotagged_text(
        text_inputs=text_inputs,
        api_keys=api_keys,
        areas_of_interest=areas_of_interest
    )
    
    # Step 3: HTML Transformation - Convert geocoded XML to clickable hyperlinks
    if geocoded_results:
        final_results = process_inputs_with_html_transformation(geocoded_results)
        return final_results
    else:
        return []


def text_list_to_geotagged_text(text_inputs: List[str], 
                               api_keys: Optional[Dict[str, str]] = None,
                               areas_of_interest: Optional[List[Dict[str, float]]] = None) -> List[Tuple[str, bool, str]]:
    """
    2-step pipeline for processing text inputs through NER and geocoding (without HTML transformation).
    
    Pipeline Steps:
    1. Named Entity Recognition: Detect geographical entities and wrap in XML tags
    2. Geocoding: Enrich XML tags with coordinate information using Esri API
    3. Area-of-Interest Filtering: Remove entities outside specified area-of-interest (if provided)
    
    Args:
        text_inputs (List[str]): List of text inputs to process
        api_keys (Optional[Dict[str, str]]): Dictionary of API keys:
            - 'shipengine': ShipEngine API key for address parsing
            - 'esri': Esri API key for geocoding
        areas_of_interest (List[Dict[str, float]], optional): List of area-of-interest bounds for filtering entities.
            Each area should contain keys: 'min_lat', 'max_lat', 'min_lon', 'max_lon'.
            Only entities within any of these areas will be returned.
        
    Returns:
        List[Tuple[str, bool, str]]: List of tuples containing:
            - geotagged_text (str): Text with entities wrapped in geocoded XML tags
            - has_entities (bool): True if geographical entities were found in the text, False otherwise
            - text_info (str): Sequential identifier in format "Text N" (e.g., "Text 1", "Text 2", etc.)
                              where N is the position of the input text in the original input list.
        
        Example return value for one entry:
            ('I visited <entity lat="40.7128" lon="-74.006">New York City</entity> last summer.', 
            True, 'Text 1')
        
    Raises:
        Exception: If processing fails
    """
    # Get API keys - no validation, let systems fail naturally
    esri_api_key = api_keys.get("esri") if api_keys else None
    
    # Step 1: Named Entity Recognition - Detect entities and wrap in XML tags
    ner_results = process_inputs_with_ner(text_inputs, api_keys)
    
    # Filter to only inputs with entities for geocoding
    inputs_with_entities = filter_inputs_with_entities(ner_results)
    
    # Step 2: Geocoding with optional area-of-interest filtering - Enrich XML tags with coordinate information
    if inputs_with_entities and esri_api_key:
        # Geocoding requested and API key provided
        geocoded_results = process_inputs_with_geocoding(inputs_with_entities, esri_api_key, areas_of_interest)
        return geocoded_results
    elif inputs_with_entities:
        # No geocoding API key, but we have entities - return NER results only
        logger.info("No Esri API key provided, returning NER results without geocoding")
        return inputs_with_entities
    else:
        return []


def text_to_geotagged_text(text_input: str, 
                           api_keys: Optional[Dict[str, str]] = None,
                           areas_of_interest: Optional[List[Dict[str, float]]] = None) -> str:
    """
    Simplified wrapper for processing a single text input through NER and geocoding (without HTML transformation).
    
    This is a convenience function that wraps text_list_to_geotagged_text for single text processing.
    
    Args:
        text_input (str): Single text input to process
        api_keys (Optional[Dict[str, str]]): Dictionary of API keys:
            - 'shipengine': ShipEngine API key for address parsing
            - 'esri': Esri API key for geocoding
        areas_of_interest (List[Dict[str, float]], optional): List of area-of-interest bounds for filtering entities.
            Each area should contain keys: 'min_lat', 'max_lat', 'min_lon', 'max_lon'.
            Only entities within any of these areas will be returned.
        
    Returns:
        str: Processed text with entities wrapped in geocoded XML tags.
             Returns the original text if no entities are found or processing fails.
        
        Example return value:
            'I visited <entity lat="40.7128" lon="-74.006">New York City</entity> last summer.'
        
    Raises:
        Exception: If processing fails
    """
    # Use the main function with a single-item list
    results = text_list_to_geotagged_text(
        text_inputs=[text_input],
        api_keys=api_keys,
        areas_of_interest=areas_of_interest
    )
    
    # Extract the geotagged text from the first (and only) result
    if results and len(results) > 0:
        geotagged_text, has_entities, text_info = results[0]
        return geotagged_text
    else:
        # If no results or no entities found, return original text
        return text_input


def text_to_geocoded_hypertext(text_input: str, 
                               api_keys: Optional[Dict[str, str]] = None,
                               areas_of_interest: Optional[List[Dict[str, float]]] = None) -> str:
    """
    Simplified wrapper for processing a single text input through NER, geocoding, and transformation.
    
    This is a convenience function that wraps text_list_to_geocoded_hypertext for single text processing.
    
    Args:
        text_input (str): Single text input to process
        api_keys (Optional[Dict[str, str]]): Dictionary of API keys:
            - 'shipengine': ShipEngine API key for address parsing
            - 'esri': Esri API key for geocoding
        areas_of_interest (List[Dict[str, float]], optional): List of area-of-interest bounds for filtering entities.
            Each area should contain keys: 'min_lat', 'max_lat', 'min_lon', 'max_lon'.
            Only entities within any of these areas will be returned.
        
    Returns:
        str: Processed text with entities converted to HTML hyperlinks for map viewing.
             Returns the original text if no entities are found or processing fails.
        
        Example return value:
            'I visited <a href="https://www.arcgis.com/apps/mapviewer/index.html?center=-74.006,40.7128&level=10">New York City</a> last summer.'
        
    Raises:
        Exception: If processing fails
    """
    # Use the main function with a single-item list
    results = text_list_to_geocoded_hypertext(
        text_inputs=[text_input],
        api_keys=api_keys,
        areas_of_interest=areas_of_interest
    )
    
    # Extract the processed text from the first (and only) result
    if results and len(results) > 0:
        processed_text, has_entities, text_info = results[0]
        return processed_text
    else:
        # If no results or no entities found, return original text
        return text_input 
    
