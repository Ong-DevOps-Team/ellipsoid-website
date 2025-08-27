#!/usr/bin/env python3
"""
SpaCy NER System Implementation

This module implements the SpaCy-based Named Entity Recognition system
following the BaseNERSystem interface.
"""

import spacy
import re
import uuid
from typing import Dict, Any, Tuple
from ..ner_base import BaseNERSystem
from ..logging_config import get_logger


class SpaCyNERSystem(BaseNERSystem):
    """
    SpaCy-based Named Entity Recognition system.
    
    This system uses SpaCy models to detect GPE (Geopolitical Entity) and LOC (Location)
    entities in text and wraps them with XML tags.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SpaCy NER system.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary containing:
                - model: SpaCy model name (e.g., "en_core_web_lg")
                - target_entities: List of entity types to detect (e.g., ["GPE", "LOC"])
        """
        super().__init__("SPACY_NER", config)
        
        # Load SpaCy model
        model_name = config.get("model", "en_core_web_lg")
        try:
            self.nlp = spacy.load(model_name)
            self.logger.info(f"Loaded SpaCy model: {model_name}")
        except OSError as e:
            self.logger.error(f"Failed to load SpaCy model '{model_name}': {e}")
            raise
            
        # Set target entities
        self.target_entities = set(config.get("target_entities", ["GPE", "LOC"]))
        self.logger.info(f"Target entities: {self.target_entities}")
        
    def process_text(self, text: str) -> Tuple[str, bool]:
        """
        Process text using SpaCy NER to detect and tag entities.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (tagged_text, has_entities)
        """
        if not text or not text.strip():
            return text, False
            
        self.logger.debug(f"Processing text of length {len(text)} characters")
        
        # Run SpaCy NER
        doc = self.nlp(text)
        
        # Find entities of target types
        entity_spans = []
        for ent in doc.ents:
            if ent.label_ in self.target_entities:
                entity_spans.append((ent.start_char, ent.end_char, ent.label_))
                
        if not entity_spans:
            self.logger.debug("No target entities found in text")
            return text, False
            
        # Sort spans by start position (reverse order to avoid index shifting)
        entity_spans.sort(key=lambda x: x[0], reverse=True)
        
        # Tag entities with XML tags
        tagged_text = text
        for start, end, label in entity_spans:
            entity_text = text[start:end]
            tagged_entity = f"<{label}>{entity_text}</{label}>"
            tagged_text = tagged_text[:start] + tagged_entity + tagged_text[end:]
            
        self.logger.debug(f"Tagged {len(entity_spans)} entities in text")
        return tagged_text, True
        
    def get_supported_entity_types(self) -> list[str]:
        """
        Return list of entity types this system can detect.
        
        Returns:
            list[str]: List of supported entity type names
        """
        return list(self.target_entities)
        
    def is_available(self) -> bool:
        """
        Check if SpaCy NER system is available.
        
        Returns:
            bool: True if system is available, False otherwise
        """
        return hasattr(self, 'nlp') and self.nlp is not None
        
    def cleanup(self):
        """Clean up SpaCy resources."""
        if hasattr(self, 'nlp'):
            del self.nlp
