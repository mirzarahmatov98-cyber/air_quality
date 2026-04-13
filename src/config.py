"""
Config Management Module
Loads and manages application configuration from YAML and environment
"""

import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path=None):
        """
        Initialize Config Manager
        
        Args:
            config_path: Path to config.yaml file.
                        If None, looks for config/config.yaml relative to project root
        """
        if config_path is None:
            # Look for config.yaml in config directory
            project_root = Path(__file__).parent.parent
            config_path = project_root / 'config' / 'config.yaml'
        
        self.config_path = Path(config_path)
        self.config = {}
        self.load()
    
    def load(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            self.config = {}
    
    def get(self, key, default=None):
        """
        Get configuration value with dot notation support
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'gee.credentials_path')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_study_area(self):
        """Get Uzbekistan study area configuration"""
        return self.get('study_area', {})
    
    def get_bounds(self):
        """Get study area bounds [west, south, east, north]"""
        bounds = self.get('study_area.bounds')
        if not bounds:
            return None
        # Import ee lazily to avoid NameError if ee isn't installed
        try:
            import ee  # noqa: WPS433
            return ee.Geometry.Rectangle(bounds, 'EPSG:4326')
        except Exception:
            logger.warning("Returning raw bounds as ee is unavailable")
            return bounds
    
    def get_datasets(self):
        """Get available air quality datasets"""
        return self.get('datasets', {})
    
    def get_processing_params(self):
        """Get processing parameters"""
        return self.get('processing', {})
    
    def get_export_settings(self):
        """Get export settings"""
        return self.get('export', {})
    
    def to_dict(self):
        """Return configuration as dictionary"""
        return self.config.copy()


# Import ee for geometry operations
try:
    import ee
except ImportError:
    logger.warning("Earth Engine not available for geometry operations")


# Global config instance
_config = None


def get_config(config_path=None):
    """
    Get or create global config instance
    
    Args:
        config_path: Path to config.yaml (only used on first call)
    
    Returns:
        ConfigManager: Global configuration manager instance
    """
    global _config
    if _config is None:
        _config = ConfigManager(config_path)
    return _config
