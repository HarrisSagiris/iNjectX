import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import time
from threading import Thread
from datetime import datetime

class IPALoader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IPA Sideloader")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, padx=20, pady=20, bg='#f0f0f0')
        self.main_frame.pack(expand=True, fill='both')
        
        # Title label with custom font
        title_label = tk.Label(self.main_frame, 
                             text="IPA Sideloader",
                             font=('Helvetica', 18, 'bold'),
                             bg='#f0f0f0')
        title_label.pack(pady=(0,20))
        
        # Device info frame
        device_frame = tk.LabelFrame(self.main_frame, text="Device Info", padx=10, pady=10, bg='#f0f0f0')
        device_frame.pack(fill='x', pady=(0,15))
        
        # Status label with better formatting
        self.status_label = tk.Label(device_frame, 
                                   text="Status: Waiting for iPhone...",
                                   wraplength=550,
                                   font=('Helvetica', 10),
                                   bg='#f0f0f0')
        self.status_label.pack(pady=5)
        
        # Device details label
        self.device_details = tk.Label(device_frame,
                                     text="No device connected",
                                     wraplength=550,
                                     font=('Helvetica', 10),
                                     bg='#f0f0f0')
        self.device_details.pack(pady=5)
        
        # File selection frame
        file_frame = tk.LabelFrame(self.main_frame, text="IPA File", padx=10, pady=10, bg='#f0f0f0')
        file_frame.pack(fill='x', pady=(0,15))
        
        # Select IPA button with modern styling
        self.select_btn = ttk.Button(file_frame, text="Select IPA File", command=self.select_ipa)
        self.select_btn.pack(pady=5)
        
        # Selected file label
        self.file_label = tk.Label(file_frame,
                                 text="No file selected",
                                 wraplength=550,
                                 font=('Helvetica', 10),
                                 bg='#f0f0f0')
        self.file_label.pack(pady=5)
        
        # Console frame
        console_frame = tk.LabelFrame(self.main_frame, text="Console", padx=10, pady=10, bg='#f0f0f0')
        console_frame.pack(fill='both', expand=True, pady=(0,15))
        
        # Console text widget
        self.console = tk.Text(console_frame, height=8, width=50, font=('Courier', 9))
        self.console.pack(fill='both', expand=True)
        
        # Scrollbar for console
        scrollbar = ttk.Scrollbar(console_frame, orient='vertical', command=self.console.yview)
        scrollbar.pack(side='right', fill='y')
        self.console.configure(yscrollcommand=scrollbar.set)
        
        # Control frame
        control_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        control_frame.pack(fill='x')
        
        # Start/Stop button with modern styling
        self.running = False
        self.toggle_btn = ttk.Button(control_frame,
                                   text="Start Sideloading",
                                   command=self.toggle_sideload)
        self.toggle_btn.pack(pady=10)
        
        self.ipa_path = None
        self.sideload_thread = None
        
        # Start device detection thread
        Thread(target=self.check_device_connection, daemon=True).start()
        
    def log_to_console(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert('end', f"[{timestamp}] {message}\n")
        self.console.see('end')
        
    def select_ipa(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("IPA files", "*.ipa")]
        )
        if filepath:
            self.ipa_path = filepath
            filename = os.path.basename(filepath)
            self.file_label.config(text=f"Selected: {filename}")
            self.log_to_console(f"Selected IPA file: {filename}")
            
    def check_device_connection(self):
        while True:
            try:
                result = subprocess.run(['idevice_id', '--list'], capture_output=True, text=True)
                if result.stdout.strip():
                    udid = result.stdout.strip().split('\n')[0]
                    
                    # Get device info
                    info = subprocess.run(['ideviceinfo', '-u', udid], capture_output=True, text=True)
                    info_dict = dict(line.split(': ') for line in info.stdout.split('\n') if ': ' in line)
                    
                    device_name = info_dict.get('DeviceName', 'Unknown Device')
                    ios_version = info_dict.get('ProductVersion', 'Unknown iOS')
                    
                    self.status_label.config(text="Status: iPhone connected")
                    self.device_details.config(text=f"Device: {device_name}\niOS Version: {ios_version}\nUDID: {udid[:8]}...")
                    
                else:
                    self.status_label.config(text="Status: No iPhone detected")
                    self.device_details.config(text="No device connected")
                    
            except Exception as e:
                self.status_label.config(text=f"Status: Error checking device connection")
                self.log_to_console(f"Connection error: {str(e)}")
            time.sleep(2)
            
    def sideload_process(self):
        while self.running:
            try:
                if not self.ipa_path:
                    self.status_label.config(text="Status: No IPA file selected")
                    continue

                device_check = subprocess.run(['idevice_id', '--list'], capture_output=True, text=True)
                if not device_check.stdout.strip():
                    self.status_label.config(text="Status: No device connected")
                    self.log_to_console("Waiting for device connection...")
                    time.sleep(5)
                    continue

                udid = device_check.stdout.strip().split('\n')[0]
                
                self.status_label.config(text="Status: Starting installation...")
                self.log_to_console("Beginning sideload process...")
                
                if not os.path.exists(self.ipa_path):
                    raise FileNotFoundError("IPA file not found")
                
                result = subprocess.run([
                    'ideviceinstaller',
                    '-u', udid,
                    '-i', self.ipa_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.status_label.config(text="Status: Sideload successful")
                    self.log_to_console("Sideload completed successfully!")
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    self.status_label.config(text=f"Status: Sideload failed - {error_msg}")
                    self.log_to_console(f"Sideload failed: {error_msg}")
                    
                time.sleep(5)
                
            except FileNotFoundError as e:
                self.status_label.config(text=f"Status: Error - {str(e)}")
                self.log_to_console(f"Error: {str(e)}")
                time.sleep(5)
            except Exception as e:
                self.status_label.config(text=f"Status: Error - {str(e)}")
                self.log_to_console(f"Error: {str(e)}")
                time.sleep(5)
                
    def toggle_sideload(self):
        if not self.running:
            if not self.ipa_path:
                messagebox.showerror("Error", "Please select an IPA file first")
                return
                
            self.running = True
            self.toggle_btn.config(text="Stop Sideloading")
            self.log_to_console("Starting sideload process...")
            self.sideload_thread = Thread(target=self.sideload_process, daemon=True)
            self.sideload_thread.start()
        else:
            self.running = False
            self.toggle_btn.config(text="Start Sideloading")
            self.log_to_console("Sideload process stopped")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IPALoader()
    app.run()
