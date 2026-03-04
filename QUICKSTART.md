# Quick Start Guide

## Step 1: Setup Credentials

1. Download your Google Earth Engine service account JSON key file
2. Place it in the config directory or a secure location
3. Update your `.env` file with the path

```bash
GEE_CREDENTIALS=/path/to/service-account-key.json
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Run Basic Monitoring

```bash
python main.py
```

## Step 4: Analyze Results

Use the notebooks in this directory for interactive analysis.

### Example Notebook Structure:

```python
from src import AirQualityMonitor
from src.config import get_config

# Initialize
monitor = AirQualityMonitor()
config = get_config()

# Get data
no2 = monitor.monitor_no2('2023-01-01', '2024-12-31')

# Visualize
visualizer = monitor.visualizer
```

## Common Tasks

### Extract Time Series for a City

```python
from src.air_quality import initialize_processor

processor = initialize_processor()
collection = processor.get_no2_data('2023-01-01', '2024-12-31')

# Get data for Tashkent
tashkent_coords = [69.2075, 41.2995]
timeseries = processor.get_city_timeseries(
    tashkent_coords, 
    collection,
    radius_m=15000
)
```

### Export Results

```python
# Export processed data
monitor.export_results(mean_image, 'my_results')

# Check status in:
# - Google Drive (if drive.google.com is configured)
# - Google Cloud Storage (if bucket is configured)
```

## Next Steps

- Review `config/config.yaml` to customize settings
- Explore datasets in Google Earth Engine Code Editor
- Create custom analysis notebooks
- Set up scheduled monitoring tasks
