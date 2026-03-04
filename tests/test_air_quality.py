"""
Unit tests for air quality monitoring system
"""

import pytest
from datetime import datetime
from src.config import ConfigManager
from src.auth import GEEAuthenticator


class TestConfig:
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test that configuration loads properly"""
        config = ConfigManager()
        assert config.config is not None
    
    def test_config_get_study_area(self):
        """Test retrieving study area configuration"""
        config = ConfigManager()
        study_area = config.get_study_area()
        assert 'bounds' in study_area
        assert 'cities' in study_area
    
    def test_config_get_datasets(self):
        """Test retrieving datasets configuration"""
        config = ConfigManager()
        datasets = config.get_datasets()
        assert 'sentinel5p' in datasets
        assert 'tropomi' in datasets
        assert 'modis_aod' in datasets


class TestAuth:
    """Test authentication"""
    
    def test_auth_initialization_no_credentials(self):
        """Test that auth fails without credentials"""
        with pytest.raises(ValueError):
            authenticator = GEEAuthenticator(credentials_path="non_existent.json")


# Additional tests can be added as development progresses
