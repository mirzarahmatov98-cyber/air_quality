#!/usr/bin/env python3
"""Debug script to check daily stats Date column"""
import pandas as pd
from air_quality_reporting import AirQualityAnalyzer

analyzer = AirQualityAnalyzer(data_dir='output/daily_download_20260413_104900', station_id=1)
analyzer.load_data()
analyzer.calculate_statistics()

print("Daily Stats Info:")
print(analyzer.daily_stats[['Date']])
print(f"\nDate dtype: {analyzer.daily_stats['Date'].dtype}")
print(f"Date values: {analyzer.daily_stats['Date'].tolist()}")
print(f"Date min: {analyzer.daily_stats['Date'].min()}")
print(f"Date max: {analyzer.daily_stats['Date'].max()}")
