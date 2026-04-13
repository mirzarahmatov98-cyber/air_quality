# HORIBA Air Quality Downloader - Complete Guide

## ✅ Successfully Created

A complete suite of tools for downloading HORIBA air quality data with three different interfaces:

### 1. **horiba_bulk_downloader.py** - Bulk Command-Line Tool
- Downloads data from stations **1 and 15**
- Date range: **2026-01-01 to 2026-04-14** (edit in script to change)
- Output: Timestamped folder with CSV and JSON files
- **Usage**: `python horiba_bulk_downloader.py`

### 2. **horiba_daily_downloader.py** - Daily Command-Line Tool
- Downloads data from **all 23 stations**
- Date range: **Yesterday 6 PM to Today 10 AM** (auto-calculated)
- Output: Timestamped folder with CSV and JSON files
- **Usage**: `python horiba_daily_downloader.py`

### 3. **horiba_downloader_gui.py** - Interactive GUI Application ⭐ (NEW)
- **Most flexible option** with user-friendly interface
- Download from **1 to 23 stations** with multiple selection modes
- **Custom date and time selection** with presets
- Real-time progress tracking
- Browse output directory option
- Separate CSV and JSON files
- **Usage**: `python horiba_downloader_gui.py`

---

## 🎯 GUI Features (Recommended for Most Users)

### Quick Date Presets
Click any preset button to automatically fill date/time fields:
- **Today** → Today 00:00 to 23:59
- **Yesterday** → Yesterday 00:00 to 23:59
- **Last 7 Days** → Last 7 days, full 24 hours
- **This Month** → 1st of month to today

### Station Selection Modes

#### All Stations (Default)
- Automatically selects all 23 stations
- Fastest way to get comprehensive data

#### Range Selection
- **From**: Set starting station (e.g., 1)
- **To**: Set ending station (e.g., 15)
- Good for downloading a subset like stations 1-10

#### Specific Selection
- **Station Numbers**: Enter comma-separated values
- Example: `1,5,10,15,23` (spaces optional)
- Best for targeting exact stations of interest

### Time Range
- **Start Time**: Hour:Minute format (e.g., 08:30 for 8:30 AM)
- **End Time**: Hour:Minute format (e.g., 18:00 for 6:00 PM)
- Supports 24-hour format (00:00 to 23:59)

### Output Options
- **Default**: `output/` folder in project directory
- **Browse**: Click to select any custom directory
- Creates timestamped subfolder for each download

### Progress Section
- Real-time download progress
- Shows success/failure per station
- Displays record count per station
- Final summary statistics

---

## 🚀 Running the EXE

### Easy Distribution
The EXE file (`dist/horiba_downloader_gui.exe`) is ready to use!

**To use the EXE:**

1. **Copy these files to a folder:**
   - `horiba_downloader_gui.exe` (from `dist/` folder)
   - `.env` (your credentials file)

2. **Optional but recommended:**
   - Create a shortcut on desktop
   - Create readme for end users

3. **Double-click the .exe to launch**

---

## 📊 Data Downloaded

### Fields per Record
Each downloaded record includes:
- **Time**: Timestamp of measurement
- **Particulate Matter**: PM₁, PM₂.₅, PM₄, PM₁₀, PM Total (µg/m³)
- **Particle Count**: Cn (P/cm³)
- **Gases**: CO, SO₂, NO, NO₂, NOₓ, O₃, NH₃ (mg/m³)
- **Weather**: Temperature (°C), Pressure (hPa), Humidity (%), Wind Speed (km/h), Wind Direction (°)

### Output Formats
- **CSV**: Easy to open in Excel, compatible with analysis tools
- **JSON**: Structured data for programmatic access
- **Combined files**: All stations merged into single files for comparison

---

## 📋 Recent Test Results

**Daily Downloader Test** (Yesterday 6 PM to Today 10 AM):
- 23 stations requested
- 16 stations successful (73%)
- 4,530 total records downloaded
- 283 records average per station
- Execution time: ~30 seconds

**Sample Stations:**
- Station 1: ✓ 300 records
- Station 15: ✓ 305 records
- Station 5: ✓ 300 records
- (Some stations had no data for this period)

---

## ⚙️ Configuration

### Requirements
- `.env` file with credentials:
  ```
  HORIBA_LOGIN=your_username
  HORIBA_PASSWORD=your_password
  ```

- Python packages (for running Python scripts):
  ```
  requests
  beautifulsoup4
  python-dotenv
  ```

- For building EXE:
  ```
  pyinstaller
  tkinter (included with Python)
  ```

---

## 🔧 Troubleshooting

### GUI Won't Start
1. Ensure `.env` file is in the same directory as the script
2. Verify credentials are correct in `.env`
3. Check internet connection
4. Try running from command line: `python horiba_downloader_gui.py` (to see error messages)

### EXE Won't Launch
1. Make sure `.env` is in the same folder as the .exe
2. Try running from different folder
3. Rebuild EXE if needed: See EXE_CREATION_GUIDE.md

### No Data Downloaded
1. Check if station has data for selected date range
2. Verify date/time format is correct (YYYY-MM-DD, HH:MM)
3. Try a different date or "All Stations" mode
4. Check the log/progress section for specific errors

### Download Takes Too Long
- Normal: ~30 seconds for 23 stations
- Reduce delay: Edit `REQUEST_DELAY` in script (default 0.5s)
- Try specific stations instead of all
- Check internet speed

---

## 📁 File Organization

```
air_quality/
├── horiba_bulk_downloader.py      # Bulk tool (2 stations, large date range)
├── horiba_daily_downloader.py     # Daily tool (all stations, 16-hour window)
├── horiba_downloader_gui.py       # GUI tool (flexible options)
├── dist/
│   └── horiba_downloader_gui.exe  # ⭐ Ready-to-use executable
├── output/
│   ├── bulk_download_20260413_104032/
│   ├── daily_download_20260413_104900/
│   └── download_YYYYMMDD_HHMMSS/  # New downloads here
├── .env                            # Your credentials (KEEP SECRET!)
├── EXE_CREATION_GUIDE.md          # How to rebuild/customize EXE
├── README.md
└── requirements.txt
```

---

## 🎯 Which Tool to Use?

| Tool | Use Case | Users |
|------|----------|-------|
| **Bulk Downloader** | Historical analysis, large date ranges, specific stations | Data scientists, analysts |
| **Daily Downloader** | Daily scheduled downloads, all stations, recent data | Automated scripts, cron jobs |
| **GUI Application** | Flexible downloads, one-time pulls, casual use | End users, non-technical staff |
| **GUI .EXE** | No Python needed, standalone application | Business users, distributed to others |

---

## 🚀 Next Steps

### To use immediately:
1. Use the GUI: `python horiba_downloader_gui.py`
2. Or double-click: `dist/horiba_downloader_gui.exe`

### To customize:
1. Edit date ranges in `horiba_bulk_downloader.py` or `horiba_daily_downloader.py`
2. Modify request delay for faster/slower downloads
3. Add logging to the GUI application
4. Rebuild EXE after changes

### To distribute:
1. Copy `dist/horiba_downloader_gui.exe` to users
2. Include `.env` file with credentials
3. Create user manual with screenshots
4. Consider signing the EXE for Windows SmartScreen verification

---

## 📞 Support

**Common Issues:**
- Can't connect to server → Check internet, verify URL in code
- Wrong credentials → Update `.env` file
- No stations have data → Try different date range
- EXE won't run → Rebuild or check Window Defender/antivirus

**Performance:**
- Slow downloads → Increase REQUEST_DELAY (in code)
- Fast downloads → Decrease REQUEST_DELAY
- Limited by server response time (~0.5-2s per station)

---

**Last Updated**: April 13, 2026
**EXE Size**: ~14.5 MB (includes Python runtime)
**Status**: ✅ Ready for production use
