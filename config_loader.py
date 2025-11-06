"""
Configuration loader for the Reddit Trading Bot
Loads and validates configuration from config.json
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages configuration from config.json"""

    _instance: Optional['ConfigLoader'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config:
            self.load_config()

    def load_config(self, config_path: str = "config.json") -> Dict[str, Any]:
        """
        Load configuration from JSON file

        Args:
            config_path: Path to config.json file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
            logger.info(f"Configuration loaded successfully from {config_path}")
            self._validate_config()
            return self._config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def _validate_config(self) -> None:
        """Validate essential configuration fields"""
        required_sections = ['reddit', 'mongodb', 'llm', 'stock_data']
        for section in required_sections:
            if section not in self._config:
                logger.warning(f"Missing section in config: {section}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key

        Example: get('reddit.client_id')

        Args:
            key: Configuration key (supports nested keys with dots)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section

        Args:
            section: Section name (e.g., 'reddit', 'mongodb')

        Returns:
            Configuration section dictionary
        """
        return self._config.get(section, {})

    def update_value(self, key: str, value: Any) -> None:
        """
        Update a configuration value at runtime

        Args:
            key: Configuration key (dot-notation)
            value: New value
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        logger.info(f"Configuration updated: {key}")

    def save_config(self, config_path: str = "config.json") -> None:
        """
        Save current configuration to file

        Args:
            config_path: Path where to save config
        """
        try:
            with open(config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {config_path}")
        except IOError as e:
            logger.error(f"Failed to save configuration: {e}")

    def __repr__(self) -> str:
        return f"ConfigLoader(config={list(self._config.keys())})"


# Convenience function
def get_config() -> ConfigLoader:
    """Get or create the global ConfigLoader instance"""
    return ConfigLoader()
