# HORIBA Air Quality Downloader - EXE Creation Guide

## GUI Features

The `horiba_downloader_gui.py` application provides a user-friendly interface to download HORIBA air quality data with the following options:

### 1. Quick Date Presets
- **Today**: Download today's data (00:00 - 23:59)
- **Yesterday**: Download yesterday's data
- **Last 7 Days**: Download last 7 days of data
- **This Month**: Download current month's data

### 2. Custom Date/Time Range
- **Start Date**: Select any start date (YYYY-MM-DD format)
- **End Date**: Select any end date
- **Start Time**: Select start hour and minute (HH:MM format)
- **End Time**: Select end hour and minute

### 3. Station Selection
Three modes available:
- **All (1-23)**: Download from all 23 stations
- **Range**: Select a range of stations (e.g., 1 to 15)
- **Specific**: Select specific station numbers (comma-separated, e.g., 1,5,10,15)

### 4. Output Management
- Configure output directory where downloaded files will be saved
- Browse button to select directory

---

## How to Create an EXE File

### Step 1: Install PyInstaller
```powershell
pip install pyinstaller
```

### Step 2: Create the EXE
Run this command in the project directory:

```powershell
pyinstaller --onefile --windowed --icon=app.ico --add-data ".env:." horiba_downloader_gui.py
```

**Options explained:**
- `--onefile`: Create a single .exe file (not a folder)
- `--windowed`: Hide the console window (GUI only)
- `--icon=app.ico`: Use a custom icon (optional, replace with your icon path)
- `--add-data ".env:."`: Include the .env file with credentials in the executable

### Step 3: Locate the EXE
The executable will be created in:
```
dist/horiba_downloader_gui.exe
```

### Step 4: Package for Distribution
Create a folder with:
- `horiba_downloader_gui.exe` (from `dist/` folder)
- `.env` (copy from project root)
- `README.txt` (instructions for users)

You can then distribute this as a standalone application.

---

## Alternative: Create with Console Window (for debugging)

If you want to see console output alongside the GUI:

```powershell
pyinstaller --onefile --icon=app.ico --add-data ".env:." horiba_downloader_gui.py
```

(Remove the `--windowed` flag)

---

## Troubleshooting

### Missing .env file in EXE
Make sure your `.env` file is in the same directory as the Python script when building.

### Icon not showing
Provide a valid `.ico` file or remove the `--icon` parameter.

### Application fails to start
- Ensure all dependencies are installed: `pip install requests python-dotenv beautifulsoup4`
- Check that `.env` file has valid credentials
- Run without `--windowed` flag to see error messages

---

## Usage Instructions for End Users

1. **Double-click** `horiba_downloader_gui.exe` to launch the application
2. **Select date range** using presets or custom dates
3. **Set time range** (defaults to 00:00 - 23:59)
4. **Choose stations** (all, range, or specific)
5. **Set output directory** (defaults to `output/` folder)
6. **Click Download** and monitor progress
7. Files will be saved in separate CSV and JSON formats per station, plus combined files

---

## What Gets Downloaded

For each station, the script saves:
- `station_XX.csv` - Individual station data in CSV format
- `station_XX.json` - Individual station data in JSON format
- `all_stations_combined.csv` - All selected stations combined
- `all_stations_combined.json` - All selected stations combined (JSON)

Data includes:
- Time
- PM measurements (1, 2.5, 4, 10, Total µg/m³)
- Particulate count (P/cm³)
- Gas measurements (CO, SO2, NO, NO2, NOx, O3, NH3)
- Weather data (Temperature, Pressure, Humidity, Wind Speed, Wind Direction)

---

## System Requirements

- Windows 7 or later
- `.env` file with HORIBA_LOGIN and HORIBA_PASSWORD configured
- Internet connection
- ~50MB free disk space (varies by data volume)

---

## Scripts Included

1. **horiba_bulk_downloader.py** - Command-line bulk download (2 stations, full date range)
2. **horiba_daily_downloader.py** - Command-line daily download (all 23 stations, yesterday 6PM-today 10AM)
3. **horiba_downloader_gui.py** - Interactive GUI application with flexible options
4. **horiba_downloader_gui.exe** - Standalone Windows executable (after building)

---

## Quick Commands

Build the EXE:
```powershell
cd d:\dev\air_quality
pip install pyinstaller
pyinstaller --onefile --windowed --add-data ".env:." horiba_downloader_gui.py
```

Test the GUI (before building EXE):
```powershell
python horiba_downloader_gui.py
```

Test daily downloader:
```powershell
python horiba_daily_downloader.py
```
