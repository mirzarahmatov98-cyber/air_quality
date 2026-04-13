#!/usr/bin/env python3
"""
Script to access HORIBA Meteo webpage with authentication credentials from .env file.
Extracts air quality data table and saves as CSV and JSON.
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import csv
import json

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Get credentials
LOGIN = os.getenv("HORIBA_LOGIN", "").strip(' "\'')
PASSWORD = os.getenv("HORIBA_PASSWORD", "").strip(' "\'')

if not LOGIN or not PASSWORD:
    raise ValueError("Missing HORIBA_LOGIN or HORIBA_PASSWORD in .env file")

# Create a session to maintain cookies across requests
session = requests.Session()

# URL parameters
BASE_URL = "https://horiba.meteo.uz"
LOGIN_URL = f"{BASE_URL}/login.php"  # Adjust if login endpoint is different
DATA_URL = "https://horiba.meteo.uz/index-new.php"

# Parameters for the data request
params = {
    "station_id": 1,
    "date_start": "2026-04-13",
    "date_end": "2026-04-13",
    "has_filter": 1
}

try:
    print(f"Logging in with username: {LOGIN}...")
    
    # Attempt login with the correct endpoint and field names
    authorize_url = f"{BASE_URL}/authorize.php"
    login_payload = {
        "username": LOGIN,
        "password": PASSWORD
    }
    
    # Try to login
    login_response = session.post(authorize_url, data=login_payload)
    login_response.raise_for_status()
    
    print("Login successful!")
    
    # Now access the data page
    print(f"Accessing data from: {DATA_URL}")
    print(f"Parameters: {params}")
    
    response = session.get(DATA_URL, params=params)
    response.raise_for_status()
    
    print(f"Status Code: {response.status_code}")
    
    # Parse the HTML and extract table data
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table
    table = soup.find('table')
    if not table:
        print("No table found in the response!")
        exit(1)
    
    # Extract headers
    headers = []
    header_row = table.find('tr')
    if header_row:
        for th in header_row.find_all('th'):
            headers.append(th.get_text(strip=True))
    
    if not headers:
        # Try td tags if th is not available
        for td in header_row.find_all('td'):
            headers.append(td.get_text(strip=True))
    
    print(f"\nFound {len(headers)} columns")
    print(f"Columns: {headers}")
    
    # Extract table rows
    rows = []
    all_tr = table.find_all('tr')
    for tr in all_tr[1:]:  # Skip header row
        cols = []
        for td in tr.find_all('td'):
            cols.append(td.get_text(strip=True))
        # Only add if we have the right number of columns
        if len(cols) == len(headers):
            rows.append(cols)
    
    print(f"Extracted {len(rows)} data rows")
    
    # Save as CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = Path(__file__).parent / "output" / f"horiba_data_{timestamp}.csv"
    csv_file.parent.mkdir(exist_ok=True)
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"\n✅ CSV saved: {csv_file}")
    
    # Save as JSON
    json_file = Path(__file__).parent / "output" / f"horiba_data_{timestamp}.json"
    json_data = []
    for row in rows:
        row_dict = {headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))}
        json_data.append(row_dict)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON saved: {json_file}")
    
    # Display first few rows
    print(f"\n📊 First 3 rows of data:")
    print("-" * 100)
    for i, row in enumerate(rows[:3]):
        print(f"Row {i+1}: {row[:5]}...")  # Print first 5 columns
    
    # Save full HTML as well
    html_file = Path(__file__).parent / "output" / f"horiba_data_{timestamp}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"\n📄 Full HTML saved: {html_file}")

except requests.exceptions.RequestException as e:
    print(f"Error accessing the webpage: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text[:500]}")

except Exception as e:
    print(f"An error occurred: {e}")
