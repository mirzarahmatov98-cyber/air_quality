# Air Quality Monitoring System - Uzbekistan

A comprehensive Python application for tracking and monitoring air quality data over Uzbekistan using Google Earth Engine APIs.

## Overview

This project leverages Google Earth Engine's vast geospatial datasets to:
- Monitor Nitrogen Dioxide (NO2) levels using Sentinel-5P
- Track Carbon Monoxide (CO) concentrations via Copernicus data
- Measure Aerosol Optical Depth (AOD) with MODIS data
- Analyze meteorological factors using ERA5 climate data
- Generate time-series analysis for major cities
- Export results for further analysis and visualization

## Features

- **Google Earth Engine Integration**: Seamless authentication and data access using service account credentials
- **Multi-Pollutant Monitoring**: Track NO2, CO, and aerosol optical depth
- **Spatial Analysis**: Focus on specific regions, cities, or the entire country of Uzbekistan
- **Temporal Analysis**: Time-series extraction and trend analysis
- **Data Export**: GeoTIFF export to Google Drive or Cloud Storage
- **Visualization**: Built-in plotting and comparison tools
- **Flexible Configuration**: YAML-based configuration system

## Project Structure

```
air_quality/
├── src/
│   ├── __init__.py           # Main application entry point
│   ├── auth.py               # GEE authentication
│   ├── config.py             # Configuration management
│   ├── air_quality.py        # Data processing
│   └── visualization.py      # Visualization tools
├── config/
│   ├── config.yaml           # Main configuration file
│   └── .env.example          # Environment variables template
├── data/                     # Input data directory
├── output/                   # Output results directory
├── notebooks/                # Jupyter notebooks for analysis
├── tests/                    # Unit tests
├── main.py                   # Main application script
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Prerequisites

- Python 3.8+
- Google Cloud Account
- Google Earth Engine account (free at https://earthengine.google.com/)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mirzarahmatov98-cyber/air_quality.git
cd air_quality
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Google Earth Engine Credentials

#### Option A: Using Service Account (Recommended for production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Earth Engine API
4. Create a Service Account
   - Navigate to IAM & Admin > Service Accounts
   - Create new service account
   - Create a JSON key file
5. Register the service account email with Earth Engine (at https://earthengine.google.com/signup/)
6. Copy the JSON key file to your project

#### Option B: Using OAuth (For development)

1. Run `earthengine authenticate` in your terminal
2. Follow the authentication flow

### 5. Configure Environment

```bash
# Copy the example environment file
cp config/.env.example config/.env

# Edit config/.env with your settings
# Set GEE_CREDENTIALS to path of your service account JSON
GEE_CREDENTIALS=/path/to/service-account-key.json
```

### 6. Update Configuration

Edit `config/config.yaml` to customize:
- Study area bounds and cities
- Datasets to monitor
- Processing parameters
- Export settings

## Usage

### Basic Usage

```bash
# Run the main monitoring script
python main.py
```

### Using the Monitor Class

```python
from src import AirQualityMonitor

# Initialize the monitor
monitor = AirQualityMonitor(credentials_path='path/to/credentials.json')

# Monitor NO2
no2_image = monitor.monitor_no2('2023-01-01', '2024-12-31')

# Export results
monitor.export_results(no2_image, 'no2_results')
```

### Interactive Analysis

Use the Jupyter notebooks in the `notebooks/` directory for interactive analysis:

```bash
jupyter notebook notebooks/
```

## Configuration

### Main Configuration File (config.yaml)

The `config/config.yaml` file contains all system settings:

- **GEE Settings**: Credentials path and project ID
- **Study Area**: Geographic bounds and cities of interest
- **Datasets**: Available Earth Engine collections
- **Processing**: Data processing parameters
- **Export**: Output settings

### Environment Variables (.env)

Set sensitive information via environment variables:

```
GEE_CREDENTIALS=path/to/service-account-key.json
GCS_BUCKET=your-gcs-bucket-name
GCS_PROJECT_ID=your-gcp-project-id
DEBUG=False
LOG_LEVEL=INFO
```

## Datasets Used

| Dataset | Description | Collection |
|---------|-------------|-----------|
| Sentinel-5P | Nitrogen Dioxide (NO2) | `COPERNICUS/S5P/NRTI_L3_NO2` |
| Copernicus | Carbon Monoxide (CO) | `COPERNICUS/S5P/NRTI_L3_CO` |
| MODIS | Aerosol Optical Depth | `MODIS/061/MOD09GA` |
| ERA5 | Meteorological Data | `ECMWF/ERA5_LAND/MONTHLY` |

## API Reference

### AirQualityMonitor

Main application class for monitoring operations.

```python
monitor = AirQualityMonitor(credentials_path=None)
```

#### Methods:
- `monitor_no2(start_date, end_date)`: Get NO2 data
- `monitor_co(start_date, end_date)`: Get CO data
- `monitor_aod(start_date, end_date)`: Get AOD data
- `export_results(image, filename)`: Export results to GeoTIFF

### AirQualityProcessor

Handles data processing operations.

```python
processor = AirQualityProcessor()
```

#### Methods:
- `get_no2_data(start_date, end_date, region=None)`
- `get_co_data(start_date, end_date, region=None)`
- `get_aod_data(start_date, end_date, region=None)`
- `compute_temporal_mean(image_collection)`
- `compute_temporal_std(image_collection)`
- `get_city_timeseries(city_coords, collection, radius_m, start_date, end_date)`

### AirQualityVisualizer

Visualization utilities.

```python
visualizer = AirQualityVisualizer()
```

#### Methods:
- `plot_timeseries(timeseries_data, title, ylabel, save_path)`
- `plot_comparison(data_dict, title, save_path)`

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Logging

The application logs to both console and file:
- Console: INFO level and above
- File: `logs/air_quality.log`

Configure logging level in `config/.env`:
```
LOG_LEVEL=DEBUG  # for verbose output
```

## Troubleshooting

### Authentication Errors

```
ValueError: GEE credentials path not provided
```

Solution: Set `GEE_CREDENTIALS` environment variable or pass credentials path to `AirQualityMonitor`.

### Collection Not Found

```
EEException: Error reading asset
```

Solution: Verify dataset collection IDs in `config.yaml` are correct and available.

### Export Timeout

For large exports, check task status in Earth Engine Code Editor or Cloud Console.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Make changes and add tests
4. Commit changes (`git commit -am 'Add improvement'`)
5. Push to branch (`git push origin feature/improvement`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## References

- [Google Earth Engine Documentation](https://developers.google.com/earth-engine)
- [Sentinel-5P Product Guide](https://sentinel.esa.int/documents/247904/351187/Sentinel-5P_Product_Definition_Technical_Report_Nitrogen_Dioxide.pdf)
- [MODIS Collection 6.1](https://modis.gsfc.nasa.gov/)
- [ERA5 Land Data Guide](https://www.ecmwf.int/en/era5-land)

## Contact

For questions or issues, please open an issue on the GitHub repository.

## Acknowledgments

- Copernicus Programme for Sentinel data
- USGS for MODIS data
- ECMWF for ERA5 climate data
- Google for Earth Engine platform
