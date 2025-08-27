#!/usr/bin/env python3
"""
Azure NER System Implementation

This module implements the Microsoft Azure Named Entity Recognition system
following the BaseNERSystem interface. It uses the Azure Text Analytics v3.0 API
to detect geographic entities in text and wrap them with XML tags.
"""

import requests
import json
import re
from typing import Dict, Any, Tuple, List
from ..ner_base import BaseNERSystem
from ..logging_config import get_logger


class AzureNERSystem(BaseNERSystem):
    """
    Microsoft Azure-based Named Entity Recognition system.
    
    This system uses Azure Text Analytics v3.0 API to detect Location and Address
    entities in text and wraps them with XML tags (GPE, LOC, address).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Azure NER system.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary containing:
                - azure_language_key: Azure Language API key
                - azure_language_endpoint: Azure Language API endpoint
                - target_entities: List of entity types to detect (default: ["Location", "Address"])
                - confidence_threshold: Minimum confidence score (default: 0.8)
        """
        super().__init__("AZURE_NER", config)
        
        # Load Azure configuration
        self.api_key = config.get("azure_language_key")
        self.endpoint = config.get("azure_language_endpoint")
        
        if not self.api_key:
            self.logger.error("Azure Language API key not provided in configuration")
            raise ValueError("Azure Language API key is required")
            
        if not self.endpoint:
            self.logger.error("Azure Language endpoint not provided in configuration")
            raise ValueError("Azure Language endpoint is required")
            
        # Ensure endpoint ends with slash for proper URL construction
        if not self.endpoint.endswith('/'):
            self.endpoint += '/'
            
        # Set target entities and confidence threshold
        self.target_entities = set(config.get("target_entities", ["Location", "Address"]))
        confidence_threshold = config.get("confidence_threshold", 0.8)
        # Ensure confidence threshold is a float
        if isinstance(confidence_threshold, str):
            try:
                self.confidence_threshold = float(confidence_threshold)
            except ValueError:
                self.logger.warning(f"Invalid confidence threshold '{confidence_threshold}', using default 0.8")
                self.confidence_threshold = 0.8
        else:
            self.confidence_threshold = float(confidence_threshold)
        
        # Construct the full API URL for Text Analytics v3.0
        self.api_url = f"{self.endpoint}text/analytics/v3.0/entities/recognition/general"
        
        self.logger.info(f"Initialized Azure NER system with endpoint: {self.endpoint}")
        self.logger.info(f"Target entities: {self.target_entities}")
        self.logger.info(f"Confidence threshold: {self.confidence_threshold}")
        
    def process_text(self, text: str) -> Tuple[str, bool]:
        """
        Process text using Azure NER to detect and tag entities.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (tagged_text, has_entities)
        """
        if not text or not text.strip():
            return text, False
            
        self.logger.debug(f"Processing text of length {len(text)} characters with Azure NER")
        
        try:
            # Call Azure Text Analytics API
            entities = self._call_azure_api(text)
            
            if not entities:
                self.logger.debug("No entities found by Azure NER")
                return text, False
                
            # Filter entities by type and confidence
            filtered_entities = self._filter_entities(entities)
            
            if not filtered_entities:
                self.logger.debug("No entities passed filtering criteria")
                return text, False
                
            # Sort entities by offset to maintain text sequence
            filtered_entities.sort(key=lambda x: x['offset'])
            
            # Tag entities with XML tags
            tagged_text = self._insert_tags(text, filtered_entities)
            
            self.logger.debug(f"Tagged {len(filtered_entities)} entities in text")
            return tagged_text, True
            
        except Exception as e:
            self.logger.error(f"Error processing text with Azure NER: {e}")
            # Return original text on error
            return text, False
            
    def _call_azure_api(self, text: str) -> List[Dict[str, Any]]:
        """
        Call Azure Text Analytics API to extract entities.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            List[Dict[str, Any]]: List of entities from Azure API
        """
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        
        payload = {
            "documents": [
                {
                    "id": "1",
                    "language": "en",
                    "text": text
                }
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract entities from response
            if 'documents' in result and len(result['documents']) > 0:
                return result['documents'][0].get('entities', [])
            else:
                self.logger.warning("Unexpected API response format")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Azure API request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Azure API response: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error calling Azure API: {e}")
            raise
            
    def _filter_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter entities by type and confidence threshold.
        
        Args:
            entities (List[Dict[str, Any]]): Raw entities from Azure API
            
        Returns:
            List[Dict[str, Any]]: Filtered entities
        """
        filtered = []
        
        for entity in entities:
            entity_type = entity.get('category', 'Unknown')
            confidence = entity.get('confidenceScore', 0.0)
            
            # Check if entity type is in target entities and meets confidence threshold
            if (entity_type in self.target_entities and 
                confidence >= self.confidence_threshold):
                filtered.append(entity)
                self.logger.debug(f"Accepted entity: {entity.get('text')} ({entity_type}, confidence: {confidence})")
            else:
                self.logger.debug(f"Filtered out entity: {entity.get('text')} ({entity_type}, confidence: {confidence})")
                
        return filtered
        
    def _insert_tags(self, text: str, entities: List[Dict[str, Any]]) -> str:
        """
        Insert XML tags around detected entities in the text.
        
        Args:
            text (str): Original text
            entities (List[Dict[str, Any]]): Filtered entities to tag
            
        Returns:
            str: Text with XML tags around entities
        """
        # Create list of (start, end, text, type) tuples for tag insertion
        entity_positions = []
        
        for entity in entities:
            start = entity['offset']
            end = start + entity['length']
            entity_text = entity['text']
            entity_type = entity['category']
            
            # Map Azure entity types to XML tags
            if entity_type == 'Location':
                tag = f"<LOC>{entity_text}</LOC>"
            elif entity_type == 'Address':
                tag = f"<address>{entity_text}</address>"
            else:
                # For other entity types, use lowercase tag name
                tag = f"<{entity_type.lower()}>{entity_text}</{entity_type.lower()}>"
                
            entity_positions.append((start, end, tag))
            
        # Sort by start position in forward order for proper text reconstruction
        entity_positions.sort(key=lambda x: x[0], reverse=False)
        
        # Insert tags in forward order
        result_parts = []
        last_pos = 0
        
        for start, end, tag in entity_positions:
            # Add text before entity
            result_parts.append(text[last_pos:start])
            
            # Add tagged entity
            result_parts.append(tag)
            last_pos = end
            
        # Add remaining text after last entity
        result_parts.append(text[last_pos:])
            
        return ''.join(result_parts)
        
    def get_supported_entity_types(self) -> List[str]:
        """
        Return list of entity types this system can detect.
        
        Returns:
            List[str]: List of supported entity type names
        """
        return list(self.target_entities)
        
    def is_available(self) -> bool:
        """
        Check if Azure NER system is available.
        
        Returns:
            bool: True if system is available, False otherwise
        """
        return bool(self.api_key and self.endpoint)
        
    def cleanup(self):
        """Clean up Azure NER resources."""
        # No specific cleanup needed for Azure NER
        pass
