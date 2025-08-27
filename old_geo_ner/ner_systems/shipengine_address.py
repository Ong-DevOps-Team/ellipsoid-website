#!/usr/bin/env python3
"""
ShipEngine Address Parser NER System Implementation

This module implements the ShipEngine-based address parsing system
following the BaseNERSystem interface.
"""

import re
import uuid
from typing import Dict, Any, Tuple
from ..ner_base import BaseNERSystem
from ..address_parser import AddressParser
from .shipengine_regex_fallback import ShipEngineRegexFallback
from ..logging_config import get_logger


class ShipEngineAddressSystem(BaseNERSystem):
    """
    ShipEngine-based address parsing system.
    
    This system uses the ShipEngine API to detect and tag addresses in text
    and wraps them with XML tags. When ShipEngine API is unavailable or fails,
    it falls back to regex-based detection specifically designed for ShipEngine.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ShipEngine address parser system.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary containing:
                - api_key: ShipEngine API key
                - enable_fallback: Whether to enable regex fallback (default: True)
                - timeout: API timeout in seconds (default: 10)
        """
        super().__init__("SHIPENGINE_ADDRESS", config)
        
        # Get configuration
        self.api_key = config.get("api_key")
        self.enable_fallback = config.get("enable_fallback", True)
        self.timeout = config.get("timeout", 10)
        
        # Initialize components based on configuration
        self.address_parser = None
        self.regex_fallback = None
        
        if self.api_key:
            # Try to initialize ShipEngine API parser
            try:
                self.address_parser = AddressParser(self.api_key)
                self.logger.info("Initialized ShipEngine address parser with API key")
            except Exception as e:
                self.logger.warning(f"Failed to initialize ShipEngine API parser: {e}")
                self.address_parser = None
        
        # Initialize regex fallback if enabled and no API parser available
        if self.enable_fallback and not self.address_parser:
            self.regex_fallback = ShipEngineRegexFallback()
            self.logger.info("Initialized ShipEngine regex fallback for address detection")
        
        if not self.address_parser and not self.regex_fallback:
            self.logger.warning("No address detection method available - system will be disabled")
            
    def process_text(self, text: str) -> Tuple[str, bool]:
        """
        Process text using ShipEngine address parser to detect and tag addresses.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (tagged_text, has_entities)
        """
        if not text or not text.strip():
            return text, False
        
        if not self.address_parser and not self.regex_fallback:
            self.logger.warning("Address detection system is disabled - no methods available")
            return text, False
            
        self.logger.debug(f"Processing text of length {len(text)} characters for addresses")
        
        try:
            # Try ShipEngine API first if available
            if self.address_parser:
                tagged_text = self.address_parser.tag_addresses_in_text(text)
                has_addresses = '<address>' in tagged_text
                
                if has_addresses:
                    address_count = tagged_text.count('<address>')
                    self.logger.debug(f"Found {address_count} addresses using ShipEngine API")
                    return tagged_text, has_addresses
                else:
                    self.logger.debug("No addresses found using ShipEngine API")
            
            # Fall back to regex if enabled and no addresses found via API
            if self.regex_fallback and self.enable_fallback:
                self.logger.debug("Falling back to regex-based address detection")
                tagged_text = self.regex_fallback.tag_addresses_in_text(text)
                has_addresses = '<address>' in tagged_text
                
                if has_addresses:
                    address_count = tagged_text.count('<address>')
                    self.logger.debug(f"Found {address_count} addresses using regex fallback")
                    return tagged_text, has_addresses
                else:
                    self.logger.debug("No addresses found using regex fallback")
            
            # No addresses found by any method
            return text, False
            
        except Exception as e:
            self.logger.error(f"Error processing text with address parser: {e}")
            # Return original text on error
            return text, False
        
    def get_supported_entity_types(self) -> list[str]:
        """
        Return list of entity types this system can detect.
        
        Returns:
            list[str]: List of supported entity type names
        """
        return ["address"]
        
    def is_available(self) -> bool:
        """
        Check if ShipEngine address system is available.
        
        Returns:
            bool: True if system is available, False otherwise
        """
        return self.address_parser is not None or self.regex_fallback is not None
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the system's current state.
        
        Returns:
            Dict[str, Any]: System information including availability and fallback status
        """
        return {
            "system_name": "SHIPENGINE_ADDRESS",
            "api_available": self.address_parser is not None,
            "fallback_available": self.regex_fallback is not None,
            "fallback_enabled": self.enable_fallback,
            "overall_available": self.is_available()
        }
