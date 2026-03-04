"""
Main entry point for air quality monitoring application
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/air_quality.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from .auth import initialize_gee
from .config import get_config
from .air_quality import initialize_processor
from .visualization import initialize_visualizer


class AirQualityMonitor:
    """Main application class for air quality monitoring"""
    
    def __init__(self, credentials_path=None):
        """
        Initialize Air Quality Monitor
        
        Args:
            credentials_path: Path to GEE service account credentials JSON
        """
        logger.info("Initializing Air Quality Monitor")
        
        # Initialize Earth Engine
        self.auth = initialize_gee(credentials_path)
        logger.info("Earth Engine initialized")
        
        # Load configuration
        self.config = get_config()
        logger.info("Configuration loaded")
        
        # Initialize processor and visualizer
        self.processor = initialize_processor()
        self.visualizer = initialize_visualizer()
        
        logger.info("Air Quality Monitor ready")
    
    def monitor_no2(self, start_date, end_date):
        """Monitor Nitrogen Dioxide levels"""
        logger.info(f"Monitoring NO2 from {start_date} to {end_date}")
        no2_data = self.processor.get_no2_data(start_date, end_date)
        mean_no2 = self.processor.compute_temporal_mean(no2_data)
        return mean_no2
    
    def monitor_co(self, start_date, end_date):
        """Monitor Carbon Monoxide levels"""
        logger.info(f"Monitoring CO from {start_date} to {end_date}")
        co_data = self.processor.get_co_data(start_date, end_date)
        mean_co = self.processor.compute_temporal_mean(co_data)
        return mean_co
    
    def monitor_aod(self, start_date, end_date):
        """Monitor Aerosol Optical Depth"""
        logger.info(f"Monitoring AOD from {start_date} to {end_date}")
        aod_data = self.processor.get_aod_data(start_date, end_date)
        mean_aod = self.processor.compute_temporal_mean(aod_data)
        return mean_aod
    
    def export_results(self, image, filename):
        """Export processing results"""
        return self.processor.export_to_geotiff(image, filename)


def main():
    """Main application entry point"""
    try:
        # Initialize monitor
        monitor = AirQualityMonitor()
        logger.info("Air Quality Monitoring System initialized successfully")
        return monitor
    except Exception as e:
        logger.error(f"Failed to initialize Air Quality Monitor: {str(e)}")
        raise


if __name__ == '__main__':
    monitor = main()
