#!/usr/bin/env python3
"""
Entity Normalization Module

This module normalizes all geographic entity types (GPE, LOC, address) to the "LOC" tag
before geocoding. This ensures consistency regardless of which NER systems are configured.
"""

import re
from typing import Tuple
import logging

# Set up basic logging for standalone testing
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def normalize_geo_entities(tagged_text: str) -> Tuple[str, bool]:
    """
    Normalize all geographic entity types to "LOC" tag.
    
    Converts GPE, LOC, and address tags to LOC tags to ensure consistency
    before geocoding. This normalization is fixed and always occurs.
    
    Args:
        tagged_text (str): Text with XML tags around geographic entities
        
    Returns:
        Tuple[str, bool]: (normalized_text, has_entities)
            - normalized_text: Text with all geographic entities normalized to LOC tags
            - has_entities: True if any geographic entities were found and normalized
    """
    if not tagged_text or not tagged_text.strip():
        return tagged_text, False
    
    logger.debug(f"Normalizing geographic entities in text of length {len(tagged_text)} characters")
    
    # Pattern to match any geographic entity tag (GPE, LOC, address)
    # This handles both opening and closing tags
    geo_entity_pattern = r'<(GPE|LOC|address)([^>]*)>'
    
    # Find all geographic entity tags
    matches = list(re.finditer(geo_entity_pattern, tagged_text))
    
    if not matches:
        logger.debug("No geographic entities found to normalize")
        return tagged_text, False
    
    logger.debug(f"Found {len(matches)} geographic entity tags to normalize")
    
    # Sort matches by position in reverse order to avoid index shifting
    matches.sort(key=lambda m: m.start(), reverse=True)
    
    normalized_text = tagged_text
    normalized_count = 0
    
    for match in matches:
        entity_type = match.group(1)
        attributes = match.group(2)
        
        # Only normalize if it's not already a LOC tag
        if entity_type != "LOC":
            # Replace opening tag
            old_tag = f"<{entity_type}{attributes}>"
            new_tag = f"<LOC{attributes}>"
            normalized_text = normalized_text[:match.start()] + new_tag + normalized_text[match.end():]
            
            # Find and replace corresponding closing tag
            # Look for the closing tag after this opening tag
            remaining_text = normalized_text[match.start():]
            closing_pattern = rf'</{entity_type}>'
            closing_match = re.search(closing_pattern, remaining_text)
            
            if closing_match:
                closing_start = match.start() + closing_match.start()
                closing_end = match.start() + closing_match.end()
                old_closing = f"</{entity_type}>"
                new_closing = "</LOC>"
                normalized_text = normalized_text[:closing_start] + new_closing + normalized_text[closing_end:]
                normalized_count += 1
                
                logger.debug(f"Normalized {entity_type} tag to LOC tag")
            else:
                logger.warning(f"Found opening {entity_type} tag without corresponding closing tag")
    
    if normalized_count > 0:
        logger.debug(f"Normalized {normalized_count} geographic entity tags to LOC tags")
        return normalized_text, True
    else:
        logger.debug("No normalization needed - all entities already use LOC tags")
        return normalized_text, False


def normalize_geo_entities_in_batch(tagged_texts: list[str]) -> list[Tuple[str, bool]]:
    """
    Normalize geographic entities in a batch of tagged texts.
    
    Args:
        tagged_texts (list[str]): List of texts with XML tags around geographic entities
        
    Returns:
        list[Tuple[str, bool]]: List of (normalized_text, has_entities) tuples
    """
    results = []
    for i, tagged_text in enumerate(tagged_texts):
        normalized_text, has_entities = normalize_geo_entities(tagged_text)
        results.append((normalized_text, has_entities))
        logger.debug(f"Normalized text {i+1}/{len(tagged_texts)}: {'entities found' if has_entities else 'no entities'}")
    
    return results
