"""
Air Quality Data Processing Module
Functions for retrieving and processing air quality data from Earth Engine
"""

import logging
from datetime import datetime
import ee
import pandas as pd
import numpy as np
from .config import get_config

logger = logging.getLogger(__name__)


class AirQualityProcessor:
    """Process air quality data from Google Earth Engine"""
    
    def __init__(self):
        """Initialize processor with configuration"""
        self.config = get_config()
        self.datasets = self.config.get_datasets()
        self.bounds = self.config.get_bounds()
    
    def get_no2_data(self, start_date, end_date, region=None):
        """
        Retrieve Sentinel-5P NO2 data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            region: ee.Geometry region (uses Uzbekistan bounds if None)
        
        Returns:
            ee.ImageCollection: NO2 imagery
        """
        if region is None:
            region = self.bounds
        
        collection = (
            ee.ImageCollection(self.datasets['sentinel5p']['collection'])
            .filterDate(start_date, end_date)
            .filterBounds(region)
            .select(self.datasets['sentinel5p']['band'])
        )
        
        logger.info(f"Retrieved NO2 data: {start_date} to {end_date}")
        return collection
    
    def get_co_data(self, start_date, end_date, region=None):
        """
        Retrieve Sentinel-5P CO data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            region: ee.Geometry region (uses Uzbekistan bounds if None)
        
        Returns:
            ee.ImageCollection: CO imagery
        """
        if region is None:
            region = self.bounds
        
        collection = (
            ee.ImageCollection(self.datasets['tropomi']['collection'])
            .filterDate(start_date, end_date)
            .filterBounds(region)
            .select(self.datasets['tropomi']['band'])
        )
        
        logger.info(f"Retrieved CO data: {start_date} to {end_date}")
        return collection
    
    def get_aod_data(self, start_date, end_date, region=None):
        """
        Retrieve MODIS Aerosol Optical Depth data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            region: ee.Geometry region (uses Uzbekistan bounds if None)
        
        Returns:
            ee.ImageCollection: AOD imagery
        """
        if region is None:
            region = self.bounds
        
        collection = (
            ee.ImageCollection(self.datasets['modis_aod']['collection'])
            .filterDate(start_date, end_date)
            .filterBounds(region)
            .select(self.datasets['modis_aod']['bands'])
        )
        
        logger.info(f"Retrieved AOD data: {start_date} to {end_date}")
        return collection
    
    def compute_temporal_mean(self, image_collection):
        """
        Compute mean across temporal dimension
        
        Args:
            image_collection: ee.ImageCollection
        
        Returns:
            ee.Image: Mean image
        """
        return image_collection.mean()
    
    def compute_temporal_std(self, image_collection):
        """
        Compute standard deviation across temporal dimension
        
        Args:
            image_collection: ee.ImageCollection
        
        Returns:
            ee.Image: Standard deviation image
        """
        return image_collection.reduce(ee.Reducer.stdDev())
    
    def export_to_geotiff(self, image, filename, scale=1000, region=None):
        """
        Export image to GeoTIFF
        
        Args:
            image: ee.Image to export
            filename: Output filename
            scale: Output scale in meters
            region: Export region (uses Uzbekistan bounds if None)
        
        Returns:
            ee.batch.Task: Export task
        """
        if region is None:
            region = self.bounds
        
        export_settings = self.config.get_export_settings()
        
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=filename,
            folder=export_settings.get('folder_prefix', 'air_quality_monitoring'),
            fileNamePrefix=filename,
            scale=scale,
            region=region,
            fileFormat=export_settings.get('format', 'GeoTIFF'),
            crs='EPSG:4326',
            maxPixels=export_settings.get('max_pixels', 1e9)
        )
        
        logger.info(f"Started export task: {filename}")
        task.start()
        return task
    
    def get_city_timeseries(self, city_coords, collection, radius_m=10000, start_date=None, end_date=None):
        """
        Extract time series of air quality around a city
        
        Args:
            city_coords: [longitude, latitude]
            collection: ee.ImageCollection
            radius_m: Buffer radius in meters
            start_date: Start date for filtering
            end_date: End date for filtering
        
        Returns:
            list: Time series data
        """
        point = ee.Geometry.Point(city_coords)
        buffer = point.buffer(radius_m)
        
        if start_date:
            collection = collection.filterDate(start_date, end_date)
        
        # Reduce collection to mean values
        result = collection.map(
            lambda img: img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=buffer,
                scale=1000
            ).set('date', img.date().format('YYYY-MM-dd'))
        )
        
        logger.info(f"Extracted time series for city at {city_coords}")
        return result


def initialize_processor():
    """Initialize air quality processor"""
    return AirQualityProcessor()
