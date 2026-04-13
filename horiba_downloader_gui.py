#!/usr/bin/env python3
"""
HORIBA Air Quality Data Downloader GUI
Allows users to select date range, time range, and stations to download.
"""

import os
import sys
import requests
import time
import csv
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class HoribaDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HORIBA Air Quality Downloader")
        self.root.geometry("700x750")
        self.root.resizable(False, False)
        
        # Credentials
        self.LOGIN = os.getenv("HORIBA_LOGIN", "").strip(' "\'')
        self.PASSWORD = os.getenv("HORIBA_PASSWORD", "").strip(' "\'')
        
        if not self.LOGIN or not self.PASSWORD:
            messagebox.showerror("Error", "Missing HORIBA_LOGIN or HORIBA_PASSWORD in .env file")
            sys.exit(1)
        
        # Configuration
        self.BASE_URL = "https://horiba.meteo.uz"
        self.AUTHORIZE_URL = f"{self.BASE_URL}/authorize.php"
        self.DATA_URL = f"{self.BASE_URL}/index-new.php"
        self.download_in_progress = False
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="HORIBA Data Downloader", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Date Range Section
        date_frame = ttk.LabelFrame(main_frame, text="Date Range", padding="10")
        date_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Quick presets
        ttk.Label(date_frame, text="Quick Presets:").grid(row=0, column=0, sticky=tk.W)
        preset_frame = ttk.Frame(date_frame)
        preset_frame.grid(row=0, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Button(preset_frame, text="Today", width=10, command=self.preset_today).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Yesterday", width=10, command=self.preset_yesterday).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Last 7 Days", width=10, command=self.preset_last_7).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="This Month", width=10, command=self.preset_this_month).pack(side=tk.LEFT, padx=2)
        
        # Start date
        ttk.Label(date_frame, text="Start Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.start_date, width=15).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(date_frame, text="(YYYY-MM-DD)").grid(row=1, column=2, sticky=tk.W)
        
        # End date
        ttk.Label(date_frame, text="End Date:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.end_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.end_date, width=15).grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(date_frame, text="(YYYY-MM-DD)").grid(row=2, column=2, sticky=tk.W)
        
        # Time Range Section
        time_frame = ttk.LabelFrame(main_frame, text="Time Range", padding="10")
        time_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Start time
        ttk.Label(time_frame, text="Start Time:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_time = tk.StringVar(value="00:00")
        ttk.Entry(time_frame, textvariable=self.start_time, width=15).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(time_frame, text="(HH:MM)").grid(row=0, column=2, sticky=tk.W)
        
        # End time
        ttk.Label(time_frame, text="End Time:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_time = tk.StringVar(value="23:59")
        ttk.Entry(time_frame, textvariable=self.end_time, width=15).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(time_frame, text="(HH:MM)").grid(row=1, column=2, sticky=tk.W)
        
        # Stations Section
        station_frame = ttk.LabelFrame(main_frame, text="Stations", padding="10")
        station_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Station selection mode
        ttk.Label(station_frame, text="Select Stations:").grid(row=0, column=0, sticky=tk.W, pady=5)
        selection_frame = ttk.Frame(station_frame)
        selection_frame.grid(row=0, column=1, columnspan=2, sticky=tk.W)
        
        self.station_mode = tk.StringVar(value="all")
        ttk.Radiobutton(selection_frame, text="All (1-23)", variable=self.station_mode, value="all", command=self.update_station_display).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(selection_frame, text="Range", variable=self.station_mode, value="range", command=self.update_station_display).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(selection_frame, text="Specific", variable=self.station_mode, value="specific", command=self.update_station_display).pack(side=tk.LEFT, padx=5)
        
        # Station range inputs
        self.station_range_frame = ttk.Frame(station_frame)
        self.station_range_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(self.station_range_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.station_from = tk.StringVar(value="1")
        ttk.Spinbox(self.station_range_frame, from_=1, to=23, textvariable=self.station_from, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.station_range_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.station_to = tk.StringVar(value="23")
        ttk.Spinbox(self.station_range_frame, from_=1, to=23, textvariable=self.station_to, width=5).pack(side=tk.LEFT, padx=2)
        
        # Specific stations input
        self.station_specific_frame = ttk.Frame(station_frame)
        self.station_specific_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(self.station_specific_frame, text="Station Numbers:").pack(side=tk.LEFT, padx=5)
        self.station_specific = tk.StringVar(value="1,15")
        ttk.Entry(self.station_specific_frame, textvariable=self.station_specific, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Label(self.station_specific_frame, text="(comma-separated)").pack(side=tk.LEFT)
        
        # Hide initially
        self.station_range_frame.grid_remove()
        self.station_specific_frame.grid_remove()
        
        # Output directory
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_dir = tk.StringVar(value=str(Path(__file__).parent / "output"))
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_text = tk.Text(progress_frame, height=8, width=80, state=tk.DISABLED)
        self.progress_text.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(progress_frame, orient=tk.VERTICAL, command=self.progress_text.yview)
        scrollbar.grid(row=0, column=3, sticky=(tk.N, tk.S))
        self.progress_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.download_btn = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Log", command=self.clear_progress)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.exit_btn = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        self.exit_btn.pack(side=tk.LEFT, padx=5)
    
    def update_station_display(self):
        mode = self.station_mode.get()
        self.station_range_frame.grid_remove()
        self.station_specific_frame.grid_remove()
        
        if mode == "range":
            self.station_range_frame.grid()
        elif mode == "specific":
            self.station_specific_frame.grid()
    
    def preset_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.start_date.set(today)
        self.end_date.set(today)
        self.start_time.set("00:00")
        self.end_time.set("23:59")
    
    def preset_yesterday(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.start_date.set(yesterday)
        self.end_date.set(yesterday)
        self.start_time.set("00:00")
        self.end_time.set("23:59")
    
    def preset_last_7(self):
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.start_date.set(start_date)
        self.end_date.set(end_date)
        self.start_time.set("00:00")
        self.end_time.set("23:59")
    
    def preset_this_month(self):
        today = datetime.now()
        first_day = today.replace(day=1).strftime("%Y-%m-%d")
        last_day = today.strftime("%Y-%m-%d")
        self.start_date.set(first_day)
        self.end_date.set(last_day)
        self.start_time.set("00:00")
        self.end_time.set("23:59")
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
    
    def log_progress(self, message):
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)
        self.root.update()
    
    def clear_progress(self):
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.config(state=tk.DISABLED)
    
    def get_stations(self):
        mode = self.station_mode.get()
        if mode == "all":
            return list(range(1, 24))
        elif mode == "range":
            start = int(self.station_from.get())
            end = int(self.station_to.get())
            return list(range(start, end + 1))
        else:  # specific
            try:
                return [int(x.strip()) for x in self.station_specific.get().split(",")]
            except:
                messagebox.showerror("Error", "Invalid station numbers format")
                return []
    
    def start_download(self):
        if self.download_in_progress:
            messagebox.showwarning("Warning", "Download already in progress")
            return
        
        self.download_btn.config(state=tk.DISABLED)
        self.download_in_progress = True
        
        # Run download in separate thread
        thread = threading.Thread(target=self.download_data)
        thread.start()
    
    def download_data(self):
        try:
            self.clear_progress()
            self.log_progress("Starting download...\n")
            
            # Validate inputs
            start_date = self.start_date.get()
            end_date = self.end_date.get()
            start_time = self.start_time.get()
            end_time = self.end_time.get()
            
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
                datetime.strptime(start_time, "%H:%M")
                datetime.strptime(end_time, "%H:%M")
            except ValueError as e:
                self.log_progress(f"Error: Invalid date/time format - {str(e)}")
                self.download_btn.config(state=tk.NORMAL)
                self.download_in_progress = False
                return
            
            DATE_START = f"{start_date} {start_time}"
            DATE_END = f"{end_date} {end_time}"
            stations = self.get_stations()
            
            if not stations:
                self.log_progress("Error: No stations selected")
                self.download_btn.config(state=tk.NORMAL)
                self.download_in_progress = False
                return
            
            # Create output directory
            output_base = Path(self.output_dir.get())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_dir = output_base / f"download_{timestamp}"
            download_dir.mkdir(parents=True, exist_ok=True)
            
            csv_dir = download_dir / "csv"
            json_dir = download_dir / "json"
            csv_dir.mkdir(exist_ok=True)
            json_dir.mkdir(exist_ok=True)
            
            self.log_progress(f"Date Range: {DATE_START} to {DATE_END}")
            self.log_progress(f"Stations: {len(stations)} ({stations[0]}-{stations[-1]})")
            self.log_progress(f"Output: {download_dir}\n")
            
            # Login
            self.log_progress("Logging in...")
            session = requests.Session()
            login_payload = {
                "username": self.LOGIN,
                "password": self.PASSWORD
            }
            
            login_response = session.post(self.AUTHORIZE_URL, data=login_payload, timeout=10)
            login_response.raise_for_status()
            self.log_progress(f"✓ Login successful\n")
            
            # Download from each station
            all_rows_data = []
            headers = None
            stats = {"total": len(stations), "successful": 0, "failed": 0, "total_rows": 0}
            
            for idx, station_id in enumerate(stations):
                self.log_progress(f"[{idx+1}/{len(stations)}] Station {station_id}...", )
                
                params = {
                    "station_id": station_id,
                    "date_start": DATE_START,
                    "date_end": DATE_END,
                    "has_filter": 1
                }
                
                try:
                    response = session.get(self.DATA_URL, params=params, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table')
                    
                    if not table:
                        self.progress_text.config(state=tk.NORMAL)
                        self.progress_text.delete("end-2c", tk.END)
                        self.progress_text.config(state=tk.DISABLED)
                        self.log_progress(f"[{idx+1}/{len(stations)}] Station {station_id}... NO DATA")
                        stats["failed"] += 1
                        time.sleep(0.3)
                        continue
                    
                    # Extract headers
                    if headers is None:
                        thead = table.find('thead')
                        if thead:
                            header_row = thead.find('tr')
                            if header_row:
                                headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
                    
                    # Extract rows
                    rows = []
                    all_trs = table.find_all('tr')[1:]
                    
                    for tr in all_trs:
                        cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                        if cols:
                            num_records = len(cols) // len(headers) if headers else 0
                            if num_records > 0:
                                for record_idx in range(num_records):
                                    start_idx = record_idx * len(headers)
                                    end_idx = start_idx + len(headers)
                                    if end_idx <= len(cols):
                                        row_data = cols[start_idx:end_idx]
                                        rows.append(row_data)
                                        all_rows_data.append([station_id] + row_data)
                    
                    # Save station data
                    csv_file = csv_dir / f"station_{station_id:02d}.csv"
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        if headers:
                            writer.writerow(['Station_ID'] + headers)
                        writer.writerows([[station_id] + row for row in rows])
                    
                    json_file = json_dir / f"station_{station_id:02d}.json"
                    json_data = []
                    if headers:
                        for row in rows:
                            row_dict = {"Station_ID": station_id}
                            row_dict.update({headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))})
                            json_data.append(row_dict)
                    
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    
                    self.progress_text.config(state=tk.NORMAL)
                    self.progress_text.delete("end-2c", tk.END)
                    self.progress_text.config(state=tk.DISABLED)
                    self.log_progress(f"[{idx+1}/{len(stations)}] Station {station_id}... OK ({len(rows)} records)")
                    
                    stats["successful"] += 1
                    stats["total_rows"] += len(rows)
                    time.sleep(0.3)
                    
                except Exception as e:
                    self.progress_text.config(state=tk.NORMAL)
                    self.progress_text.delete("end-2c", tk.END)
                    self.progress_text.config(state=tk.DISABLED)
                    self.log_progress(f"[{idx+1}/{len(stations)}] Station {station_id}... ERROR")
                    stats["failed"] += 1
                    time.sleep(0.3)
            
            # Save combined files
            if all_rows_data and headers:
                combined_csv = download_dir / "all_stations_combined.csv"
                with open(combined_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Station_ID'] + headers)
                    writer.writerows(all_rows_data)
                
                combined_json = download_dir / "all_stations_combined.json"
                combined_json_data = []
                for row_data in all_rows_data:
                    row_dict = {"Station_ID": row_data[0]}
                    row_dict.update({headers[i]: row_data[i+1] if i < len(row_data)-1 else '' for i in range(len(headers))})
                    combined_json_data.append(row_dict)
                
                with open(combined_json, 'w', encoding='utf-8') as f:
                    json.dump(combined_json_data, f, indent=2, ensure_ascii=False)
            
            # Final summary
            self.log_progress("\n" + "="*70)
            self.log_progress("DOWNLOAD COMPLETE")
            self.log_progress("="*70)
            self.log_progress(f"Successful: {stats['successful']}/{stats['total']}")
            self.log_progress(f"Failed: {stats['failed']}/{stats['total']}")
            self.log_progress(f"Total rows: {stats['total_rows']}")
            self.log_progress(f"Output: {download_dir}")
            self.log_progress("="*70)
            
        except Exception as e:
            self.log_progress(f"\nError: {str(e)}")
        finally:
            self.download_btn.config(state=tk.NORMAL)
            self.download_in_progress = False

def main():
    root = tk.Tk()
    app = HoribaDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
