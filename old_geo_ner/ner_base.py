#!/usr/bin/env python3
"""
Base NER System Interface

This module defines the base interface that all NER systems must implement.
This allows for easy addition of new NER systems while maintaining a consistent API.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import re
import uuid
from .logging_config import get_logger
from .config import get_placeholder_strategy_enabled, get_nested_tag_removal_enabled
from .nested_tag_remover import remove_nested_geo_tags


class BaseNERSystem(ABC):
    """
    Base class for all NER systems.
    
    All NER systems must inherit from this class and implement the required methods.
    This ensures consistency across different NER implementations.
    """
    
    def __init__(self, system_name: str, config: Dict[str, Any]):
        """
        Initialize the NER system.
        
        Args:
            system_name (str): Name of the NER system
            config (Dict[str, Any]): Configuration dictionary for this system
        """
        self.system_name = system_name
        self.config = config
        self.logger = get_logger(f"{__name__}.{system_name}")
        self.logger.debug(f"Initializing {system_name} NER system with config: {config}")
        
    @abstractmethod
    def process_text(self, text: str) -> Tuple[str, bool]:
        """
        Process text and return tagged text with boolean indicating if entities were found.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (tagged_text, has_entities)
                - tagged_text: Text with XML tags around detected entities
                - has_entities: True if any entities were detected, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_entity_types(self) -> list[str]:
        """
        Return list of entity types this system can detect.
        
        Returns:
            list[str]: List of supported entity type names
        """
        pass
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about this NER system.
        
        Returns:
            Dict[str, Any]: System information including name, config, and supported entities
        """
        return {
            "name": self.system_name,
            "config": self.config,
            "supported_entities": self.get_supported_entity_types()
        }
    
    def is_available(self) -> bool:
        """
        Check if this NER system is available and ready to use.
        
        Returns:
            bool: True if system is available, False otherwise
        """
        return True
    
    def cleanup(self):
        """
        Clean up resources used by this NER system.
        Override in subclasses if cleanup is needed.
        """
        pass


class NERSystemRegistry:
    """
    Registry for managing multiple NER systems.
    
    This class handles the registration, configuration, and execution of multiple NER systems
    in the order specified by the configuration.
    """
    
    def __init__(self):
        """Initialize the NER system registry."""
        self.systems: Dict[str, BaseNERSystem] = {}
        self.execution_order: list[str] = []
        self.logger = get_logger(__name__)
        
    def _create_placeholders_for_existing_tags(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Create placeholders for existing XML tags to prevent nested tagging.
        
        Args:
            text (str): Text that may contain XML tags
            
        Returns:
            Tuple[str, Dict[str, str]]: (text_with_placeholders, placeholder_mapping)
        """
        placeholders = {}
        placeholder_text = text
        
        # Find all XML tags and replace with placeholders
        tag_pattern = r'<(\w+)(?:\s[^>]*)?>(.*?)</\1>'
        for match in re.finditer(tag_pattern, text, re.DOTALL):
            full_match = match.group(0)  # The full tag
            tag_name = match.group(1)    # Tag name (e.g., "GPE", "LOC", "address")
            placeholder = f"TAG_PLACEHOLDER_{tag_name}_{uuid.uuid4().hex[:8]}"
            placeholders[placeholder] = full_match
            placeholder_text = placeholder_text.replace(full_match, placeholder, 1)
            
        self.logger.debug(f"Created {len(placeholders)} tag placeholders")
        return placeholder_text, placeholders
        
    def _restore_placeholders(self, text: str, placeholders: Dict[str, str]) -> str:
        """
        Restore original XML tags from placeholders.
        
        Args:
            text (str): Text with placeholders
            placeholders (Dict[str, str]): Mapping of placeholders to original tags
            
        Returns:
            str: Text with placeholders replaced by original tags
        """
        restored_text = text
        for placeholder, original_tag in placeholders.items():
            restored_text = restored_text.replace(placeholder, original_tag)
            
        self.logger.debug(f"Restored {len(placeholders)} tag placeholders")
        return restored_text
        
    def register_system(self, system: BaseNERSystem):
        """
        Register an NER system.
        
        Args:
            system (BaseNERSystem): The NER system to register
        """
        self.systems[system.system_name] = system
        self.logger.debug(f"Registered NER system: {system.system_name}")
        
    def set_execution_order(self, order: list[str]):
        """
        Set the execution order for NER systems.
        
        Args:
            order (list[str]): List of system names in execution order
        """
        self.execution_order = order
        self.logger.debug(f"Set NER system execution order: {order}")
        
    def get_system(self, system_name: str) -> Optional[BaseNERSystem]:
        """
        Get a registered NER system by name.
        
        Args:
            system_name (str): Name of the system to retrieve
            
        Returns:
            Optional[BaseNERSystem]: The requested system or None if not found
        """
        return self.systems.get(system_name)
        
    def process_text_with_all_systems(self, text: str) -> Tuple[str, bool]:
        """
        Process text through all enabled NER systems in the specified order.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (final_tagged_text, has_entities)
        """
        if not self.execution_order:
            self.logger.warning("No NER systems configured for execution")
            return text, False
            
        # Check if placeholder strategy is enabled
        use_placeholders = get_placeholder_strategy_enabled()
        self.logger.debug(f"Placeholder strategy enabled: {use_placeholders}")
        
        if use_placeholders:
            return self._process_with_placeholders(text)
        else:
            return self._process_sequentially(text)
            
    def _process_with_placeholders(self, text: str) -> Tuple[str, bool]:
        """
        Process text using placeholder strategy to prevent nested XML tags.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (final_tagged_text, has_entities)
        """
        current_text = text
        has_entities = False
        all_placeholders = {}
        
        for system_name in self.execution_order:
            system = self.systems.get(system_name)
            if not system:
                self.logger.warning(f"NER system '{system_name}' not found in registry")
                continue
                
            if not system.is_available():
                self.logger.warning(f"NER system '{system_name}' is not available, skipping")
                continue
                
            try:
                self.logger.debug(f"Processing text with {system_name}")
                
                # Create placeholders for existing tags before processing
                placeholder_text, new_placeholders = self._create_placeholders_for_existing_tags(current_text)
                
                # Process with current system
                tagged_text, entities_found = system.process_text(placeholder_text)
                
                # Update placeholders and current text
                all_placeholders.update(new_placeholders)
                current_text = tagged_text
                has_entities = has_entities or entities_found
                
                if entities_found:
                    self.logger.debug(f"{system_name} found entities in text")
                    
            except Exception as e:
                self.logger.error(f"Error processing text with {system_name}: {e}")
                # Continue with other systems
                
        # Restore all placeholders at the end
        if all_placeholders:
            current_text = self._restore_placeholders(current_text, all_placeholders)
            
        # Apply nested tag removal if enabled
        if get_nested_tag_removal_enabled():
            self.logger.debug("Applying nested tag removal")
            current_text = remove_nested_geo_tags(current_text)
        else:
            self.logger.debug("Nested tag removal disabled")
            
        return current_text, has_entities
        
    def _process_sequentially(self, text: str) -> Tuple[str, bool]:
        """
        Process text sequentially without placeholder strategy (may result in nested tags).
        
        Args:
            text (str): Input text to process
            
        Returns:
            Tuple[str, bool]: (final_tagged_text, has_entities)
        """
        current_text = text
        has_entities = False
        
        for system_name in self.execution_order:
            system = self.systems.get(system_name)
            if not system:
                self.logger.warning(f"NER system '{system_name}' not found in registry")
                continue
                
            if not system.is_available():
                self.logger.warning(f"NER system '{system_name}' is not available, skipping")
                continue
                
            try:
                self.logger.debug(f"Processing text with {system_name}")
                tagged_text, entities_found = system.process_text(current_text)
                current_text = tagged_text
                has_entities = has_entities or entities_found
                
                if entities_found:
                    self.logger.debug(f"{system_name} found entities in text")
                    
            except Exception as e:
                self.logger.error(f"Error processing text with {system_name}: {e}")
                # Continue with other systems
                
        # Apply nested tag removal if enabled
        if get_nested_tag_removal_enabled():
            self.logger.debug("Applying nested tag removal")
            current_text = remove_nested_geo_tags(current_text)
        else:
            self.logger.debug("Nested tag removal disabled")
            
        return current_text, has_entities
        
    def get_registered_systems(self) -> list[str]:
        """
        Get list of all registered system names.
        
        Returns:
            list[str]: List of registered system names
        """
        return list(self.systems.keys())
        
    def cleanup_all_systems(self):
        """Clean up all registered NER systems."""
        for system in self.systems.values():
            try:
                system.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up {system.system_name}: {e}")
