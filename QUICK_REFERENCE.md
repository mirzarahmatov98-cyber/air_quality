# Air Quality Reporting - Quick Reference Guide

## System Overview

A complete Python-based reporting system for HORIBA air quality data that automatically generates:
- 📊 **4 Professional Visualizations** (PNG plots)
- 📋 **3 CSV Data Exports** (daily, weekly, monthly)
- 🌐 **Interactive HTML Report** (web viewable)
- 📈 **Comprehensive Statistics** (WHO/EPA compliant)

## One-Minute Setup

```bash
# 1. Your data is already downloaded via bulk_downloader.py
# 2. Run the reporting script:
python air_quality_reporting.py

# 3. Open the report:
open reports/station_1_report.html
```

## What Gets Generated

### 📊 Plots (High-Quality PNG)
| Plot | Shows | Useful For |
|------|-------|-----------|
| Daily Trends | PM2.5/PM10 daily averages + range | Trend analysis |
| Hourly Heatmap | Hour-of-day patterns across dates | Diurnal variation |
| Distribution | Histograms + hourly box plots | Statistical analysis |
| Correlation | PM vs Temp/Humidity scatter plots | Meteorological effects |

### 📋 Data Tables (CSV Export)
| File | Frequency | Rows | Use Case |
|------|-----------|------|----------|
| daily_stats.csv | Daily | 1 per day | Detailed tracking |
| weekly_stats.csv | Weekly | 1 per ISO week | Weekly overview |
| monthly_stats.csv | Monthly | 1 per month | Long-term trends |

### 🌐 HTML Report
- Auto-styled responsive design
- Embedded plots and tables
- Air quality status indicator
- Statistical summary

## Sample Output (Station 1, April 12, 2026)

### Daily Statistics
```
Date: 2026-04-12
PM2.5 Mean: 19.04 µg/m³  (Standard: 12 µg/m³ - Moderate)
PM10 Mean:  40.15 µg/m³  (Standard: 54 µg/m³ - Good)
Temperature: 19.97°C (Range: 12.03 - 23.95°C)
Humidity: 47.88% (Range: 37.9 - 70.27%)
Records: 300 hourly measurements
```

### Air Quality Assessment
- **PM2.5**: MODERATE (exceeds WHO good threshold)
- **PM10**: GOOD (within EPA standard)
- **Recommendation**: Sensitive groups should limit outdoor exposure

## Command-Line Options

### Basic Usage
```bash
python air_quality_reporting.py
# Uses defaults: data from ./output, station 1, output to ./reports
```

### Custom Station
```bash
python air_quality_reporting.py --station-id 15
```

### Custom Directories
```bash
python air_quality_reporting.py \
  --data-dir "./output/daily_download_20260413_104900" \
  --station-id 1 \
  --output-dir "./my_reports"
```

### Batch Processing
```bash
# Run analysis for multiple stations
for i in 1 15 21; do
  python air_quality_reporting.py --station-id $i
done
```

## Report File Structure

```
reports/
├── station_1_report.html              ← Open this in browser!
├── station_1_daily_trends.png
├── station_1_hourly_heatmap.png
├── station_1_distribution_analysis.png
├── station_1_correlation_analysis.png
├── station_1_daily_stats.csv
├── station_1_weekly_stats.csv
└── station_1_monthly_stats.csv
```

## HTML Report Sections

1. **Header**: Station info, data period, total records
2. **Executive Summary**: Key metrics in card format
3. **Statistical Summary**: Mean, median, std dev, min/max
4. **Daily Review**: Last 7 days of data
5. **Weekly Review**: Weekly aggregates
6. **Monthly Review**: Monthly aggregates
7. **Visualizations**: All 4 plots embedded
8. **Footer**: Generation timestamp

## Statistics Explained

### PM2.5 Metrics
- **Mean**: Average concentration across period
- **Median**: Middle value (50th percentile)
- **Std Dev**: Variability (higher = more fluctuation)
- **Min/Max**: Lowest and highest values
- **Q25/Q75**: Lower and upper quartiles (IQR)

### Air Quality Categories (PM2.5)
```
≤12 µg/m³      → GOOD
12-35.4        → MODERATE
35.4-55.4      → UNHEALTHY FOR SENSITIVE GROUPS
55.4-150.4     → UNHEALTHY
>150.4         → VERY UNHEALTHY
```

### Air Quality Categories (PM10)
```
≤54 µg/m³      → GOOD
54-154         → MODERATE
154-254        → UNHEALTHY FOR SENSITIVE GROUPS
254-354        → UNHEALTHY
>354           → VERY UNHEALTHY
```

## Common Tasks

### View the Interactive Report
```bash
# Windows
start reports\station_1_report.html

# Mac
open reports/station_1_report.html

# Linux
xdg-open reports/station_1_report.html
```

### Export Data for Excel
```bash
# CSV files are already generated:
# - station_1_daily_stats.csv
# - station_1_weekly_stats.csv
# - station_1_monthly_stats.csv

# Open directly in Excel or import via:
# Data → From Text → Select CSV file
```

### Analyze Multiple Stations
```bash
python examples_reporting.py --example 2
# Creates reports for stations 1, 15, and 21
```

### Get Summary Statistics
```python
python examples_reporting.py --example 3
# Prints key statistics to console
```

## Understanding the Plots

### Daily Trends Plot
- **Top Chart**: PM2.5 daily average (red line) with min-max range (pink shaded)
- **Bottom Chart**: PM10 daily average (teal line) with min-max range (cyan shaded)
- **Use**: Identify pollution spikes and overall trends

### Hourly Heatmap
- **Colors**: Yellow→Red intensity = Low→High concentration
- **X-axis**: Date (left to right)
- **Y-axis**: Hour of day (0-23)
- **Use**: Find times of day with highest pollution (usually morning/evening)

### Distribution Analysis
- **Top-Left**: PM2.5 histogram (frequency distribution)
- **Top-Right**: PM10 histogram
- **Bottom-Left**: PM2.5 by hour (box plot showing median, quartiles)
- **Bottom-Right**: PM10 by hour
- **Use**: Understand typical ranges and hourly variation

### Correlation Analysis
- **Scatter Plots**: Each point = one measurement
- **Trend Lines**: Show linear relationship
- **r value**: Correlation coefficient (-1 to +1)
  - `r > 0`: Positive correlation (both increase together)
  - `r < 0`: Negative correlation (inverse relationship)
  - `r ≈ 0`: No linear correlation
- **Use**: See how PM correlates with weather conditions

## Data Quality

The script automatically handles:
- ✅ Special characters (µ, °, ³)
- ✅ Missing values (-9999 → NaN)
- ✅ Time format conversion
- ✅ Numeric type conversion
- ✅ UTF-8 encoding

## Performance

- **Processing Time**: 3-5 seconds for 300 measurements
- **Plot Generation**: ~0.5-1 seconds each
- **HTML Report**: <0.1 seconds
- **Total**: Typically <5 seconds for complete analysis
- **Disk Space**: ~5-10MB per station

## Requirements

```
Python 3.8+
pandas >= 2.1.4
numpy >= 1.24.3
matplotlib >= 3.8.3
seaborn >= 0.13.1
```

Install via: `pip install -r requirements.txt`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No CSV files found" | Check `--data-dir` path |
| "Station not in file" | Verify station ID exists |
| Plot appears empty | Check data quality for gaps |
| HTML won't open | Use full path or drag-drop to browser |
| Character encoding errors | Script handles UTF-8 automatically |

## Examples

### Example 1: Quick Report
```bash
python air_quality_reporting.py --data-dir "./output/latest_download" --station-id 1
```

### Example 2: Batch Reporting
```python
python examples_reporting.py --example 2
```

### Example 3: Statistics Only
```python
from air_quality_reporting import AirQualityAnalyzer
analyzer = AirQualityAnalyzer(station_id=1)
analyzer.load_data()
summary = analyzer.get_statistical_summary()
print(f"PM2.5: {summary['pm25']['mean']:.1f} µg/m³")
```

### Example 4: Export for Analysis
```bash
python air_quality_reporting.py --station-id 1
# Then open station_1_*_stats.csv in Excel
```

## Next Steps

1. **Generate Report**: `python air_quality_reporting.py`
2. **View Report**: Open `station_1_report.html`
3. **Analyze Data**: Review plots and statistics
4. **Export Data**: Use CSV files for advanced analysis
5. **Batch Process**: Run on other stations
6. **Customize**: Extend for multiple stations, additional metrics

## Support Resources

- **Full Guide**: See `REPORTING_GUIDE.md`
- **Examples**: See `examples_reporting.py`
- **API Docs**: See source code comments in `air_quality_reporting.py`
- **Logs**: Check `logs/` directory for detailed debug info

---

**Quick Links**:
- 📖 [Full Reporting Guide](REPORTING_GUIDE.md)
- 📝 [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
- 🐍 [Example Scripts](examples_reporting.py)
- 📊 [Generated Reports](reports/)

**Version**: 1.0  
**Status**: Production Ready ✅  
**Last Updated**: April 13, 2026
