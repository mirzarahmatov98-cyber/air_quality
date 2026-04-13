#!/usr/bin/env python3
"""
Comprehensive Air Quality Analysis and Reporting Script
Analyzes PM2.5, PM10 and other pollutants with daily, weekly, and monthly reviews
Generates plots, statistical analysis, and HTML reports
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path
import seaborn as sns
from scipy import stats
import logging
import warnings

warnings.filterwarnings('ignore')

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"reporting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class AirQualityAnalyzer:
    """Comprehensive air quality data analyzer"""
    
    def __init__(self, data_dir, station_id=1, output_dir=None):
        """
        Initialize analyzer
        
        Args:
            data_dir: Path to directory containing CSV files
            station_id: Station ID to analyze (default: 1)
            output_dir: Directory for reports and plots
        """
        self.data_dir = Path(data_dir)
        self.station_id = station_id
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = None
        self.daily_stats = None
        self.weekly_stats = None
        self.monthly_stats = None
        
        logger.info(f"Analyzer initialized - Station: {station_id}, Output: {self.output_dir}")
    
    def load_data(self):
        """Load and parse CSV data for the station"""
        logger.info(f"Loading data for station {self.station_id}...")
        
        # Try to find the latest combined data or station-specific data
        csv_files = list(self.data_dir.glob("*combined.csv"))
        if not csv_files:
            csv_files = list(self.data_dir.glob("**/station_*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {self.data_dir}")
        
        # Use the most recent file
        csv_file = sorted(csv_files, key=os.path.getmtime)[-1]
        logger.info(f"Using file: {csv_file.name}")
        
        # Load CSV with proper encoding
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Filter by station if needed
        if 'Station_ID' in df.columns:
            df = df[df['Station_ID'] == self.station_id].copy()
        
        # Parse time
        df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S')
        
        # Convert all columns except Time and Station_ID to numeric
        for col in df.columns:
            if col not in ['Station_ID', 'Time']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Replace -9999 with NaN (missing values)
        df = df.replace(-9999, np.nan)
        
        # Sort by time
        df = df.sort_values('Time').reset_index(drop=True)
        
        logger.info(f"Loaded {len(df)} records from {df['Time'].min()} to {df['Time'].max()}")
        logger.info(f"Data shape: {df.shape}")
        
        self.df = df
        return df
    
    def calculate_statistics(self):
        """Calculate daily, weekly, and monthly statistics"""
        logger.info("Calculating statistics...")
        
        df = self.df.copy()
        
        # Add time components
        df['Date'] = df['Time'].dt.date
        df['Week'] = df['Time'].dt.isocalendar().week
        df['Year'] = df['Time'].dt.year
        df['Month'] = df['Time'].dt.month
        df['Hour'] = df['Time'].dt.hour
        df['DayName'] = df['Time'].dt.day_name()
        
        # Standardize column names
        pm25_col = 'PM 2.5(µg/m³)'
        pm10_col = 'PM 10(µg/m³)'
        temp_col = 'Temperature(°C)'
        humidity_col = 'Humidity(%)'
        pressure_col = 'Pressure(hPa)'
        
        # Daily statistics
        daily_agg = {}
        if pm25_col in df.columns:
            daily_agg[pm25_col] = ['mean', 'std', 'min', 'max', 'count']
        if pm10_col in df.columns:
            daily_agg[pm10_col] = ['mean', 'std', 'min', 'max', 'count']
        if temp_col in df.columns:
            daily_agg[temp_col] = ['mean', 'min', 'max']
        if humidity_col in df.columns:
            daily_agg[humidity_col] = ['mean', 'min', 'max']
        if pressure_col in df.columns:
            daily_agg[pressure_col] = 'mean'
        
        daily = df.groupby('Date').agg(daily_agg).round(2)
        daily.columns = ['_'.join(str(col).strip() for col in col_tuple if col) for col_tuple in daily.columns.values]
        daily = daily.reset_index()
        
        self.daily_stats = daily
        logger.info(f"Calculated daily statistics for {len(daily)} days")
        
        # Weekly statistics
        weekly_agg = {}
        if pm25_col in df.columns:
            weekly_agg[pm25_col] = ['mean', 'std', 'min', 'max']
        if pm10_col in df.columns:
            weekly_agg[pm10_col] = ['mean', 'std', 'min', 'max']
        
        weekly = df.groupby(['Year', 'Week']).agg(weekly_agg).round(2)
        weekly.columns = ['_'.join(str(col).strip() for col in col_tuple if col) for col_tuple in weekly.columns.values]
        
        self.weekly_stats = weekly
        logger.info(f"Calculated weekly statistics")
        
        # Monthly statistics
        monthly_agg = {}
        if pm25_col in df.columns:
            monthly_agg[pm25_col] = ['mean', 'std', 'min', 'max', 'median']
        if pm10_col in df.columns:
            monthly_agg[pm10_col] = ['mean', 'std', 'min', 'max', 'median']
        
        monthly = df.groupby(['Year', 'Month']).agg(monthly_agg).round(2)
        monthly.columns = ['_'.join(str(col).strip() for col in col_tuple if col) for col_tuple in monthly.columns.values]
        
        self.monthly_stats = monthly
        logger.info(f"Calculated monthly statistics")
        
        return daily, weekly, monthly
    
    def get_statistical_summary(self):
        """Generate comprehensive statistics summary"""
        df = self.df
        
        # Dynamically find column names
        pm25_col = next((col for col in df.columns if 'PM 2' in col and 'µg' in col), 'PM 2.5(µg/m³)')
        pm10_col = next((col for col in df.columns if 'PM 10' in col and 'µg' in col), 'PM 10(µg/m³)')
        temp_col = next((col for col in df.columns if 'Temperature' in col), 'Temperature(°C)')
        humidity_col = next((col for col in df.columns if 'Humidity' in col), 'Humidity(%)')
        pressure_col = next((col for col in df.columns if 'Pressure' in col), 'Pressure(hPa)')
        
        summary = {
            'station_id': self.station_id,
            'data_period': f"{df['Time'].min()} to {df['Time'].max()}",
            'total_records': len(df),
            'pm25': self._get_pollutant_stats(pm25_col),
            'pm10': self._get_pollutant_stats(pm10_col),
            'temperature': self._get_pollutant_stats(temp_col),
            'humidity': self._get_pollutant_stats(humidity_col),
            'pressure': self._get_pollutant_stats(pressure_col),
        }
        
        # Add pollution categories for PM2.5 and PM10
        summary['pm25']['who_category'] = self._categorize_pm25(summary['pm25']['mean'])
        summary['pm10']['who_category'] = self._categorize_pm10(summary['pm10']['mean'])
        
        return summary
    
    def _get_pollutant_stats(self, column):
        """Get statistics for a pollutant"""
        data = self.df[column].dropna()
        
        if len(data) == 0:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'median': 0, 'count': 0}
        
        return {
            'mean': data.mean(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'median': data.median(),
            'q25': data.quantile(0.25),
            'q75': data.quantile(0.75),
            'count': len(data),
        }
    
    @staticmethod
    def _categorize_pm25(pm25_mean):
        """Categorize PM2.5 based on WHO guidelines"""
        if pm25_mean <= 12:
            return "Good (WHO)"
        elif pm25_mean <= 35.4:
            return "Moderate"
        elif pm25_mean <= 55.4:
            return "Unhealthy for Sensitive Groups"
        elif pm25_mean <= 150.4:
            return "Unhealthy"
        else:
            return "Very Unhealthy"
    
    @staticmethod
    def _categorize_pm10(pm10_mean):
        """Categorize PM10 based on EPA standards"""
        if pm10_mean <= 54:
            return "Good"
        elif pm10_mean <= 154:
            return "Moderate"
        elif pm10_mean <= 254:
            return "Unhealthy for Sensitive Groups"
        elif pm10_mean <= 354:
            return "Unhealthy"
        else:
            return "Very Unhealthy"
    
    def plot_daily_trends(self):
        """Plot daily PM2.5 and PM10 trends"""
        logger.info("Generating daily trends plot...")
        
        # Find column names dynamically
        pm25_col = next((col for col in self.df.columns if 'PM 2' in col and 'µg' in col), None)
        pm10_col = next((col for col in self.df.columns if 'PM 10' in col and 'µg' in col), None)
        
        if not pm25_col or not pm10_col:
            logger.warning("Could not find PM columns, skipping daily trends plot")
            return None
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # PM2.5 daily trend
        daily = self.daily_stats.copy()
        daily['Date'] = pd.to_datetime(daily['Date'])
        
        pm25_mean_col = next((col for col in daily.columns if 'PM 2' in col and 'mean' in col), None)
        pm25_min_col = next((col for col in daily.columns if 'PM 2' in col and 'min' in col), None)
        pm25_max_col = next((col for col in daily.columns if 'PM 2' in col and 'max' in col), None)
        
        if pm25_mean_col:
            axes[0].plot(daily['Date'], daily[pm25_mean_col], 
                        marker='o', linewidth=2, label='Daily Average', color='#FF6B6B')
            if pm25_min_col and pm25_max_col:
                axes[0].fill_between(daily['Date'], 
                                    daily[pm25_min_col],
                                    daily[pm25_max_col],
                                    alpha=0.3, color='#FF6B6B', label='Min-Max Range')
        axes[0].set_ylabel('PM 2.5 (µg/m³)', fontsize=12, fontweight='bold')
        axes[0].set_title('Daily PM 2.5 Trend', fontsize=14, fontweight='bold')
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45)
        
        # PM10 daily trend
        pm10_mean_col = next((col for col in daily.columns if 'PM 10' in col and 'mean' in col), None)
        pm10_min_col = next((col for col in daily.columns if 'PM 10' in col and 'min' in col), None)
        pm10_max_col = next((col for col in daily.columns if 'PM 10' in col and 'max' in col), None)
        
        if pm10_mean_col:
            axes[1].plot(daily['Date'], daily[pm10_mean_col],
                        marker='s', linewidth=2, label='Daily Average', color='#4ECDC4')
            if pm10_min_col and pm10_max_col:
                axes[1].fill_between(daily['Date'],
                                    daily[pm10_min_col],
                                    daily[pm10_max_col],
                                    alpha=0.3, color='#4ECDC4', label='Min-Max Range')
        axes[1].set_ylabel('PM 10 (µg/m³)', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Date', fontsize=12, fontweight='bold')
        axes[1].set_title('Daily PM 10 Trend', fontsize=14, fontweight='bold')
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.3)
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        plot_file = self.output_dir / f"station_{self.station_id}_daily_trends.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {plot_file}")
        plt.close()
        
        return plot_file
    
    def plot_hourly_heatmap(self):
        """Plot hourly heatmaps for PM2.5 and PM10"""
        logger.info("Generating hourly heatmap...")
        
        # Find column names dynamically
        pm25_col = next((col for col in self.df.columns if 'PM 2' in col and 'µg' in col), None)
        pm10_col = next((col for col in self.df.columns if 'PM 10' in col and 'µg' in col), None)
        
        if not pm25_col or not pm10_col:
            logger.warning("Could not find PM columns, skipping hourly heatmap")
            return None
        
        df = self.df.copy()
        df['Date'] = df['Time'].dt.date
        df['Hour'] = df['Time'].dt.hour
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # PM2.5 heatmap
        pm25_pivot = df.pivot_table(values=pm25_col, 
                                    index='Hour', 
                                    columns='Date', 
                                    aggfunc='mean')
        sns.heatmap(pm25_pivot, cmap='YlOrRd', ax=axes[0], cbar_kws={'label': 'µg/m³'})
        axes[0].set_title('PM 2.5 Hourly Pattern (Hour of Day vs Date)', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Hour of Day', fontsize=12, fontweight='bold')
        
        # PM10 heatmap
        pm10_pivot = df.pivot_table(values=pm10_col,
                                    index='Hour',
                                    columns='Date',
                                    aggfunc='mean')
        sns.heatmap(pm10_pivot, cmap='YlGnBu', ax=axes[1], cbar_kws={'label': 'µg/m³'})
        axes[1].set_title('PM 10 Hourly Pattern (Hour of Day vs Date)', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Hour of Day', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Date', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        plot_file = self.output_dir / f"station_{self.station_id}_hourly_heatmap.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {plot_file}")
        plt.close()
        
        return plot_file
    
    def plot_distribution_analysis(self):
        """Plot distribution analysis for PM2.5 and PM10"""
        logger.info("Generating distribution analysis...")
        
        # Find column names dynamically
        pm25_col = next((col for col in self.df.columns if 'PM 2' in col and 'µg' in col), None)
        pm10_col = next((col for col in self.df.columns if 'PM 10' in col and 'µg' in col), None)
        
        if not pm25_col or not pm10_col:
            logger.warning("Could not find PM columns, skipping distribution analysis")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        pm25_data = self.df[pm25_col].dropna()
        pm10_data = self.df[pm10_col].dropna()
        
        # PM2.5 histogram
        axes[0, 0].hist(pm25_data, bins=50, color='#FF6B6B', alpha=0.7, edgecolor='black')
        axes[0, 0].axvline(pm25_data.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {pm25_data.mean():.1f}')
        axes[0, 0].axvline(pm25_data.median(), color='orange', linestyle='--', linewidth=2, label=f'Median: {pm25_data.median():.1f}')
        axes[0, 0].set_title('PM 2.5 Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('PM 2.5 (µg/m³)', fontsize=11, fontweight='bold')
        axes[0, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # PM10 histogram
        axes[0, 1].hist(pm10_data, bins=50, color='#4ECDC4', alpha=0.7, edgecolor='black')
        axes[0, 1].axvline(pm10_data.mean(), color='darkblue', linestyle='--', linewidth=2, label=f'Mean: {pm10_data.mean():.1f}')
        axes[0, 1].axvline(pm10_data.median(), color='cyan', linestyle='--', linewidth=2, label=f'Median: {pm10_data.median():.1f}')
        axes[0, 1].set_title('PM 10 Distribution', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('PM 10 (µg/m³)', fontsize=11, fontweight='bold')
        axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # PM2.5 Box plot by hour
        hourly_pm25 = [self.df[self.df['Time'].dt.hour == h][pm25_col].dropna().values for h in range(24)]
        axes[1, 0].boxplot(hourly_pm25, labels=range(24))
        axes[1, 0].set_title('PM 2.5 by Hour of Day', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Hour', fontsize=11, fontweight='bold')
        axes[1, 0].set_ylabel('PM 2.5 (µg/m³)', fontsize=11, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # PM10 Box plot by hour
        hourly_pm10 = [self.df[self.df['Time'].dt.hour == h][pm10_col].dropna().values for h in range(24)]
        axes[1, 1].boxplot(hourly_pm10, labels=range(24))
        axes[1, 1].set_title('PM 10 by Hour of Day', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Hour', fontsize=11, fontweight='bold')
        axes[1, 1].set_ylabel('PM 10 (µg/m³)', fontsize=11, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        plot_file = self.output_dir / f"station_{self.station_id}_distribution_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {plot_file}")
        plt.close()
        
        return plot_file
    
    def plot_correlation_analysis(self):
        """Plot correlation analysis between PM and meteorological factors"""
        logger.info("Generating correlation analysis...")
        
        # Find column names dynamically
        pm25_col = next((col for col in self.df.columns if 'PM 2' in col and 'µg' in col), None)
        pm10_col = next((col for col in self.df.columns if 'PM 10' in col and 'µg' in col), None)
        temp_col = next((col for col in self.df.columns if 'Temperature' in col), None)
        humidity_col = next((col for col in self.df.columns if 'Humidity' in col), None)
        
        if not all([pm25_col, pm10_col, temp_col, humidity_col]):
            logger.warning("Could not find required columns for correlation analysis")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        df = self.df.copy()
        
        # PM2.5 vs Temperature
        valid_data = df[[pm25_col, temp_col]].dropna()
        if len(valid_data) > 0:
            axes[0, 0].scatter(valid_data[temp_col], valid_data[pm25_col], 
                              alpha=0.5, s=30, color='#FF6B6B')
            z = np.polyfit(valid_data[temp_col], valid_data[pm25_col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid_data[temp_col].min(), valid_data[temp_col].max(), 100)
            axes[0, 0].plot(x_line, p(x_line), "r--", linewidth=2)
            corr = valid_data[pm25_col].corr(valid_data[temp_col])
            axes[0, 0].set_title(f'PM 2.5 vs Temperature (r={corr:.2f})', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Temperature (°C)', fontsize=11, fontweight='bold')
        axes[0, 0].set_ylabel('PM 2.5 (µg/m³)', fontsize=11, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        
        # PM2.5 vs Humidity
        valid_data = df[[pm25_col, humidity_col]].dropna()
        if len(valid_data) > 0:
            axes[0, 1].scatter(valid_data[humidity_col], valid_data[pm25_col],
                              alpha=0.5, s=30, color='#FF6B6B')
            z = np.polyfit(valid_data[humidity_col], valid_data[pm25_col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid_data[humidity_col].min(), valid_data[humidity_col].max(), 100)
            axes[0, 1].plot(x_line, p(x_line), "r--", linewidth=2)
            corr = valid_data[pm25_col].corr(valid_data[humidity_col])
            axes[0, 1].set_title(f'PM 2.5 vs Humidity (r={corr:.2f})', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Humidity (%)', fontsize=11, fontweight='bold')
        axes[0, 1].set_ylabel('PM 2.5 (µg/m³)', fontsize=11, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        # PM10 vs Temperature
        valid_data = df[[pm10_col, temp_col]].dropna()
        if len(valid_data) > 0:
            axes[1, 0].scatter(valid_data[temp_col], valid_data[pm10_col],
                              alpha=0.5, s=30, color='#4ECDC4')
            z = np.polyfit(valid_data[temp_col], valid_data[pm10_col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid_data[temp_col].min(), valid_data[temp_col].max(), 100)
            axes[1, 0].plot(x_line, p(x_line), "b--", linewidth=2)
            corr = valid_data[pm10_col].corr(valid_data[temp_col])
            axes[1, 0].set_title(f'PM 10 vs Temperature (r={corr:.2f})', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Temperature (°C)', fontsize=11, fontweight='bold')
        axes[1, 0].set_ylabel('PM 10 (µg/m³)', fontsize=11, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # PM10 vs Humidity
        valid_data = df[[pm10_col, humidity_col]].dropna()
        if len(valid_data) > 0:
            axes[1, 1].scatter(valid_data[humidity_col], valid_data[pm10_col],
                              alpha=0.5, s=30, color='#4ECDC4')
            z = np.polyfit(valid_data[humidity_col], valid_data[pm10_col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid_data[humidity_col].min(), valid_data[humidity_col].max(), 100)
            axes[1, 1].plot(x_line, p(x_line), "b--", linewidth=2)
            corr = valid_data[pm10_col].corr(valid_data[humidity_col])
            axes[1, 1].set_title(f'PM 10 vs Humidity (r={corr:.2f})', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Humidity (%)', fontsize=11, fontweight='bold')
        axes[1, 1].set_ylabel('PM 10 (µg/m³)', fontsize=11, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        plot_file = self.output_dir / f"station_{self.station_id}_correlation_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {plot_file}")
        plt.close()
        
        return plot_file
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        logger.info("Generating HTML report...")
        
        summary = self.get_statistical_summary()
        
        html_file = self.output_dir / f"station_{self.station_id}_report.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(self._get_html_header())
            f.write(self._get_executive_summary_section(summary))
            f.write(self._get_statistical_summary_section(summary))
            f.write(self._get_daily_review_section())
            f.write(self._get_weekly_review_section())
            f.write(self._get_monthly_review_section())
            f.write(self._get_trends_section())
            f.write(self._get_html_footer())
        
        logger.info(f"Saved: {html_file}")
        return html_file
    
    def _get_html_header(self):
        """Get HTML header"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Air Quality Report - Station {self.station_id}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f5f5f5;
                    color: #333;
                    line-height: 1.6;
                }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                .header p {{ font-size: 1.1em; opacity: 0.9; }}
                .section {{
                    background: white;
                    padding: 25px;
                    margin-bottom: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .section h2 {{
                    color: #667eea;
                    margin-bottom: 20px;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                    font-size: 1.8em;
                }}
                .section h3 {{
                    color: #764ba2;
                    margin-top: 20px;
                    margin-bottom: 15px;
                    font-size: 1.3em;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .stat-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .stat-card h4 {{ font-size: 0.9em; opacity: 0.9; margin-bottom: 10px; }}
                .stat-card .value {{ font-size: 2em; font-weight: bold; }}
                .stat-card .unit {{ font-size: 0.8em; opacity: 0.8; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-size: 0.95em;
                }}
                table th {{
                    background: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                table td {{
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }}
                table tr:hover {{ background-color: #f9f9f9; }}
                table tr:nth-child(even) {{ background-color: #f5f5f5; }}
                .plot-container {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .plot-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .alert {{
                    padding: 15px;
                    margin: 15px 0;
                    border-left: 4px solid;
                    border-radius: 4px;
                    background-color: #f0f0f0;
                }}
                .alert-warning {{ border-color: #ff9800; background-color: #fff3e0; }}
                .alert-danger {{ border-color: #f44336; background-color: #ffebee; }}
                .alert-success {{ border-color: #4caf50; background-color: #e8f5e9; }}
                .alert-info {{ border-color: #2196f3; background-color: #e3f2fd; }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
        """
    
    def _get_html_footer(self):
        """Get HTML footer"""
        return """
            </div>
            <div class="footer">
                <p>Generated using Air Quality Analysis System</p>
                <p>Report generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
        </body>
        </html>
        """
    
    def _get_executive_summary_section(self, summary):
        """Get executive summary HTML section"""
        html = f"""
        <div class="header">
            <h1>Air Quality Report - Station {self.station_id}</h1>
            <p>Period: {summary['data_period']}</p>
            <p>Total Records: {summary['total_records']:,} measurements</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>PM 2.5</h4>
                    <div class="value">{summary['pm25']['mean']:.1f}</div>
                    <div class="unit">µg/m³ (Average)</div>
                    <div style="margin-top: 10px; font-size: 0.9em;">{summary['pm25']['who_category']}</div>
                </div>
                <div class="stat-card">
                    <h4>PM 10</h4>
                    <div class="value">{summary['pm10']['mean']:.1f}</div>
                    <div class="unit">µg/m³ (Average)</div>
                    <div style="margin-top: 10px; font-size: 0.9em;">{summary['pm10']['who_category']}</div>
                </div>
                <div class="stat-card">
                    <h4>Temperature</h4>
                    <div class="value">{summary['temperature']['mean']:.1f}</div>
                    <div class="unit">°C (Average)</div>
                    <div style="margin-top: 10px; font-size: 0.9em;">Min: {summary['temperature']['min']:.1f}°C | Max: {summary['temperature']['max']:.1f}°C</div>
                </div>
                <div class="stat-card">
                    <h4>Humidity</h4>
                    <div class="value">{summary['humidity']['mean']:.1f}</div>
                    <div class="unit">% (Average)</div>
                    <div style="margin-top: 10px; font-size: 0.9em;">Range: {summary['humidity']['min']:.1f}% - {summary['humidity']['max']:.1f}%</div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _get_statistical_summary_section(self, summary):
        """Get statistical summary HTML section"""
        
        html = """
        <div class="section">
            <h2>Statistical Summary</h2>
            
            <h3>PM 2.5 Statistics (µg/m³)</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Mean</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Median</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Std Dev</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Min</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Max</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>25th Percentile</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>75th Percentile</td>
                    <td>{:.2f}</td>
                </tr>
            </table>
            
            <h3>PM 10 Statistics (µg/m³)</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Mean</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Median</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Std Dev</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Min</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>Max</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>25th Percentile</td>
                    <td>{:.2f}</td>
                </tr>
                <tr>
                    <td>75th Percentile</td>
                    <td>{:.2f}</td>
                </tr>
            </table>
        </div>
        """.format(
            summary['pm25']['mean'], summary['pm25']['median'], summary['pm25']['std'],
            summary['pm25']['min'], summary['pm25']['max'], summary['pm25']['q25'], summary['pm25']['q75'],
            summary['pm10']['mean'], summary['pm10']['median'], summary['pm10']['std'],
            summary['pm10']['min'], summary['pm10']['max'], summary['pm10']['q25'], summary['pm10']['q75']
        )
        
        return html
    
    def _get_daily_review_section(self):
        """Get daily review HTML section"""
        daily = self.daily_stats.copy()
        daily['Date'] = pd.to_datetime(daily['Date']).dt.strftime('%Y-%m-%d')
        
        # Get last 7 days
        daily_recent = daily.tail(7).copy()
        
        # Find column names dynamically
        pm25_mean = next((col for col in daily.columns if 'PM 2' in col and 'mean' in col), None)
        pm25_min = next((col for col in daily.columns if 'PM 2' in col and 'min' in col), None)
        pm25_max = next((col for col in daily.columns if 'PM 2' in col and 'max' in col), None)
        pm25_count = next((col for col in daily.columns if 'PM 2' in col and 'count' in col), None)
        pm10_mean = next((col for col in daily.columns if 'PM 10' in col and 'mean' in col), None)
        pm10_min = next((col for col in daily.columns if 'PM 10' in col and 'min' in col), None)
        pm10_max = next((col for col in daily.columns if 'PM 10' in col and 'max' in col), None)
        temp_mean = next((col for col in daily.columns if 'Temperature' in col and 'mean' in col), None)
        humidity_mean = next((col for col in daily.columns if 'Humidity' in col and 'mean' in col), None)
        
        html = """
        <div class="section">
            <h2>Daily Review (Last 7 Days)</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>PM2.5 Avg (µg/m³)</th>
                    <th>PM2.5 Min-Max</th>
                    <th>PM10 Avg (µg/m³)</th>
                    <th>PM10 Min-Max</th>
                    <th>Temp Avg (°C)</th>
                    <th>Humidity Avg (%)</th>
                    <th>Records</th>
                </tr>
        """
        
        for _, row in daily_recent.iterrows():
            count_val = int(row[pm25_count]) if pm25_count and pd.notna(row[pm25_count]) else 0
            pm25_mean_val = row[pm25_mean] if pm25_mean and pd.notna(row[pm25_mean]) else 0
            pm25_min_val = row[pm25_min] if pm25_min and pd.notna(row[pm25_min]) else 0
            pm25_max_val = row[pm25_max] if pm25_max and pd.notna(row[pm25_max]) else 0
            pm10_mean_val = row[pm10_mean] if pm10_mean and pd.notna(row[pm10_mean]) else 0
            pm10_min_val = row[pm10_min] if pm10_min and pd.notna(row[pm10_min]) else 0
            pm10_max_val = row[pm10_max] if pm10_max and pd.notna(row[pm10_max]) else 0
            temp_mean_val = row[temp_mean] if temp_mean and pd.notna(row[temp_mean]) else 0
            humidity_mean_val = row[humidity_mean] if humidity_mean and pd.notna(row[humidity_mean]) else 0
            
            html += f"""
                <tr>
                    <td>{row['Date']}</td>
                    <td>{pm25_mean_val:.1f}</td>
                    <td>{pm25_min_val:.1f} - {pm25_max_val:.1f}</td>
                    <td>{pm10_mean_val:.1f}</td>
                    <td>{pm10_min_val:.1f} - {pm10_max_val:.1f}</td>
                    <td>{temp_mean_val:.1f}</td>
                    <td>{humidity_mean_val:.1f}</td>
                    <td>{count_val}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html
    
    def _get_weekly_review_section(self):
        """Get weekly review HTML section"""
        weekly = self.weekly_stats.copy()
        
        # Find column names dynamically
        pm25_mean = next((col for col in weekly.columns if 'PM 2' in col and 'mean' in col), None)
        pm25_min = next((col for col in weekly.columns if 'PM 2' in col and 'min' in col), None)
        pm25_max = next((col for col in weekly.columns if 'PM 2' in col and 'max' in col), None)
        pm10_mean = next((col for col in weekly.columns if 'PM 10' in col and 'mean' in col), None)
        pm10_min = next((col for col in weekly.columns if 'PM 10' in col and 'min' in col), None)
        pm10_max = next((col for col in weekly.columns if 'PM 10' in col and 'max' in col), None)
        
        html = """
        <div class="section">
            <h2>Weekly Review</h2>
            <table>
                <tr>
                    <th>Year-Week</th>
                    <th>PM2.5 Avg (µg/m³)</th>
                    <th>PM2.5 Min-Max</th>
                    <th>PM10 Avg (µg/m³)</th>
                    <th>PM10 Min-Max</th>
                </tr>
        """
        
        for (year, week), row in weekly.iterrows():
            pm25_mean_val = row[pm25_mean] if pm25_mean and pd.notna(row[pm25_mean]) else 0
            pm25_min_val = row[pm25_min] if pm25_min and pd.notna(row[pm25_min]) else 0
            pm25_max_val = row[pm25_max] if pm25_max and pd.notna(row[pm25_max]) else 0
            pm10_mean_val = row[pm10_mean] if pm10_mean and pd.notna(row[pm10_mean]) else 0
            pm10_min_val = row[pm10_min] if pm10_min and pd.notna(row[pm10_min]) else 0
            pm10_max_val = row[pm10_max] if pm10_max and pd.notna(row[pm10_max]) else 0
            
            html += f"""
                <tr>
                    <td>{year}-W{week:02d}</td>
                    <td>{pm25_mean_val:.1f}</td>
                    <td>{pm25_min_val:.1f} - {pm25_max_val:.1f}</td>
                    <td>{pm10_mean_val:.1f}</td>
                    <td>{pm10_min_val:.1f} - {pm10_max_val:.1f}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html
    
    def _get_monthly_review_section(self):
        """Get monthly review HTML section"""
        monthly = self.monthly_stats.copy()
        
        # Find column names dynamically
        pm25_mean = next((col for col in monthly.columns if 'PM 2' in col and 'mean' in col), None)
        pm25_min = next((col for col in monthly.columns if 'PM 2' in col and 'min' in col), None)
        pm25_max = next((col for col in monthly.columns if 'PM 2' in col and 'max' in col), None)
        pm25_median = next((col for col in monthly.columns if 'PM 2' in col and 'median' in col), None)
        pm10_mean = next((col for col in monthly.columns if 'PM 10' in col and 'mean' in col), None)
        pm10_min = next((col for col in monthly.columns if 'PM 10' in col and 'min' in col), None)
        pm10_max = next((col for col in monthly.columns if 'PM 10' in col and 'max' in col), None)
        pm10_median = next((col for col in monthly.columns if 'PM 10' in col and 'median' in col), None)
        
        html = """
        <div class="section">
            <h2>Monthly Review</h2>
            <table>
                <tr>
                    <th>Year-Month</th>
                    <th>PM2.5 Avg (µg/m³)</th>
                    <th>PM2.5 Min-Max</th>
                    <th>PM2.5 Median</th>
                    <th>PM10 Avg (µg/m³)</th>
                    <th>PM10 Min-Max</th>
                    <th>PM10 Median</th>
                </tr>
        """
        
        for (year, month), row in monthly.iterrows():
            pm25_mean_val = row[pm25_mean] if pm25_mean and pd.notna(row[pm25_mean]) else 0
            pm25_min_val = row[pm25_min] if pm25_min and pd.notna(row[pm25_min]) else 0
            pm25_max_val = row[pm25_max] if pm25_max and pd.notna(row[pm25_max]) else 0
            pm25_median_val = row[pm25_median] if pm25_median and pd.notna(row[pm25_median]) else 0
            pm10_mean_val = row[pm10_mean] if pm10_mean and pd.notna(row[pm10_mean]) else 0
            pm10_min_val = row[pm10_min] if pm10_min and pd.notna(row[pm10_min]) else 0
            pm10_max_val = row[pm10_max] if pm10_max and pd.notna(row[pm10_max]) else 0
            pm10_median_val = row[pm10_median] if pm10_median and pd.notna(row[pm10_median]) else 0
            
            html += f"""
                <tr>
                    <td>{year}-{month:02d}</td>
                    <td>{pm25_mean_val:.1f}</td>
                    <td>{pm25_min_val:.1f} - {pm25_max_val:.1f}</td>
                    <td>{pm25_median_val:.1f}</td>
                    <td>{pm10_mean_val:.1f}</td>
                    <td>{pm10_min_val:.1f} - {pm10_max_val:.1f}</td>
                    <td>{pm10_median_val:.1f}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html
    
    def _get_trends_section(self):
        """Get trends and visualizations HTML section"""
        html = """
        <div class="section">
            <h2>Trend Analysis & Visualizations</h2>
            
            <h3>Daily Trends</h3>
            <div class="plot-container">
                <img src="station_{}_daily_trends.png" alt="Daily Trends">
            </div>
            
            <h3>Hourly Pattern Analysis</h3>
            <div class="plot-container">
                <img src="station_{}_hourly_heatmap.png" alt="Hourly Heatmap">
            </div>
            
            <h3>Distribution Analysis</h3>
            <div class="plot-container">
                <img src="station_{}_distribution_analysis.png" alt="Distribution Analysis">
            </div>
            
            <h3>Correlation with Meteorological Factors</h3>
            <div class="plot-container">
                <img src="station_{}_correlation_analysis.png" alt="Correlation Analysis">
            </div>
        </div>
        """.format(self.station_id, self.station_id, self.station_id, self.station_id)
        
        return html
    
    def generate_csv_reports(self):
        """Save statistical summaries as CSV files"""
        logger.info("Generating CSV reports...")
        
        # Daily stats CSV
        daily_csv = self.output_dir / f"station_{self.station_id}_daily_stats.csv"
        self.daily_stats.to_csv(daily_csv, index=False)
        logger.info(f"Saved: {daily_csv}")
        
        # Weekly stats CSV
        weekly_csv = self.output_dir / f"station_{self.station_id}_weekly_stats.csv"
        self.weekly_stats.to_csv(weekly_csv)
        logger.info(f"Saved: {weekly_csv}")
        
        # Monthly stats CSV
        monthly_csv = self.output_dir / f"station_{self.station_id}_monthly_stats.csv"
        self.monthly_stats.to_csv(monthly_csv)
        logger.info(f"Saved: {monthly_csv}")
        
        return daily_csv, weekly_csv, monthly_csv
    
    def run_complete_analysis(self):
        """Run complete analysis pipeline"""
        logger.info("=" * 70)
        logger.info(f"Starting complete analysis for Station {self.station_id}")
        logger.info("=" * 70)
        
        try:
            # Load data
            self.load_data()
            
            # Calculate statistics
            self.calculate_statistics()
            
            # Generate visualizations
            self.plot_daily_trends()
            self.plot_hourly_heatmap()
            self.plot_distribution_analysis()
            self.plot_correlation_analysis()
            
            # Generate reports
            self.generate_csv_reports()
            html_report = self.generate_html_report()
            
            logger.info("=" * 70)
            logger.info(f"Analysis complete for Station {self.station_id}")
            logger.info(f"Report saved to: {html_report}")
            logger.info("=" * 70)
            
            return html_report
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            raise


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Air Quality Analysis and Reporting')
    parser.add_argument('--data-dir', type=str, default='./output',
                       help='Directory containing downloaded data')
    parser.add_argument('--station-id', type=int, default=1,
                       help='Station ID to analyze (default: 1)')
    parser.add_argument('--output-dir', type=str, default='./reports',
                       help='Directory for reports and plots')
    
    args = parser.parse_args()
    
    try:
        analyzer = AirQualityAnalyzer(
            data_dir=args.data_dir,
            station_id=args.station_id,
            output_dir=args.output_dir
        )
        
        analyzer.run_complete_analysis()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
