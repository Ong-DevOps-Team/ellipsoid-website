#!/usr/bin/env python3
"""
ShipEngine Regex Fallback Module

This module provides regex-based address detection as a fallback when
the ShipEngine API is unavailable or fails. It's specifically designed
to work with the ShipEngineAddressSystem and mimics ShipEngine's expected
input/output format.
"""

import re
from typing import Dict, List, Optional
from ..logging_config import get_logger


class ShipEngineRegexFallback:
    """
    Regex-based address detection fallback for ShipEngine system.
    
    This class provides address detection using regex patterns that are
    specifically designed to work with the ShipEngine system when the
    API is unavailable.
    """
    
    def __init__(self):
        """Initialize the regex fallback system."""
        self.logger = get_logger(__name__)
        
        # Define regex patterns for US addresses (ShipEngine's primary market)
        self.address_patterns = [
            # Standard address with full components: number + street + city + state + zip
            r'\b\d{1,5}\s+[A-Za-z0-9\s,.-]+?(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?|Circle|Cir\.?|Court|Ct\.?|Place|Pl\.?|Way|Parkway|Pkwy\.?|Highway|Hwy\.?)\b[^.!?]*?[A-Za-z\s]+[,\s]+(?:[A-Z]{2}|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)\s+\d{5}(?:-\d{4})?',
            
            # More flexible pattern - address line with potential suite/apt
            r'\b\d{1,5}\s+[A-Za-z0-9\s,.-]+?(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?|Circle|Cir\.?|Court|Ct\.?|Place|Pl\.?|Way|Parkway|Pkwy\.?)(?:\s*,?\s*(?:Suite|Ste\.?|Apt\.?|Apartment|Unit|#)\s*[A-Za-z0-9-]+)?[^.!?]*?[A-Za-z\s]+[,\s]+[A-Z]{2}\s+\d{5}(?:-\d{4})?',
            
            # PO Box patterns
            r'\b(?:P\.?O\.?\s+Box|Post\s+Office\s+Box)\s+\d+[^.!?]*?[A-Za-z\s]+[,\s]+[A-Z]{2}\s+\d{5}(?:-\d{4})?',
            
            # Simpler pattern for just number + street name (less restrictive)
            r'\b\d{1,5}\s+[A-Za-z][A-Za-z0-9\s,.-]{5,50}(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?)'
        ]
    
    def detect_addresses(self, text: str) -> List[Dict]:
        """
        Detect addresses in text using regex patterns.
        
        Args:
            text (str): Text to search for addresses
            
        Returns:
            List[Dict]: List of detected addresses with ShipEngine-like format
        """
        if not text or not text.strip():
            return []
        
        self.logger.debug("Using ShipEngine regex fallback for address detection")
        
        addresses = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains address-like patterns
            if self._looks_like_address(sentence):
                # Extract address components
                address_data = self._extract_address_components(sentence)
                if address_data:
                    addresses.append(address_data)
        
        return addresses
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for address detection.
        
        Args:
            text (str): Text to split
            
        Returns:
            List[str]: List of sentences
        """
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _looks_like_address(self, text: str) -> bool:
        """
        Check if text looks like it contains an address.
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if text appears to contain an address
        """
        # Basic checks for address components
        has_number = bool(re.search(r'\b\d{1,5}\b', text))
        has_street = bool(re.search(r'\b(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?)\b', text, re.IGNORECASE))
        has_city_state_zip = bool(re.search(r'\b[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', text))
        has_po_box = bool(re.search(r'\bP\.?O\.?\s+Box\s+\d+\b', text, re.IGNORECASE))
        
        # Must have either (number + street) or PO box to be considered an address
        return (has_number and has_street) or has_po_box or has_city_state_zip
    
    def _extract_address_components(self, text: str) -> Optional[Dict]:
        """
        Extract address components from text using regex.
        
        Args:
            text (str): Text containing address
            
        Returns:
            Dict: Address data in ShipEngine-like format, or None if extraction fails
        """
        # Try to extract address line
        addr_match = re.search(r'\b\d{1,5}\s+[A-Za-z0-9\s,.-]+?(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?|Circle|Cir\.?|Court|Ct\.?|Place|Pl\.?|Way|Parkway|Pkwy\.?)', text, re.IGNORECASE)
        address_line1 = addr_match.group().strip() if addr_match else ""
        
        # Try to extract city, state, zip
        csz_match = re.search(r'\b([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b', text)
        city = csz_match.group(1).strip() if csz_match else ""
        state = csz_match.group(2) if csz_match else ""
        postal_code = csz_match.group(3) if csz_match else ""
        
        # Calculate confidence score
        score = self._calculate_confidence_score(text)
        
        # Only return if we have meaningful address data
        if address_line1 or (city and state):
            return {
                "score": score,
                "address": {
                    "address_line1": address_line1,
                    "city_locality": city,
                    "state_province": state,
                    "postal_code": postal_code,
                    "country_code": "US"
                },
                "entities": self._extract_entities(text)
            }
        
        return None
    
    def _calculate_confidence_score(self, text: str) -> float:
        """
        Calculate confidence score for address detection.
        
        Args:
            text (str): Text containing address
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # Check for various address components
        if re.search(r'\b\d{1,5}\b', text):
            score += 0.2
        if re.search(r'\b(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?)\b', text, re.IGNORECASE):
            score += 0.3
        if re.search(r'\b[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', text):
            score += 0.3
        if re.search(r'\bP\.?O\.?\s+Box\s+\d+\b', text, re.IGNORECASE):
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """
        Extract entities from text in ShipEngine-like format.
        
        Args:
            text (str): Text containing address
            
        Returns:
            List[Dict]: List of entities with position information
        """
        entities = []
        
        # Extract address line entity
        addr_match = re.search(r'\b\d{1,5}\s+[A-Za-z0-9\s,.-]+?(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Lane|Ln\.?|Drive|Dr\.?|Boulevard|Blvd\.?|Circle|Cir\.?|Court|Ct\.?|Place|Pl\.?|Way|Parkway|Pkwy\.?)', text, re.IGNORECASE)
        if addr_match:
            entities.append({
                "type": "address_line",
                "start_index": addr_match.start(),
                "end_index": addr_match.end(),
                "text": addr_match.group()
            })
        
        # Extract city entity
        city_match = re.search(r'\b([A-Za-z\s]+),\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', text)
        if city_match:
            city_start = city_match.start(1)
            city_end = city_match.end(1)
            entities.append({
                "type": "city_locality",
                "start_index": city_start,
                "end_index": city_end,
                "text": city_match.group(1).strip()
            })
        
        # Extract state entity
        if city_match:
            state_start = city_match.start(2)
            state_end = city_match.end(2)
            entities.append({
                "type": "state_province",
                "start_index": state_start,
                "end_index": state_end,
                "text": city_match.group(2)
            })
        
        # Extract postal code entity
        if city_match:
            postal_start = city_match.start(3)
            postal_end = city_match.end(3)
            entities.append({
                "type": "postal_code",
                "start_index": postal_start,
                "end_index": postal_end,
                "text": city_match.group(3)
            })
        
        return entities
    
    def tag_addresses_in_text(self, text: str) -> str:
        """
        Tag addresses in text using regex patterns.
        
        Args:
            text (str): Text that may contain addresses
            
        Returns:
            str: Text with addresses wrapped in <address>...</address> tags
        """
        if not text or not text.strip():
            return text
        
        self.logger.debug("Tagging addresses using ShipEngine regex fallback")
        
        # Find address candidates
        candidates = self._find_address_candidates(text)
        tagged_text = text
        
        # Tag each candidate
        for candidate in candidates:
            if len(candidate) > 15:  # Filter out very short matches
                # Escape special regex characters
                escaped_candidate = re.escape(candidate)
                pattern = f"({escaped_candidate})"
                replacement = r"<address>\1</address>"
                
                # Replace only the first occurrence to avoid double-tagging
                tagged_text = re.sub(pattern, replacement, tagged_text, count=1)
        
        return tagged_text
    
    def _find_address_candidates(self, text: str) -> List[str]:
        """
        Find potential address candidates in text using regex patterns.
        
        Args:
            text (str): Text to search for addresses
            
        Returns:
            List[str]: List of potential address strings
        """
        candidates = []
        
        # Use the defined address patterns - these are more precise
        for pattern in self.address_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                candidate = match.group().strip()
                # Clean up candidate - remove trailing punctuation except periods in abbreviations
                candidate = re.sub(r'[,;]\s*$', '', candidate)
                
                if len(candidate) > 15:  # Filter out very short matches
                    candidates.append(candidate)
        
        # More conservative sentence-based detection - only tag sentences that are clearly addresses
        sentences = self._split_into_sentences(text)
        for sentence in sentences:
            sentence = sentence.strip()
            # Only tag sentences that look like complete addresses
            # Must have: number + street + city, state + zip (or very strong address indicators)
            if (len(sentence) > 20 and 
                re.search(r'\b\d{1,5}\s', sentence) and 
                re.search(r'\b(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)\b', sentence, re.IGNORECASE) and
                re.search(r'\b[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', sentence)):
                # This sentence has all the components of a complete address
                candidates.append(sentence)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            candidate_clean = re.sub(r'\s+', ' ', candidate.lower().strip())
            if candidate_clean not in seen and len(candidate) > 15:
                seen.add(candidate_clean)
                unique_candidates.append(candidate)
        
        return unique_candidates
