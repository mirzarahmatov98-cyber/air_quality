## Air Quality Reporting System

This system provides comprehensive dynamic reporting for HORIBA air quality monitoring data with statistical analysis, visualizations, and multi-level temporal reviews.

### Features

#### 1. **Data Analysis**
- Automated data loading from CSV output of the bulk downloader
- Robust numeric conversion and missing value handling (-9999 → NaN)
- Support for any station in the dataset
- Time-series analysis from hourly measurements

#### 2. **Statistical Analysis**
- **Descriptive Statistics**: Mean, median, standard deviation, min, max, quartiles
- **WHO/EPA Categorization**: Air quality classification for PM2.5 and PM10
- **Temporal Aggregation**: Daily, weekly, and monthly statistical summaries
- **Data Quality**: Automatic handling of missing values and outliers

#### 3. **Visualizations** (High-Resolution PNG Files)
- **Daily Trends**: Line plots showing PM2.5 and PM10 daily averages with min-max ranges
- **Hourly Heatmaps**: Hour-of-day patterns across all dates for PM2.5 and PM10
- **Distribution Analysis**: 
  - Histograms with mean/median indicators
  - Box plots showing hourly variations
- **Correlation Analysis**: 
  - PM vs Temperature scatter plots with trend lines
  - PM vs Humidity relationships
  - Pearson correlation coefficients

#### 4. **Report Types**

##### CSV Reports
- `station_1_daily_stats.csv`: Daily aggregated statistics
- `station_1_weekly_stats.csv`: Weekly aggregations
- `station_1_monthly_stats.csv`: Monthly aggregations

##### Interactive HTML Report
- Professional, styled interface with responsive design
- Executive summary with key metrics
- Color-coded WHO/EPA air quality categories
- Four data review tables (daily, weekly, monthly)
- Embedded high-resolution plots
- comprehensive statistical summary tables

### Usage

#### Basic Usage
```bash
python air_quality_reporting.py --data-dir "output/daily_download_20260413_104900" --station-id 1 --output-dir "reports"
```

#### Command-Line Arguments
- `--data-dir`: Path to directory containing downloaded CSV files (default: `./output`)
- `--station-id`: Station ID to analyze (default: `1`)
- `--output-dir`: Directory for reports and plots (default: `./reports`)

#### Example with Multiple Stations
```bash
# Analyze station 15
python air_quality_reporting.py --data-dir "output/daily_download_20260413_104900" --station-id 15 --output-dir "reports/station_15"

# Analyze station 21  
python air_quality_reporting.py --data-dir "output/daily_download_20260413_104900" --station-id 21 --output-dir "reports/station_21"
```

### Output Files

For each station analysis, the following files are generated:

#### Visualizations
1. **station_1_daily_trends.png** (14x10 inches, 300 DPI)
   - Top: PM2.5 daily averages with range
   - Bottom: PM10 daily averages with range
   - Format: publication-ready

2. **station_1_hourly_heatmap.png**
   - Hour-of-day (Y-axis) vs Date (X-axis)
   - Color intensity shows pollutant concentration
   - Useful for identifying diurnal patterns

3. **station_1_distribution_analysis.png** (2x2 grid)
   - Top-left: PM2.5 distribution histogram
   - Top-right: PM10 distribution histogram
   - Bottom-left: PM2.5 by hour-of-day box plot
   - Bottom-right: PM10 by hour-of-day box plot

4. **station_1_correlation_analysis.png** (2x2 grid)
   - Top-left: PM2.5 vs Temperature
   - Top-right: PM2.5 vs Humidity
   - Bottom-left: PM10 vs Temperature
   - Bottom-right: PM10 vs Humidity
   - Including trend lines and correlation coefficients

#### Data Tables (CSV Format)
- **daily_stats.csv**: 24 columns including mean, std, min, max for each pollutant
- **weekly_stats.csv**: Weekly aggregations by ISO week
- **monthly_stats.csv**: Monthly aggregations by year-month

#### Report
- **station_1_report.html**: Interactive HTML report viewable in any web browser

### Air Quality Categories

#### PM2.5 (WHO Guidelines)
- **Good**: ≤ 12 µg/m³
- **Moderate**: 12 - 35.4 µg/m³
- **Unhealthy for Sensitive Groups**: 35.4 - 55.4 µg/m³
- **Unhealthy**: 55.4 - 150.4 µg/m³
- **Very Unhealthy**: > 150.4 µg/m³

#### PM10 (EPA Standards)
- **Good**: ≤ 54 µg/m³
- **Moderate**: 54 - 154 µg/m³
- **Unhealthy for Sensitive Groups**: 154 - 254 µg/m³
- **Unhealthy**: 254 - 354 µg/m³
- **Very Unhealthy**: > 354 µg/m³

### Logging & Debugging

The script generates detailed logs in `logs/` directory:
- Timestamp-based log files
- Both file and console output
- INFO, WARNING, and ERROR level messages
- Full stack traces for troubleshooting

### Key Statistics Provided

For each pollutant and time period:
- **Mean**: Average concentration
- **Median**: 50th percentile (robust average)
- **Std Dev**: Standard deviation (variability)
- **Min**: Minimum observed value
- **Max**: Maximum observed value
- **Q25/Q75**: 25th and 75th percentiles (interquartile range)
- **Count**: Number of valid observations

### Performance Notes

- Processing 300 hourly records: < 2 seconds
- Plot generation: ~0.5-1 second each
- HTML report generation: < 0.1 seconds
- Total execution time: ~3-5 seconds for complete analysis

### Technical Requirements

**Python Packages:**
- pandas >= 2.1.4
- numpy >= 1.24.3
- matplotlib >= 3.8.3
- seaborn >= 0.13.1
- scipy (for statistics)

**Environment:**
- Python 3.8+
- Minimum 500MB disk space for reports
- UTF-8 file encoding support

### Advanced Usage

#### Batch Analysis of Multiple Stations
```bash
@echo off
REM Analyze all stations from the latest download
for %%s in (1 3 4 5 6 7 8 9 11 12 13 14 15 17 18 21) do (
    python air_quality_reporting.py ^
        --data-dir "output/daily_download_20260413_104900" ^
        --station-id %%s ^
        --output-dir "reports/station_%%s"
    echo Completed station %%s
)
```

#### Customizing Report Output
The script can be extended to:
- Add additional pollutant analyses (CO, NO2, SO2, O3)
- Generate PDF reports instead of HTML
- Add time-series forecasting
- Include anomaly detection
- Generate animated visualizations

### Troubleshooting

**Issue**: "No CSV files found"
- Solution: Verify `--data-dir` path contains CSV files from the bulk downloader

**Issue**: "Station not found"
- Solution: Verify station ID exists in the CSV file (check first column)

**Issue**: "Encoding errors in column names"
- Solution: Ensure UTF-8 file encoding; script handles this automatically

**Issue**: Plots appear empty or incomplete
- Solution: Check data quality - may have insufficient data for the analysis period

### Future Enhancements

1. Real-time monitoring dashboard
2. Predictive modeling for air quality forecasting
3. Spatial analysis across multiple stations
4. Health impact assessment
5. Automated alert system for high pollution events
6. Interactive web-based dashboard
7. Machine learning anomaly detection
8. Seasonal decomposition analysis

### Contact & Support

For issues or feature requests, check:
1. Logs directory for detailed error messages
2. Sample data structure in output/
3. Script comments for technical details
