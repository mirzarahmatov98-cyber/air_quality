#!/usr/bin/env python3
"""
Script to access HORIBA Meteo webpage with authentication credentials from .env file.
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

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
    
    # Attempt login
    login_payload = {
        "login": LOGIN,
        "password": PASSWORD
    }
    
    # Try to login
    login_response = session.post(LOGIN_URL, data=login_payload)
    login_response.raise_for_status()
    
    print("Login successful!")
    
    # Now access the data page
    print(f"Accessing data from: {DATA_URL}")
    print(f"Parameters: {params}")
    
    response = session.get(DATA_URL, params=params)
    response.raise_for_status()
    
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse Preview (first 500 chars):")
    print(response.text[:500])
    
    # Optionally save the response to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(__file__).parent / "output" / f"horiba_data_{timestamp}.html"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"\nFull response saved to: {output_file}")

except requests.exceptions.RequestException as e:
    print(f"Error accessing the webpage: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text[:500]}")

except Exception as e:
    print(f"An error occurred: {e}")
