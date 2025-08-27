#!/usr/bin/env python3
"""
Modular NER Processor

This module provides a new modular approach to Named Entity Recognition that
can coordinate multiple NER systems based on configuration.
"""

from typing import List, Tuple, Dict, Any, Optional
from .ner_base import NERSystemRegistry
from .ner_systems import SpaCyNERSystem, ShipEngineAddressSystem, AzureNERSystem
from .config import get_enabled_systems, get_system_config, get_shipengine_config, get_azure_ner_config
from .logging_config import get_logger

logger = get_logger(__name__)


class ModularNERProcessor:
    """
    A modular NER processor that can coordinate multiple NER systems.
    
    This processor reads configuration to determine which NER systems are enabled
    and in what order they should be executed.
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize the modular NER processor.
        
        Args:
            api_keys (Optional[Dict[str, str]]): Dictionary of API keys for various services
                - 'shipengine': ShipEngine API key
                - 'esri': Esri API key (for geocoding)
        """
        self.api_keys = api_keys or {}
        self.registry = NERSystemRegistry()
        self._initialize_systems()
        
    def _initialize_systems(self):
        """Initialize and register all enabled NER systems."""
        enabled_systems = get_enabled_systems()
        logger.info(f"Initializing NER systems: {enabled_systems}")
        
        # Register SpaCy NER system if enabled
        if "SPACY_NER" in enabled_systems:
            spacy_config = get_system_config("SPACY")
            if not spacy_config:
                spacy_config = {
                    "model": "en_core_web_lg",
                    "target_entities": ["GPE", "LOC"]
                }
            spacy_system = SpaCyNERSystem(spacy_config)
            self.registry.register_system(spacy_system)
            
        # Register ShipEngine address parser if enabled
        if "SHIPENGINE_ADDRESS" in enabled_systems:
            shipengine_config = get_shipengine_config()
            if not shipengine_config:
                shipengine_config = {
                    "api_key": self.api_keys.get("shipengine"),
                    "enable_fallback": True,
                    "timeout": 10
                }
            shipengine_system = ShipEngineAddressSystem(shipengine_config)
            self.registry.register_system(shipengine_system)
            
        # Register Azure NER system if enabled
        if "AZURE_NER" in enabled_systems:
            azure_config = get_azure_ner_config()
            # Add API keys from the api_keys parameter
            if "azure_language_key" not in azure_config:
                azure_config["azure_language_key"] = self.api_keys.get("azure_language_key")
            if "azure_language_endpoint" not in azure_config:
                azure_config["azure_language_endpoint"] = self.api_keys.get("azure_language_endpoint")
                
            if not azure_config.get("azure_language_key") or not azure_config.get("azure_language_endpoint"):
                logger.warning("Azure NER system requires azure_language_key and azure_language_endpoint - skipping registration")
            else:
                try:
                    azure_system = AzureNERSystem(azure_config)
                    self.registry.register_system(azure_system)
                    logger.info("Azure NER system registered successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Azure NER system: {e}")
                    logger.warning("Azure NER system will be skipped due to initialization failure")
            
        # Set execution order
        self.registry.set_execution_order(enabled_systems)
        logger.info(f"Registered {len(self.registry.get_registered_systems())} NER systems")
        
    def process_text(self, text: str) -> Tuple[str, bool]:
        """
        Process text using all enabled NER systems in the configured order.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (tagged_text, has_entities)
        """
        if not text or not text.strip():
            return text, False
            
        logger.debug(f"Processing text of length {len(text)} characters with modular NER")
        
        # Process through all systems
        tagged_text, has_entities = self.registry.process_text_with_all_systems(text)
        
        if has_entities:
            logger.debug("Entities found in text")
        else:
            logger.debug("No entities found in text")
            
        return tagged_text, has_entities
        
    def process_chunks(self, chunks: List[str]) -> List[Tuple[str, bool, str]]:
        """
        Process multiple text chunks using the modular NER system.
        
        Args:
            chunks (List[str]): List of text chunks to process
            
        Returns:
            List[Tuple[str, bool, str]]: List of (tagged_text, has_entities, chunk_info) tuples
        """
        results = []
        for i, chunk in enumerate(chunks, 1):
            tagged_text, has_entities = self.process_text(chunk)
            results.append((tagged_text, has_entities, f"Chunk {i}"))
        return results
        
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about all registered NER systems.
        
        Returns:
            Dict[str, Any]: Information about registered systems
        """
        info = {
            "enabled_systems": get_enabled_systems(),
            "registered_systems": self.registry.get_registered_systems(),
            "system_details": {}
        }
        
        for system_name in self.registry.get_registered_systems():
            system = self.registry.get_system(system_name)
            if system:
                info["system_details"][system_name] = system.get_system_info()
                
        return info
        
    def cleanup(self):
        """Clean up all registered NER systems."""
        self.registry.cleanup_all_systems()


def process_text_inputs(texts: List[str], api_keys: Optional[Dict[str, str]] = None) -> List[Tuple[str, bool, str]]:
    """
    Convenience function to process multiple text inputs using the modular NER processor.
    
    Args:
        texts (List[str]): List of text strings to process
        api_keys (Optional[Dict[str, str]]): Dictionary of API keys
        
    Returns:
        List[Tuple[str, bool, str]]: List of (tagged_text, has_entities, chunk_info) tuples
    """
    processor = ModularNERProcessor(api_keys)
    try:
        return processor.process_chunks(texts)
    finally:
        processor.cleanup()


def process_text_input(text: str, api_keys: Optional[Dict[str, str]] = None) -> Tuple[str, bool]:
    """
    Convenience function to process a single text input using the modular NER processor.
    
    Args:
        text (str): Text string to process
        api_keys (Optional[Dict[str, str]]): Dictionary of API keys
        
    Returns:
        Tuple[str, bool]: (tagged_text, has_entities)
    """
    processor = ModularNERProcessor(api_keys)
    try:
        return processor.process_text(text)
    finally:
        processor.cleanup()
