"""Configuration utilities for geo_ner package.

Supports configuration of multiple NER systems with configurable options
and execution order via geo_ner.cfg located in the same package directory.
"""
from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Optional, List, Any
from .logging_config import get_logger

logger = get_logger(__name__)

_CONFIG_CACHE: Optional[Dict[str, Any]] = None

PACKAGE_DIR = Path(__file__).parent
CONFIG_FILE = PACKAGE_DIR / "geo_ner.cfg"

# Default configuration values
DEFAULT_CONFIG = {
    "ENABLED_SYSTEMS": [],
    "SPACY_MODEL": "en_core_web_lg",
    "SPACY_TARGET_ENTITIES": ["GPE", "LOC"],
    "NER_LOG_LEVEL": "INFO",
    "ENABLE_PLACEHOLDER_STRATEGY": True,
    "ENABLE_NESTED_TAG_REMOVAL": True
}

# Configuration patterns
LINE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\"([^\"]+)\"\s*$")
BOOLEAN_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(true|false)\s*$", re.IGNORECASE)
NUMBER_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\d+)\s*$")


def _parse_config(text: str) -> Dict[str, Any]:
    """Parse configuration file content into a dictionary."""
    cfg: Dict[str, Any] = {}
    
    for ln_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
            
        # Try different patterns
        m = LINE_RE.match(line)
        if m:
            key, value = m.groups()
            cfg[key.upper()] = value
            continue
            
        m = BOOLEAN_RE.match(line)
        if m:
            key, value = m.groups()
            cfg[key.upper()] = value.lower() == "true"
            continue
            
        m = NUMBER_RE.match(line)
        if m:
            key, value = m.groups()
            cfg[key.upper()] = int(value)
            continue
            
        logger.warning(f"Ignoring invalid config line {ln_no}: {line!r}")
    
    return cfg


def load_config(force: bool = False) -> Dict[str, Any]:
    """Load configuration from geo_ner.cfg file with caching."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None and not force:
        return _CONFIG_CACHE
        
    if not CONFIG_FILE.exists():
        logger.warning(f"Configuration file not found at {CONFIG_FILE}. Using defaults.")
        _CONFIG_CACHE = DEFAULT_CONFIG.copy()
        return _CONFIG_CACHE
        
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
        cfg = _parse_config(text)
        
        # Process special configuration values
        if "ENABLED_SYSTEMS" in cfg:
            if cfg["ENABLED_SYSTEMS"].strip() == "":
                cfg["ENABLED_SYSTEMS"] = []
            else:
                cfg["ENABLED_SYSTEMS"] = [s.strip() for s in cfg["ENABLED_SYSTEMS"].split(",")]
            
        if "SPACY_TARGET_ENTITIES" in cfg:
            cfg["SPACY_TARGET_ENTITIES"] = [e.strip() for e in cfg["SPACY_TARGET_ENTITIES"].split(",")]
            
        if "AZURE_TARGET_ENTITIES" in cfg:
            cfg["AZURE_TARGET_ENTITIES"] = [e.strip() for e in cfg["AZURE_TARGET_ENTITIES"].split(",")]
            
        # Merge with defaults for missing values
        for key, default_value in DEFAULT_CONFIG.items():
            if key not in cfg:
                cfg[key] = default_value
                
        _CONFIG_CACHE = cfg
        
    except Exception as e:
        logger.warning(f"Failed reading config file {CONFIG_FILE}: {e}. Using defaults.")
        _CONFIG_CACHE = DEFAULT_CONFIG.copy()
        
    return _CONFIG_CACHE


def get_enabled_systems() -> List[str]:
    """Get list of enabled NER systems in execution order."""
    cfg = load_config()
    return cfg.get("ENABLED_SYSTEMS", DEFAULT_CONFIG["ENABLED_SYSTEMS"])


def is_system_enabled(system_name: str) -> bool:
    """Check if a specific NER system is enabled."""
    enabled_systems = get_enabled_systems()
    return system_name.upper() in [s.upper() for s in enabled_systems]


def get_system_config(system_name: str) -> Dict[str, Any]:
    """Get configuration for a specific NER system."""
    cfg = load_config()
    system_config = {}
    
    # Extract system-specific configuration
    system_prefix = system_name.upper()
    for key, value in cfg.items():
        if key.startswith(system_prefix + "_"):
            config_key = key[len(system_prefix + "_"):].lower()
            system_config[config_key] = value
            
    return system_config


def get_spacy_model_name(override: Optional[str] = None) -> str:
    """Return the SpaCy model name to use.

    Precedence:
      1. Explicit override argument
      2. SPACY_MODEL value in config
      3. Default constant
    """
    if override:
        return override
    cfg = load_config()
    model = cfg.get("SPACY_MODEL", DEFAULT_CONFIG["SPACY_MODEL"])
    if model != cfg.get("SPACY_MODEL"):
        logger.debug(f"Using default SpaCy model '{model}' (no SPACY_MODEL specified in config).")
    else:
        logger.debug(f"Using SpaCy model from config: {model}")
    return model


def get_spacy_target_entities(override: Optional[List[str]] = None) -> List[str]:
    """Return the target entity types for SpaCy NER."""
    if override:
        return override
    cfg = load_config()
    entities = cfg.get("SPACY_TARGET_ENTITIES", DEFAULT_CONFIG["SPACY_TARGET_ENTITIES"])
    logger.debug(f"Using SpaCy target entities: {entities}")
    return entities


def get_shipengine_config() -> Dict[str, Any]:
    """Get ShipEngine-specific configuration."""
    cfg = load_config()
    shipengine_config = {}
    
    # Extract system-specific configuration
    for key, value in cfg.items():
        if key.startswith("SHIPENGINE_"):
            config_key = key[len("SHIPENGINE_"):].lower()
            shipengine_config[config_key] = value
    
    # Add fallback configuration
    if "ENABLE_SHIPENGINE_FALLBACK" in cfg:
        shipengine_config["enable_fallback"] = cfg["ENABLE_SHIPENGINE_FALLBACK"]
    else:
        shipengine_config["enable_fallback"] = True  # Default to enabled
    
    return shipengine_config


def get_azure_ner_config() -> Dict[str, Any]:
    """Get Azure NER-specific configuration."""
    cfg = load_config()
    azure_config = {}
    
    # Extract system-specific configuration
    for key, value in cfg.items():
        if key.startswith("AZURE_"):
            config_key = key[len("AZURE_"):].lower()
            azure_config[config_key] = value
    
    # Add default values for missing configuration
    if "target_entities" not in azure_config:
        azure_config["target_entities"] = ["Location", "Address"]
    if "confidence_threshold" not in azure_config:
        azure_config["confidence_threshold"] = 0.8
    
    return azure_config


def get_placeholder_strategy_enabled() -> bool:
    """Get whether the placeholder strategy is enabled to prevent nested XML tags."""
    cfg = load_config()
    return cfg.get("ENABLE_PLACEHOLDER_STRATEGY", DEFAULT_CONFIG["ENABLE_PLACEHOLDER_STRATEGY"])


def get_nested_tag_removal_enabled() -> bool:
    """Get whether nested tag removal is enabled to clean up nested XML tags."""
    cfg = load_config()
    return cfg.get("ENABLE_NESTED_TAG_REMOVAL", DEFAULT_CONFIG["ENABLE_NESTED_TAG_REMOVAL"])
