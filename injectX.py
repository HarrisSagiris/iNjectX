import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import time
from threading import Thread

class IPALoader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IPA Sideloader")
        self.root.geometry("400x300")
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill='both')
        
        # Status label
        self.status_label = tk.Label(self.main_frame, text="Status: Waiting for iPhone...", wraplength=350)
        self.status_label.pack(pady=10)
        
        # Select IPA button
        self.select_btn = tk.Button(self.main_frame, text="Select IPA File", command=self.select_ipa)
        self.select_btn.pack(pady=10)
        
        # Selected file label
        self.file_label = tk.Label(self.main_frame, text="No file selected", wraplength=350)
        self.file_label.pack(pady=10)
        
        # Start/Stop button
        self.running = False
        self.toggle_btn = tk.Button(self.main_frame, text="Start Sideloading", command=self.toggle_sideload)
        self.toggle_btn.pack(pady=10)
        
        self.ipa_path = None
        self.sideload_thread = None
        
        # Start device detection thread
        Thread(target=self.check_device_connection, daemon=True).start()
        
    def select_ipa(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("IPA files", "*.ipa")]
        )
        if filepath:
            self.ipa_path = filepath
            self.file_label.config(text=f"Selected: {os.path.basename(filepath)}")
            
    def check_device_connection(self):
        while True:
            try:
                # Using libimobiledevice's idevice_id to check connection
                result = subprocess.run(['idevice_id', '--list'], capture_output=True, text=True)
                if result.stdout.strip():
                    self.status_label.config(text="Status: iPhone connected")
                else:
                    self.status_label.config(text="Status: No iPhone detected")
            except Exception as e:
                self.status_label.config(text=f"Status: Error checking device connection - {str(e)}")
            time.sleep(2)
            
    def sideload_process(self):
        while self.running:
            try:
                if not self.ipa_path:
                    self.status_label.config(text="Status: No IPA file selected")
                    continue

                # First verify device is connected
                device_check = subprocess.run(['idevice_id', '--list'], capture_output=True, text=True)
                if not device_check.stdout.strip():
                    self.status_label.config(text="Status: No device connected")
                    time.sleep(5)
                    continue

                # Get device UDID
                udid = device_check.stdout.strip().split('\n')[0]
                
                # Using libimobiledevice tools for installation
                self.status_label.config(text="Status: Starting installation...")
                
                # Verify the IPA file exists
                if not os.path.exists(self.ipa_path):
                    raise FileNotFoundError("IPA file not found")
                
                # Install using ideviceinstaller (part of libimobiledevice)
                result = subprocess.run([
                    'ideviceinstaller',
                    '-u', udid,
                    '-i', self.ipa_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.status_label.config(text="Status: Sideload successful")
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    self.status_label.config(text=f"Status: Sideload failed - {error_msg}")
                    
                time.sleep(5)  # Wait before next attempt
                
            except FileNotFoundError as e:
                self.status_label.config(text=f"Status: Error - {str(e)}")
                time.sleep(5)
            except Exception as e:
                self.status_label.config(text=f"Status: Error - {str(e)}")
                time.sleep(5)
                
    def toggle_sideload(self):
        if not self.running:
            if not self.ipa_path:
                messagebox.showerror("Error", "Please select an IPA file first")
                return
                
            self.running = True
            self.toggle_btn.config(text="Stop Sideloading")
            self.sideload_thread = Thread(target=self.sideload_process, daemon=True)
            self.sideload_thread.start()
        else:
            self.running = False
            self.toggle_btn.config(text="Start Sideloading")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IPALoader()
    app.run()
