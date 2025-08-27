#!/usr/bin/env python3
"""
Address Parser Module using ShipEngine API

This module provides functionality to detect and tag addresses in text using
the ShipEngine address parsing API. It identifies addresses and wraps them
with XML tags for further processing.
"""

import re
import requests
import logging
from typing import Dict, List, Tuple, Optional
import json
try:
    from .logging_config import get_logger
except ImportError:
    # Fallback for standalone execution
    import logging
    def get_logger(name):
        print("Using fallback logging")
        return logging.getLogger(name)


class AddressParser:
    """
    A class to handle address detection and tagging using ShipEngine API.
    
    This class is designed to work specifically with ShipEngine and does not
    provide general regex fallback functionality. Fallback logic should be
    handled by the calling NER system.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.shipengine.com"):
        """
        Initialize the Address Parser with ShipEngine API credentials.
        
        Args:
            api_key (str): ShipEngine API key (required)
            base_url (str): ShipEngine API base URL (default: "https://api.shipengine.com")
        """
        if not api_key:
            raise ValueError("ShipEngine API key is required")
        
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        # Setup logging using centralized configuration
        self.logger = get_logger(__name__)
    
    def parse_address_with_shipengine(self, text: str) -> Optional[Dict]:
        """
        Call ShipEngine API to recognize potential addresses from text.
        
        Args:
            text (str): Text that might contain an address
            
        Returns:
            Dict: Parsed address data from ShipEngine API, or None if parsing fails
        """
        try:
            url = f"{self.base_url}/v1/addresses/recognize"
            payload = {"text": text}
            
            response = requests.put(url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                # Check if ShipEngine found a valid address
                if result and result.get('address'):
                    return result
            elif response.status_code == 402:
                self.logger.warning("ShipEngine API: Address recognition requires Advanced plan or higher")
                return None
            elif response.status_code == 401:
                self.logger.error("ShipEngine API: Invalid API key")
                return None
            else:
                self.logger.warning(f"ShipEngine API returned status {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling ShipEngine API: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing ShipEngine response: {e}")
        
        return None
    
    def tag_addresses_in_text(self, text: str) -> str:
        """
        Tag addresses in text using ShipEngine API.
        
        Args:
            text (str): Text that may contain addresses
            
        Returns:
            str: Text with addresses wrapped in <address>...</address> tags
        """
        if not text or not text.strip():
            return text
            
        self.logger.debug(f"Processing text of length {len(text)} characters for addresses")
        
        # Split text into sentences for better address detection
        sentences = self._split_into_sentences(text)
        tagged_text = text
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Try to parse address using ShipEngine
            parsed_address = self.parse_address_with_shipengine(sentence)
            
            if parsed_address and parsed_address.get('address'):
                # Extract the original address text from the sentence
                address_text = self._extract_address_text_from_sentence(parsed_address, sentence)
                
                if address_text:
                    # Tag the address in the original text
                    tagged_text = self._tag_address_in_text(tagged_text, address_text)
                    self.logger.debug(f"Tagged address: {address_text}")
        
        return tagged_text
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for address detection.
        
        Args:
            text (str): Text to split
            
        Returns:
            List[str]: List of sentences
        """
        # Simple sentence splitting - can be enhanced with more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_address_text_from_sentence(self, parsed_response: Dict, original_text: str) -> Optional[str]:
        """
        Extract the original address text from a sentence based on ShipEngine response.
        
        Args:
            parsed_response (Dict): Response from ShipEngine recognize API
            original_text (str): Original text that was parsed
            
        Returns:
            str: Original address text if found, None otherwise
        """
        if not parsed_response.get('entities'):
            return None
        
        # Find address-related entities and their positions
        address_entities = []
        for entity in parsed_response['entities']:
            if entity.get('type') in ['address', 'address_line', 'city_locality', 'state_province', 'postal_code']:
                start_idx = entity.get('start_index')
                end_idx = entity.get('end_index')
                if start_idx is not None and end_idx is not None:
                    address_entities.append((start_idx, end_idx))
        
        if not address_entities:
            return None
        
        # Find the span that covers all address entities
        min_start = min(start for start, end in address_entities)
        max_end = max(end for start, end in address_entities)
        
        # Extract the text span, but expand to word boundaries
        address_text = original_text[min_start:max_end].strip()
        
        # Basic validation - should contain numbers and letters
        if len(address_text) > 10 and any(c.isdigit() for c in address_text):
            return address_text
        
        return None
    
    def _tag_address_in_text(self, text: str, address_text: str) -> str:
        """
        Tag a specific address in the text with XML tags.
        
        Args:
            text (str): Original text
            address_text (str): Address text to tag
            
        Returns:
            str: Text with address tagged
        """
        # Escape special regex characters in the address text
        escaped_address = re.escape(address_text)
        
        # Replace the address text with tagged version
        pattern = f"({escaped_address})"
        replacement = r"<address>\1</address>"
        
        return re.sub(pattern, replacement, text, count=1)
    
    def extract_tagged_addresses(self, tagged_text: str) -> List[str]:
        """
        Extract addresses that have been tagged with XML tags.
        
        Args:
            tagged_text (str): Text containing <address>...</address> tags
            
        Returns:
            List[str]: List of addresses found within tags
        """
        pattern = r'<address>(.*?)</address>'
        matches = re.findall(pattern, tagged_text, re.DOTALL)
        return matches


if __name__ == "__main__":
    # Example usage
    import os
    
    # Get API key from environment variable
    api_key = os.getenv('SHIPENGINE_API_KEY')
    if not api_key:
        print("Please set SHIPENGINE_API_KEY environment variable")
        print("Example: $env:SHIPENGINE_API_KEY = 'your_api_key_here'")
        exit(1)
    
    # Example text with addresses
    sample_text = """
    John Smith lives at 123 Main Street, Anytown, CA 90210. 
    Our office is located at 456 Oak Avenue, Suite 100, Los Angeles, CA 90001.
    Please send mail to P.O. Box 789, San Francisco, CA 94102.
    The meeting will be held in New York City next week.
    """
    
    parser = AddressParser(api_key)
    result = parser.tag_addresses_in_text(sample_text)
    
    print("Original text:")
    print(sample_text)
    print("\nTagged text:")
    print(result)
    
    # Extract tagged addresses
    addresses = parser.extract_tagged_addresses(result)
    print(f"\nFound {len(addresses)} addresses:")
    for i, addr in enumerate(addresses, 1):
        print(f"{i}. {addr}")
