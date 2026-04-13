#!/usr/bin/env python3
"""
Download HORIBA air quality data from all 23 stations for a recent time period.
Downloads data from yesterday 6 PM to today 10 AM.
"""

import os
import requests
import time
import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"daily_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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

# Calculate date range: Yesterday 6 PM to Today 10 AM
today = datetime.now().date()
yesterday = today - timedelta(days=1)

# Format dates for the API (YYYY-MM-DD format)
# Request: yesterday 6 PM to today 10 AM
DATE_START_DATE = yesterday
DATE_START_TIME = "18:00"  # 6 PM
DATE_END_DATE = today
DATE_END_TIME = "10:00"    # 10 AM

# Try different date-time formats based on what the API accepts
DATE_START = f"{DATE_START_DATE} {DATE_START_TIME}"  # YYYY-MM-DD HH:MM
DATE_END = f"{DATE_END_DATE} {DATE_END_TIME}"        # YYYY-MM-DD HH:MM

# All 23 stations
STATIONS_TO_DOWNLOAD = list(range(1, 24))  # Stations 1-23
REQUEST_DELAY = 0.5  # seconds between requests (reduce to speed up slightly)

# Create output directories
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
daily_output_dir = Path(__file__).parent / "output" / f"daily_download_{timestamp}"
daily_output_dir.mkdir(parents=True, exist_ok=True)

csv_dir = daily_output_dir / "csv"
json_dir = daily_output_dir / "json"
csv_dir.mkdir(exist_ok=True)
json_dir.mkdir(exist_ok=True)

print(f"Output directory: {daily_output_dir}")
print(f"Request delay: {REQUEST_DELAY}s per request")
print(f"Date range: {DATE_START} to {DATE_END}")
print(f"Stations: {len(STATIONS_TO_DOWNLOAD)} stations ({STATIONS_TO_DOWNLOAD[0]}-{STATIONS_TO_DOWNLOAD[-1]})\n")

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
    "station_details": {}
}

# Download data for each station
print("="*70)
print(f"DOWNLOADING DATA FROM {len(STATIONS_TO_DOWNLOAD)} STATIONS")
print("="*70)

for station_id in STATIONS_TO_DOWNLOAD:
    station_num = STATIONS_TO_DOWNLOAD.index(station_id) + 1
    print(f"\n[{station_num}/{len(STATIONS_TO_DOWNLOAD)}] Downloading station {station_id}...", end=" ", flush=True)
    
    params = {
        "station_id": station_id,
        "date_start": DATE_START,
        "date_end": DATE_END,
        "has_filter": 1
    }
    
    try:
        stats["total_requests"] += 1
        
        # Make request
        response = session.get(DATA_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            print(f"WARNING: No table found")
            stats["failed"] += 1
            stats["station_details"][station_id] = {"status": "FAILED", "reason": "No table found", "rows": 0}
            continue
        
        # Extract headers (only from first station)
        if headers is None:
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        # Extract rows
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
        
        # Save CSV for this station
        csv_file = csv_dir / f"station_{station_id:02d}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(['Station_ID'] + headers)
            writer.writerows([[station_id] + row for row in rows])
        
        # Save JSON for this station
        json_file = json_dir / f"station_{station_id:02d}.json"
        json_data = []
        if headers:
            for row in rows:
                row_dict = {"Station_ID": station_id}
                row_dict.update({headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))})
                json_data.append(row_dict)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        stats["successful"] += 1
        stats["total_rows"] += len(rows)
        stats["station_details"][station_id] = {"status": "OK", "rows": len(rows)}
        
        print(f"OK ({len(rows)} records)")
        
    except requests.exceptions.Timeout:
        stats["failed"] += 1
        print(f"TIMEOUT")
        stats["station_details"][station_id] = {"status": "FAILED", "reason": "Timeout", "rows": 0}
    except requests.exceptions.ConnectionError as e:
        stats["failed"] += 1
        print(f"CONNECTION ERROR")
        stats["station_details"][station_id] = {"status": "FAILED", "reason": "Connection error", "rows": 0}
    except requests.exceptions.RequestException as e:
        stats["failed"] += 1
        print(f"REQUEST ERROR")
        stats["station_details"][station_id] = {"status": "FAILED", "reason": f"Request error: {str(e)[:30]}", "rows": 0}
    except Exception as e:
        stats["failed"] += 1
        print(f"ERROR")
        stats["station_details"][station_id] = {"status": "FAILED", "reason": f"Error: {str(e)[:30]}", "rows": 0}
    
    # Respect rate limits
    if station_id != STATIONS_TO_DOWNLOAD[-1]:  # Don't wait after last station
        time.sleep(REQUEST_DELAY)

print("\n" + "="*70)
print("DOWNLOAD SUMMARY")
print("="*70)
print(f"Total requests: {stats['total_requests']}")
print(f"Successful: {stats['successful']}")
print(f"Failed: {stats['failed']}")
print(f"Total rows downloaded: {stats['total_rows']}")
if stats['successful'] > 0:
    print(f"Average rows per station: {stats['total_rows'] // stats['successful']:.0f}")

# Print station details
print("\n" + "="*70)
print("STATION-BY-STATION RESULTS")
print("="*70)
for station_id in STATIONS_TO_DOWNLOAD:
    detail = stats["station_details"].get(station_id, {})
    status = detail.get("status", "UNKNOWN")
    rows = detail.get("rows", 0)
    if status == "OK":
        print(f"Station {station_id:2d}: ✓ {rows:7d} records")
    else:
        reason = detail.get("reason", "Unknown error")
        print(f"Station {station_id:2d}: ✗ FAILED ({reason})")

# Save combined dataset
if all_rows_data and headers:
    print("\n" + "="*70)
    print("SAVING COMBINED DATASETS")
    print("="*70)
    
    combined_csv = daily_output_dir / f"all_stations_combined.csv"
    combined_json = daily_output_dir / f"all_stations_combined.json"
    
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

print(f"\nAll files saved to: {daily_output_dir}")
print("="*70)
