#!/usr/bin/env python3
"""
Quick Start Example - Air Quality Reporting
Demonstrates how to use the reporting system with downloaded data
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def example_basic_analysis():
    """Example 1: Basic analysis of the most recent download"""
    from air_quality_reporting import AirQualityAnalyzer
    
    print("=" * 70)
    print("EXAMPLE 1: Basic Analysis")
    print("=" * 70)
    
    # Create analyzer for station 1
    analyzer = AirQualityAnalyzer(
        data_dir='./output',  # Uses most recent download
        station_id=1,
        output_dir='./reports'
    )
    
    # Run complete analysis
    report = analyzer.run_complete_analysis()
    print(f"✓ Analysis complete: {report}")
    print()


def example_multiple_stations():
    """Example 2: Analyze multiple stations"""
    from air_quality_reporting import AirQualityAnalyzer
    
    print("=" * 70)
    print("EXAMPLE 2: Analyzing Multiple Stations")
    print("=" * 70)
    
    stations = [1, 15, 21]  # Adapt these to your actual station IDs
    
    for station_id in stations:
        print(f"Analyzing station {station_id}...")
        
        analyzer = AirQualityAnalyzer(
            data_dir='./output',
            station_id=station_id,
            output_dir=f'./reports/station_{station_id}'
        )
        
        try:
            analyzer.run_complete_analysis()
            print(f"✓ Station {station_id} complete\n")
        except Exception as e:
            print(f"✗ Station {station_id} failed: {str(e)}\n")


def example_custom_analysis():
    """Example 3: Custom data analysis without full report generation"""
    from air_quality_reporting import AirQualityAnalyzer
    import pandas as pd
    
    print("=" * 70)
    print("EXAMPLE 3: Custom Analysis")
    print("=" * 70)
    
    analyzer = AirQualityAnalyzer(
        data_dir='./output',
        station_id=1,
        output_dir='./reports'
    )
    
    # Load data
    analyzer.load_data()
    
    # Get summary statistics
    summary = analyzer.get_statistical_summary()
    
    print(f"Station: {summary['station_id']}")
    print(f"Period: {summary['data_period']}")
    print(f"Records: {summary['total_records']}")
    print()
    print("PM 2.5 Statistics:")
    print(f"  Mean: {summary['pm25']['mean']:.1f} µg/m³")
    print(f"  Median: {summary['pm25']['median']:.1f} µg/m³")
    print(f"  Range: {summary['pm25']['min']:.1f} - {summary['pm25']['max']:.1f} µg/m³")
    print(f"  Category: {summary['pm25']['who_category']}")
    print()
    print("PM 10 Statistics:")
    print(f"  Mean: {summary['pm10']['mean']:.1f} µg/m³")
    print(f"  Median: {summary['pm10']['median']:.1f} µg/m³")
    print(f"  Range: {summary['pm10']['min']:.1f} - {summary['pm10']['max']:.1f} µg/m³")
    print(f"  Category: {summary['pm10']['who_category']}")
    print()


def example_data_export():
    """Example 4: Export statistics as CSV for external analysis"""
    from air_quality_reporting import AirQualityAnalyzer
    
    print("=" * 70)
    print("EXAMPLE 4: Data Export")
    print("=" * 70)
    
    analyzer = AirQualityAnalyzer(
        data_dir='./output',
        station_id=1,
        output_dir='./reports'
    )
    
    # Load and calculate statistics
    analyzer.load_data()
    analyzer.calculate_statistics()
    
    # Export as CSV
    daily_csv, weekly_csv, monthly_csv = analyzer.generate_csv_reports()
    
    print(f"✓ Daily stats: {daily_csv}")
    print(f"✓ Weekly stats: {weekly_csv}")
    print(f"✓ Monthly stats: {monthly_csv}")
    print()
    
    # Show preview of daily stats
    import pandas as pd
    daily_df = pd.read_csv(daily_csv)
    print("Daily Statistics Preview:")
    print(daily_df.to_string(max_rows=5))
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Air Quality Reporting Examples',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python examples_reporting.py                    # Run all examples
  python examples_reporting.py --example 1       # Run example 1 only
  python examples_reporting.py --example 2       # Run example 2 only
        """
    )
    
    parser.add_argument('--example', type=int, choices=[1, 2, 3, 4],
                       help='Run specific example (1-4)')
    
    args = parser.parse_args()
    
    try:
        if args.example == 1 or not args.example:
            example_basic_analysis()
        if args.example == 2 or not args.example:
            example_multiple_stations()
        if args.example == 3 or not args.example:
            example_custom_analysis()
        if args.example == 4 or not args.example:
            example_data_export()
        
        print("=" * 70)
        print("All examples completed!")
        print("=" * 70)
        print("\nNext Steps:")
        print("1. Check ./reports for generated HTML reports")
        print("2. Open station_1_report.html in your web browser")
        print("3. View PNG plots for visualization")
        print("4. Analyze CSV exports in Excel or other tools")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
