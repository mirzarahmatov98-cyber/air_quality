#!/usr/bin/env python3
"""
Bulk download HORIBA air quality data from all stations for a date range.
Downloads data from 1 Jan 2026 to current date, respecting rate limits.
"""

import os
import requests
import time
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"bulk_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get credentials
LOGIN = os.getenv("HORIBA_LOGIN", "").strip(' "\'')
PASSWORD = os.getenv("HORIBA_PASSWORD", "").strip(' "\'')

if not LOGIN or not PASSWORD:
    raise ValueError("Missing HORIBA_LOGIN or HORIBA_PASSWORD in .env file")

# Configuration
BASE_URL = "https://horiba.meteo.uz"
AUTHORIZE_URL = f"{BASE_URL}/authorize.php"
DATA_URL = f"{BASE_URL}/index-new.php"
DATE_START = "2026-01-01"
DATE_END = "2026-04-14"
STATIONS_TO_DOWNLOAD = [1, 15]  # Test with 2 stations
REQUEST_DELAY = 1.0  # seconds between requests

# Create output directories
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
bulk_output_dir = Path(__file__).parent / "output" / f"bulk_download_{timestamp}"
bulk_output_dir.mkdir(parents=True, exist_ok=True)

csv_dir = bulk_output_dir / "csv"
json_dir = bulk_output_dir / "json"
csv_dir.mkdir(exist_ok=True)
json_dir.mkdir(exist_ok=True)

print(f"Output directory: {bulk_output_dir}")
print(f"Request delay: {REQUEST_DELAY}s per request")
print(f"Date range: {DATE_START} to {DATE_END}")
print(f"Stations: {STATIONS_TO_DOWNLOAD}\n")

# Create session for all requests
session = requests.Session()
login_payload = {
    "username": LOGIN,
    "password": PASSWORD
}

# Login once
print(f"Logging in as: {LOGIN}")
print(f"  Login URL: {AUTHORIZE_URL}")
try:
    print("  Sending login request...")
    login_response = session.post(AUTHORIZE_URL, data=login_payload, timeout=10)
    login_response.raise_for_status()
    print(f"  Response status: {login_response.status_code} {login_response.reason}")
    print(f"  Session cookies: {len(session.cookies)} cookie(s) received")
    if session.cookies:
        for cookie_name in session.cookies:
            print(f"    - {cookie_name}")
    print("  ✓ Login successful!\n")
except requests.exceptions.Timeout:
    print(f"  ✗ Login failed: Connection timeout (10s)")
    exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"  ✗ Login failed: Connection error - {str(e)[:100]}")
    exit(1)
except Exception as e:
    print(f"  ✗ Login failed: {str(e)[:100]}")
    exit(1)

# Track statistics
all_rows_data = []  # To combine all data
headers = None
stats = {
    "total_requests": 0,
    "successful": 0,
    "failed": 0,
    "total_rows": 0,
}

# Download data for each station
for station_id in STATIONS_TO_DOWNLOAD:
    station_num = STATIONS_TO_DOWNLOAD.index(station_id) + 1
    print(f"\n[{station_num}/{len(STATIONS_TO_DOWNLOAD)}] Downloading station {station_id}...")
    
    params = {
        "station_id": station_id,
        "date_start": DATE_START,
        "date_end": DATE_END,
        "has_filter": 1
    }
    
    print(f"  Request URL: {DATA_URL}")
    print(f"  Parameters: station_id={station_id}, date_range={DATE_START} to {DATE_END}")
    
    try:
        stats["total_requests"] += 1
        
        # Make request
        print("  Sending request...", end=" ", flush=True)
        response = session.get(DATA_URL, params=params, timeout=10)
        response.raise_for_status()
        print(f"✓ (Status: {response.status_code}, Size: {len(response.text)} bytes)")
        
        # Parse HTML
        print("  Parsing HTML response...", end=" ", flush=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            print("✗ No table found")
            stats["failed"] += 1
            continue
        print("✓")
        
        # Extract headers (only from first station)
        if headers is None:
            print("  Extracting column headers...", end=" ", flush=True)
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
                    print(f"✓ ({len(headers)} columns)")
                    for idx, header in enumerate(headers, 1):
                        print(f"    {idx}. {header}")
                else:
                    print("✗ No header row found")
            else:
                print("✗ No thead found")
        
        # Extract rows
        print("  Extracting data rows...", end=" ", flush=True)
        rows = []
        all_trs = table.find_all('tr')[1:]  # Skip header row
        
        for tr in all_trs:
            cols = [td.get_text(strip=True) for td in tr.find_all('td')]
            if cols:
                # Split if multiple records in single row
                num_records = len(cols) // len(headers) if headers else 0
                if num_records > 0:
                    for record_idx in range(num_records):
                        start_idx = record_idx * len(headers)
                        end_idx = start_idx + len(headers)
                        if end_idx <= len(cols):
                            row_data = cols[start_idx:end_idx]
                            rows.append(row_data)
                            # Add station ID to combined dataset
                            all_rows_data.append([station_id] + row_data)
        print(f"✓ ({len(rows)} records)")
        
        # Save CSV for this station
        csv_file = csv_dir / f"station_{station_id:02d}.csv"
        print(f"  Saving CSV: {csv_file.name}...", end=" ", flush=True)
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(['Station_ID'] + headers)
            writer.writerows([[station_id] + row for row in rows])
        print("✓")
        
        # Save JSON for this station
        json_file = json_dir / f"station_{station_id:02d}.json"
        print(f"  Saving JSON: {json_file.name}...", end=" ", flush=True)
        json_data = []
        if headers:
            for row in rows:
                row_dict = {"Station_ID": station_id}
                row_dict.update({headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))})
                json_data.append(row_dict)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print("✓")
        
        stats["successful"] += 1
        stats["total_rows"] += len(rows)
        
        print(f"  ✓ Station {station_id} completed successfully")
        
    except requests.exceptions.Timeout:
        stats["failed"] += 1
        print(f"✗ Connection timeout (10s)")
    except requests.exceptions.ConnectionError as e:
        stats["failed"] += 1
        print(f"✗ Connection error: {str(e)[:50]}")
    except requests.exceptions.RequestException as e:
        stats["failed"] += 1
        print(f"✗ Request error: {str(e)[:50]}")
    except Exception as e:
        stats["failed"] += 1
        print(f"✗ Error: {str(e)[:50]}")
    
    # Respect rate limits
    if station_id != STATIONS_TO_DOWNLOAD[-1]:  # Don't wait after last station
        print(f"  Waiting {REQUEST_DELAY}s before next request...")
        time.sleep(REQUEST_DELAY)

print("\n" + "="*70)
print("DOWNLOAD SUMMARY")
print("="*70)
print(f"Total requests: {stats['total_requests']}")
print(f"Successful: {stats['successful']}")
print(f"Failed: {stats['failed']}")
print(f"Total rows downloaded: {stats['total_rows']}")
print(f"Average rows per station: {stats['total_rows'] // max(stats['successful'], 1):.0f}")

# Save combined dataset
if all_rows_data and headers:
    print("\n" + "="*70)
    print("SAVING COMBINED DATASETS")
    print("="*70)
    
    combined_csv = bulk_output_dir / f"all_stations_combined.csv"
    combined_json = bulk_output_dir / f"all_stations_combined.json"
    
    # Save combined CSV
    print(f"Saving combined CSV: {combined_csv.name}...", end=" ", flush=True)
    with open(combined_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Station_ID'] + headers)
        writer.writerows(all_rows_data)
    print(f"✓ ({len(all_rows_data)} rows)")
    
    # Save combined JSON
    print(f"Saving combined JSON: {combined_json.name}...", end=" ", flush=True)
    combined_json_data = []
    for row_data in all_rows_data:
        row_dict = {"Station_ID": row_data[0]}
        row_dict.update({headers[i]: row_data[i+1] if i < len(row_data)-1 else '' for i in range(len(headers))})
        combined_json_data.append(row_dict)
    
    with open(combined_json, 'w', encoding='utf-8') as f:
        json.dump(combined_json_data, f, indent=2, ensure_ascii=False)
    print(f"✓ ({len(combined_json_data)} rows)")
else:
    print("\nNo data to combine (no successful downloads)")

print(f"\nAll files saved to: {bulk_output_dir}")
print("="*70)
