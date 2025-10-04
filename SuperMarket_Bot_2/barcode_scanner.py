"""
Barcode Scanning and QR Code Support
"""
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from pyzbar import pyzbar
import threading
import time
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class BarcodeScanner:
    """Barcode and QR code scanner using camera"""
    
    def __init__(self, parent, on_barcode_scanned):
        self.parent = parent
        self.on_barcode_scanned = on_barcode_scanned
        self.camera = None
        self.scanning = False
        self.scan_thread = None
        
        # Barcode database (in real app, this would be in database)
        self.barcode_database = {
            "123456789012": {"name": "Coca Cola 500ml", "price": 2.50, "category": "Cold Drinks"},
            "234567890123": {"name": "Sprite 500ml", "price": 2.50, "category": "Cold Drinks"},
            "345678901234": {"name": "Rice 1kg", "price": 3.00, "category": "Grocery"},
            "456789012345": {"name": "Wheat Flour 1kg", "price": 2.00, "category": "Grocery"},
            "567890123456": {"name": "Hand Sanitizer 100ml", "price": 4.50, "category": "Medical"},
            "678901234567": {"name": "Face Mask (Pack of 10)", "price": 5.00, "category": "Medical"},
            "789012345678": {"name": "Mineral Water 1L", "price": 1.50, "category": "Cold Drinks"},
            "890123456789": {"name": "Cooking Oil 1L", "price": 4.00, "category": "Grocery"},
            "901234567890": {"name": "Thermal Gun", "price": 25.00, "category": "Medical"},
            "012345678901": {"name": "Maggi Noodles", "price": 1.50, "category": "Grocery"},
        }
    
    def create_scanner_window(self):
        """Create the barcode scanner window"""
        self.scanner_window = tk.Toplevel(self.parent)
        self.scanner_window.title("Barcode Scanner")
        self.scanner_window.geometry("800x600")
        self.scanner_window.configure(bg='#f0f0f0')
        
        # Title
        title_label = tk.Label(self.scanner_window, text="📱 Barcode & QR Code Scanner", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Camera frame
        self.camera_frame = tk.Frame(self.scanner_window, bg='black', width=640, height=480)
        self.camera_frame.pack(pady=10)
        self.camera_frame.pack_propagate(False)
        
        # Camera label
        self.camera_label = tk.Label(self.camera_frame, text="Initializing Camera...", 
                                    fg='white', bg='black', font=('Arial', 14))
        self.camera_label.pack(expand=True)
        
        # Controls frame
        controls_frame = tk.Frame(self.scanner_window, bg='#f0f0f0')
        controls_frame.pack(pady=10)
        
        # Start/Stop buttons
        self.start_button = tk.Button(controls_frame, text="Start Scanning", 
                                     command=self.start_scanning, bg='#4CAF50', fg='white',
                                     font=('Arial', 12, 'bold'), padx=20, pady=5)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(controls_frame, text="Stop Scanning", 
                                    command=self.stop_scanning, bg='#f44336', fg='white',
                                    font=('Arial', 12, 'bold'), padx=20, pady=5, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # Manual entry
        manual_frame = tk.Frame(self.scanner_window, bg='#f0f0f0')
        manual_frame.pack(pady=10)
        
        tk.Label(manual_frame, text="Manual Entry:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(side='left')
        self.manual_entry = tk.Entry(manual_frame, font=('Arial', 12), width=20)
        self.manual_entry.pack(side='left', padx=5)
        self.manual_entry.bind('<Return>', self.manual_scan)
        
        tk.Button(manual_frame, text="Add Product", command=self.manual_scan, 
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        # Status label
        self.status_label = tk.Label(self.scanner_window, text="Ready to scan", 
                                    font=('Arial', 12), bg='#f0f0f0', fg='#666')
        self.status_label.pack(pady=5)
        
        # Recent scans
        self.create_recent_scans_frame()
        
        # Close button
        tk.Button(self.scanner_window, text="Close", command=self.close_scanner, 
                 bg='#666', fg='white', font=('Arial', 12, 'bold'), padx=20, pady=5).pack(pady=10)
    
    def create_recent_scans_frame(self):
        """Create frame for recent scans"""
        recent_frame = tk.LabelFrame(self.scanner_window, text="Recent Scans", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        recent_frame.pack(fill='x', padx=10, pady=5)
        
        # Recent scans listbox
        self.recent_scans_listbox = tk.Listbox(recent_frame, height=4, font=('Arial', 10))
        self.recent_scans_listbox.pack(fill='x', padx=5, pady=5)
        
        # Clear button
        tk.Button(recent_frame, text="Clear History", command=self.clear_recent_scans,
                 bg='#FF9800', fg='white', font=('Arial', 10)).pack(pady=5)
    
    def start_scanning(self):
        """Start the barcode scanning process"""
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Could not access camera. Please check your camera connection.")
                return
            
            self.scanning = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text="Scanning... Point camera at barcode/QR code", fg='#4CAF50')
            
            # Start scanning thread
            self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.scan_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting scanner: {e}")
            messagebox.showerror("Error", f"Failed to start scanner: {e}")
    
    def stop_scanning(self):
        """Stop the barcode scanning process"""
        self.scanning = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Scanning stopped", fg='#666')
        
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def _scan_loop(self):
        """Main scanning loop running in separate thread"""
        while self.scanning and self.camera:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Resize frame for display
                height, width = frame.shape[:2]
                max_width = 640
                if width > max_width:
                    scale = max_width / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Convert to RGB for tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect barcodes
                barcodes = pyzbar.decode(frame)
                
                # Draw bounding boxes around detected barcodes
                for barcode in barcodes:
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Extract barcode data
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    # Process the barcode
                    self._process_barcode(barcode_data, barcode_type)
                
                # Update camera display
                self._update_camera_display(frame_rgb)
                
                time.sleep(0.1)  # Small delay to prevent high CPU usage
                
            except Exception as e:
                logger.error(f"Error in scan loop: {e}")
                break
    
    def _update_camera_display(self, frame):
        """Update the camera display in the GUI"""
        try:
            # Convert frame to PhotoImage
            height, width = frame.shape[:2]
            image = tk.PhotoImage(data=cv2.imencode('.ppm', frame)[1].tobytes())
            
            # Update camera label
            self.camera_label.config(image=image, text="")
            self.camera_label.image = image  # Keep a reference
            
        except Exception as e:
            logger.error(f"Error updating camera display: {e}")
    
    def _process_barcode(self, barcode_data: str, barcode_type: str):
        """Process detected barcode"""
        try:
            # Check if barcode exists in database
            if barcode_data in self.barcode_database:
                product_info = self.barcode_database[barcode_data]
                
                # Update status
                self.status_label.config(text=f"Found: {product_info['name']}", fg='#4CAF50')
                
                # Add to recent scans
                self._add_to_recent_scans(barcode_data, product_info)
                
                # Call the callback function
                self.on_barcode_scanned(barcode_data, product_info)
                
                # Brief pause to prevent duplicate scans
                time.sleep(1)
            else:
                self.status_label.config(text=f"Unknown barcode: {barcode_data}", fg='#FF9800')
                
        except Exception as e:
            logger.error(f"Error processing barcode: {e}")
    
    def _add_to_recent_scans(self, barcode: str, product_info: Dict):
        """Add scan to recent scans list"""
        try:
            scan_text = f"{product_info['name']} - ${product_info['price']} ({barcode})"
            self.recent_scans_listbox.insert(0, scan_text)
            
            # Keep only last 10 scans
            if self.recent_scans_listbox.size() > 10:
                self.recent_scans_listbox.delete(10, tk.END)
                
        except Exception as e:
            logger.error(f"Error adding to recent scans: {e}")
    
    def manual_scan(self, event=None):
        """Handle manual barcode entry"""
        try:
            barcode = self.manual_entry.get().strip()
            if not barcode:
                return
            
            if barcode in self.barcode_database:
                product_info = self.barcode_database[barcode]
                self._add_to_recent_scans(barcode, product_info)
                self.on_barcode_scanned(barcode, product_info)
                self.manual_entry.delete(0, tk.END)
                self.status_label.config(text=f"Added: {product_info['name']}", fg='#4CAF50')
            else:
                self.status_label.config(text=f"Unknown barcode: {barcode}", fg='#FF9800')
                
        except Exception as e:
            logger.error(f"Error in manual scan: {e}")
    
    def clear_recent_scans(self):
        """Clear recent scans history"""
        self.recent_scans_listbox.delete(0, tk.END)
    
    def close_scanner(self):
        """Close the scanner window"""
        self.stop_scanning()
        self.scanner_window.destroy()
    
    def add_barcode_to_database(self, barcode: str, name: str, price: float, category: str):
        """Add new barcode to database"""
        self.barcode_database[barcode] = {
            "name": name,
            "price": price,
            "category": category
        }
        logger.info(f"Added barcode {barcode} for {name}")
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Get product information by barcode"""
        return self.barcode_database.get(barcode)
    
    def get_all_barcodes(self) -> Dict[str, Dict]:
        """Get all barcodes in database"""
        return self.barcode_database.copy()
