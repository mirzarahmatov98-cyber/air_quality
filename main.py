#!/usr/bin/env python3
"""
Main script for air quality monitoring over Uzbekistan
Usage: python main.py
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from src import AirQualityMonitor
from src.config import get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_log_directory():
    """Create logs directory if it doesn't exist"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)


def main():
    """
    Main application function
    """
    create_log_directory()
    logger.info("=" * 60)
    logger.info("Starting Air Quality Monitoring System")
    logger.info("=" * 60)
    
    try:
        # Initialize the monitor
        monitor = AirQualityMonitor()
        
        # Define date range (last 6 months)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        logger.info(f"Monitoring period: {start_date} to {end_date}")
        
        # Get configuration
        config = get_config()
        study_area = config.get_study_area()
        
        logger.info(f"Study area: {study_area.get('region_name', 'Uzbekistan')}")
        logger.info("Monitoring cities:")
        for city, coords in study_area.get('cities', {}).items():
            logger.info(f"  - {city}: {coords}")
        
        # Example: Monitor NO2
        logger.info("\nGathering NO2 data...")
        no2_image = monitor.monitor_no2(start_date, end_date)
        logger.info("NO2 data retrieved successfully")
        
        # Example: Monitor CO
        logger.info("\nGathering CO data...")
        co_image = monitor.monitor_co(start_date, end_date)
        logger.info("CO data retrieved successfully")
        
        # Example: Monitor AOD
        logger.info("\nGathering AOD data...")
        aod_image = monitor.monitor_aod(start_date, end_date)
        logger.info("AOD data retrieved successfully")
        
        # Export results
        logger.info("\nExporting results...")
        monitor.export_results(no2_image, "no2_mean_uzbekistan")
        monitor.export_results(co_image, "co_mean_uzbekistan")
        monitor.export_results(aod_image, "aod_mean_uzbekistan")
        
        logger.info("\n" + "=" * 60)
        logger.info("Air Quality Monitoring completed successfully")
        logger.info("Check Google Drive for exported results")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
