"""
Google Earth Engine Authentication Module
Handles authentication with service account credentials
"""

import os
import json
import logging
from pathlib import Path
import ee
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GEEAuthenticator:
    """Authenticates and initializes Google Earth Engine"""
    
    def __init__(self, credentials_path=None):
        """
        Initialize GEE Authenticator
        
        Args:
            credentials_path: Path to service account JSON key file.
                            If None, uses GEE_CREDENTIALS env variable.
        """
        self.credentials_path = credentials_path or os.getenv('GEE_CREDENTIALS')
        
        if not self.credentials_path:
            raise ValueError(
                "GEE credentials path not provided. Set GEE_CREDENTIALS "
                "environment variable or pass credentials_path argument."
            )
        
        if not Path(self.credentials_path).exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}"
            )
    
    def authenticate(self):
        """
        Authenticate with Google Earth Engine using service account
        
        Returns:
            ee.Credentials: Authenticated credentials object
        
        Raises:
            ValueError: If authentication fails
        """
        try:
            logger.info(f"Authenticating with GEE using credentials: {self.credentials_path}")
            
            # Load service account credentials
            with open(self.credentials_path, 'r') as f:
                service_account_info = json.load(f)
            
            # Create credentials from service account info
            credentials = ee.ServiceAccountCredentials(
                email=service_account_info['client_email'],
                key_data=service_account_info['private_key']
            )
            
            # Initialize Earth Engine with credentials
            ee.Initialize(credentials)
            
            logger.info("Successfully authenticated with Google Earth Engine")
            return credentials
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise ValueError(f"Failed to authenticate with GEE: {str(e)}")
    
    def verify_authentication(self):
        """
        Verify that GEE is properly authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # Try to access a simple property to verify auth
            image = ee.Image('USGS/SRTM90_V4')
            image.getInfo()
            logger.info("GEE authentication verified")
            return True
        except Exception as e:
            logger.error(f"Authentication verification failed: {str(e)}")
            return False


def initialize_gee(credentials_path=None):
    """
    Convenience function to authenticate and initialize GEE
    
    Args:
        credentials_path: Path to service account JSON key file
    
    Returns:
        ee.Credentials: Authenticated credentials object
    """
    authenticator = GEEAuthenticator(credentials_path)
    authenticator.authenticate()
    authenticator.verify_authentication()
    return authenticator
