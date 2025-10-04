"""
Enhanced GUI with AI Features, Dashboard, and Barcode Scanning
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import datetime
import threading
import webbrowser
import json
import os
import subprocess
import tempfile
import platform
import shutil

from models import Customer, Bill, Product
from database import DatabaseManager
from billing_service import BillingService
from inventory_service import InventoryService
from dashboard import RealTimeDashboard
from barcode_scanner import BarcodeScanner
# AI features have been removed for a lean, professional UI.

logger = logging.getLogger(__name__)


class EnhancedSupermarketGUI:
    """Enhanced GUI with AI features, real-time dashboard, and barcode scanning"""
    
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager,
                 billing_service: BillingService, inventory_service: InventoryService):
        self.root = root
        self.db_manager = db_manager
        self.billing_service = billing_service
        self.inventory_service = inventory_service

        # Initialize barcode scanner (if used)
        self.barcode_scanner = None

        # Window configuration
        self.root.title("Supermarket Management System v2.0")
        self.root.geometry("1400x900")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Build UI and load initial data
        self._create_widgets()
        self._load_initial_data()
    
    def _create_widgets(self):
        """Creates the main GUI widgets including tabs."""
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs (focused, professional UI)
        self._create_dashboard_tab()
        self._create_billing_tab()
        self._create_inventory_tab()
        self._create_reports_tab()
        self._create_settings_tab()
    
    def _create_dashboard_tab(self):
        """Create the real-time dashboard tab"""
        self.dashboard_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.dashboard_frame, text="Dashboard")

        # Initialize dashboard
        self.dashboard = RealTimeDashboard(
            self.dashboard_frame, self.billing_service, self.inventory_service
        )
    
    def _create_billing_tab(self):
        """Create the enhanced billing tab"""
        self.billing_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.billing_frame, text="Billing")

        # Top controls
        controls_frame = ttk.Frame(self.billing_frame)
        controls_frame.pack(fill='x', pady=(0, 10))

        # Barcode scanner button
        ttk.Button(controls_frame, text="Barcode Scanner",
                  command=self._open_barcode_scanner).pack(side='left', padx=5)

        # Quick add product
        ttk.Label(controls_frame, text="Quick Add:").pack(side='left', padx=(20, 5))
        self.quick_add_var = tk.StringVar()
        quick_add_entry = ttk.Entry(controls_frame, textvariable=self.quick_add_var, width=20)
        quick_add_entry.pack(side='left', padx=5)
        quick_add_entry.bind('<Return>', self._quick_add_product)

        ttk.Button(controls_frame, text="Add", command=self._quick_add_product).pack(side='left', padx=5)
        
        # Customer Details
        customer_frame = ttk.LabelFrame(self.billing_frame, text="Customer Details", padding="10")
        customer_frame.pack(fill='x', pady=5)
        
        ttk.Label(customer_frame, text="Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.customer_name_var = tk.StringVar()
        ttk.Entry(customer_frame, textvariable=self.customer_name_var, width=30).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(customer_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.customer_phone_var = tk.StringVar()
        ttk.Entry(customer_frame, textvariable=self.customer_phone_var, width=30).grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(customer_frame, text="Email:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.customer_email_var = tk.StringVar()
        ttk.Entry(customer_frame, textvariable=self.customer_email_var, width=30).grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Main content area
        content_frame = ttk.Frame(self.billing_frame)
        content_frame.pack(fill='both', expand=True, pady=5)
        
        # Product selection
        products_frame = ttk.LabelFrame(content_frame, text="Products", padding="10")
        products_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Product search
        search_frame = ttk.Frame(products_frame)
        search_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace_add("write", self._filter_products)
        ttk.Entry(search_frame, textvariable=self.product_search_var, width=25).pack(side='left', padx=5)
        
        # Product tree
        self.product_tree = ttk.Treeview(products_frame, columns=("Name", "Price", "Stock", "Category"), show="headings")
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Price", text="Price")
        self.product_tree.heading("Stock", text="Stock")
        self.product_tree.heading("Category", text="Category")
        self.product_tree.pack(fill='both', expand=True)
        self.product_tree.bind("<Double-1>", self._add_product_to_cart)
        
        # Cart
        cart_frame = ttk.LabelFrame(content_frame, text="Shopping Cart", padding="10")
        cart_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.cart_tree = ttk.Treeview(cart_frame, columns=("Product", "Qty", "Price", "Total"), show="headings")
        self.cart_tree.heading("Product", text="Product")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Price", text="Price")
        self.cart_tree.heading("Total", text="Total")
        self.cart_tree.pack(fill='both', expand=True)
        
        # Cart controls
        cart_controls = ttk.Frame(cart_frame)
        cart_controls.pack(fill='x', pady=5)
        
        ttk.Button(cart_controls, text="Remove", command=self._remove_from_cart).pack(side='left', padx=5)
        ttk.Button(cart_controls, text="Update Qty", command=self._update_cart_quantity).pack(side='left', padx=5)
        ttk.Button(cart_controls, text="Clear Cart", command=self._clear_cart).pack(side='left', padx=5)
        
        # Bill summary
        summary_frame = ttk.LabelFrame(self.billing_frame, text="Bill Summary", padding="10")
        summary_frame.pack(fill='x', pady=5)
        
        summary_content = ttk.Frame(summary_frame)
        summary_content.pack(fill='x')
        
        ttk.Label(summary_content, text="Subtotal:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.subtotal_var = tk.StringVar(value="0.00")
        ttk.Label(summary_content, textvariable=self.subtotal_var, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="e")
        
        ttk.Label(summary_content, text="Tax:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.tax_var = tk.StringVar(value="0.00")
        ttk.Label(summary_content, textvariable=self.tax_var, font=("Arial", 10, "bold")).grid(row=1, column=1, padx=5, pady=2, sticky="e")
        
        ttk.Label(summary_content, text="Total:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.total_var = tk.StringVar(value="0.00")
        ttk.Label(summary_content, textvariable=self.total_var, font=("Arial", 12, "bold")).grid(row=2, column=1, padx=5, pady=2, sticky="e")
        
        # Action buttons
        action_frame = ttk.Frame(self.billing_frame)
        action_frame.pack(fill='x', pady=5)
        
        ttk.Button(action_frame, text="Generate Bill", command=self._generate_bill).pack(side='left', padx=5)
        ttk.Button(action_frame, text="New Bill", command=self._new_bill).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Print Bill", command=self._print_bill).pack(side='left', padx=5)
        
        # Initialize cart
        self.cart_items = {}
        self._update_bill_summary()
    
    def _create_inventory_tab(self):
        """Create the inventory management tab"""
        self.inventory_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.inventory_frame, text="Inventory")

        # Inventory tree
        self.inventory_tree = ttk.Treeview(self.inventory_frame, 
                                         columns=("ID", "Name", "Category", "Price", "Stock", "Min Stock"), 
                                         show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Stock", text="Stock")
        self.inventory_tree.heading("Min Stock", text="Min Stock")
        self.inventory_tree.pack(fill='both', expand=True)
        
        # Inventory controls
        controls_frame = ttk.Frame(self.inventory_frame)
        controls_frame.pack(fill='x', pady=5)

        ttk.Button(controls_frame, text="Add Product", command=self._add_product).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Edit Product", command=self._edit_product).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Delete Product", command=self._delete_product).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Check Low Stock", command=self._check_low_stock).pack(side='left', padx=5)
    
    # AI-related tabs and methods removed to keep the application focused and lightweight.
    
    def _create_reports_tab(self):
        """Create the reports tab"""
        self.reports_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.reports_frame, text="Reports")

        # Report selection
        report_frame = ttk.LabelFrame(self.reports_frame, text="Select Report", padding="10")
        report_frame.pack(fill='x', pady=5)

        self.report_type_var = tk.StringVar()
        report_types = ["Sales Summary", "Inventory Report", "Customer Analysis"]
        ttk.OptionMenu(report_frame, self.report_type_var, report_types[0], *report_types).pack(side='left', padx=5)

        ttk.Button(report_frame, text="Generate Report", command=self._generate_report).pack(side='left', padx=5)
        ttk.Button(report_frame, text="Export Report", command=self._export_report).pack(side='left', padx=5)

        # Report display
        self.report_display = scrolledtext.ScrolledText(self.reports_frame, wrap=tk.WORD, height=20, width=100)
        self.report_display.pack(fill='both', expand=True, pady=5)
    
    def _create_settings_tab(self):
        """Create the settings tab"""
        self.settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.settings_frame, text="Settings")

        # Email settings
        email_frame = ttk.LabelFrame(self.settings_frame, text="Email Configuration", padding="10")
        email_frame.pack(fill='x', pady=5)

        ttk.Label(email_frame, text="Sender Email:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.sender_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.sender_email_var, width=40).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(email_frame, text="Password:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.sender_password_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.sender_password_var, show="*", width=40).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(email_frame, text="Receiver Email:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.receiver_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.receiver_email_var, width=40).grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Button(email_frame, text="Save Email Settings", command=self._save_email_settings).grid(row=3, column=0, columnspan=2, pady=10)

        # API settings
        api_frame = ttk.LabelFrame(self.settings_frame, text="API Configuration", padding="10")
        api_frame.pack(fill='x', pady=5)

        ttk.Button(api_frame, text="Start API Server", command=self._start_api_server).pack(side='left', padx=5)
        ttk.Button(api_frame, text="Open API Docs", command=self._open_api_docs).pack(side='left', padx=5)

        # System info
        info_frame = ttk.LabelFrame(self.settings_frame, text="System Information", padding="10")
        info_frame.pack(fill='x', pady=5)
        
        self.system_info_text = scrolledtext.ScrolledText(info_frame, height=8, width=80)
        self.system_info_text.pack(fill='both', expand=True)
        
        self._load_system_info()
    
    def _load_initial_data(self):
        """Load initial data and populate dropdowns"""
        try:
            # Load products for dropdowns
            products = self.db_manager.get_all_products()
            product_names = [p.name for p in products]
            
            # Update forecast product combobox
            if hasattr(self, 'forecast_product_var'):
                # This will be set when the AI tab is created
                pass
            
            # Load products to trees
            self._load_products_to_tree()
            self._load_inventory_to_tree()
            
        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
    
    def _load_products_to_tree(self):
        """Load products into the product tree"""
        try:
            # Clear existing items
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)
            
            products = self.db_manager.get_all_products()
            for product in products:
                self.product_tree.insert("", "end", iid=product.id, values=(
                    product.name, f"${product.price:.2f}", product.quantity, product.category
                ))
        except Exception as e:
            logger.error(f"Error loading products to tree: {e}")
    
    def _load_inventory_to_tree(self):
        """Load products into the inventory tree"""
        try:
            # Clear existing items
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            
            products = self.db_manager.get_all_products()
            for product in products:
                self.inventory_tree.insert("", "end", iid=product.id, values=(
                    product.id, product.name, product.category, f"${product.price:.2f}",
                    product.quantity, product.min_stock_level
                ))
        except Exception as e:
            logger.error(f"Error loading inventory to tree: {e}")
    
    def _filter_products(self, *args):
        """Filter products based on search term"""
        try:
            search_term = self.product_search_var.get().lower()
            
            # Clear existing items
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)
            
            products = self.db_manager.get_all_products()
            filtered_products = [p for p in products if search_term in p.name.lower() or search_term in p.category.lower()]
            
            for product in filtered_products:
                self.product_tree.insert("", "end", iid=product.id, values=(
                    product.name, f"${product.price:.2f}", product.quantity, product.category
                ))
        except Exception as e:
            logger.error(f"Error filtering products: {e}")
    
    def _add_product_to_cart(self, event):
        """Add selected product to cart"""
        try:
            selected_item = self.product_tree.focus()
            if not selected_item:
                return

            # selected_item is the item's iid
            product_id = selected_item
            product = self.db_manager.get_product_by_id(product_id)
            
            if not product:
                messagebox.showerror("Error", "Product not found")
                return
            
            if product.quantity <= 0:
                messagebox.showwarning(
                    "Warning", f"{product.name} is out of stock!"
                )
                return
            
            # Prompt for quantity; max allowed is current stock
            quantity = self._get_quantity_dialog(
                product.name, product.quantity
            )
            if quantity is None:
                return
            
            # Add to cart
            if product_id in self.cart_items:
                self.cart_items[product_id]['quantity'] += quantity
            else:
                self.cart_items[product_id] = {
                    'product': product,
                    'quantity': quantity
                }
            
            self._update_cart_display()
            self._update_bill_summary()
            
        except Exception as e:
            logger.error(f"Error adding product to cart: {e}")
            messagebox.showerror("Error", f"Failed to add product: {e}")
    
    def _get_quantity_dialog(self, product_name, max_quantity):
        """Get quantity from user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Quantity")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(
            dialog, text=f"Enter quantity for {product_name}:"
        ).pack(padx=10, pady=10)
        
        qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(dialog, textvariable=qty_var, width=10)
        qty_entry.pack(padx=10, pady=5)
        qty_entry.focus_set()
        
        result = [None]
        
        def confirm():
            try:
                quantity = int(qty_var.get())
                if 1 <= quantity <= max_quantity:
                    result[0] = quantity
                    dialog.destroy()
                else:
                    messagebox.showerror(
                        "Error",
                        f"Quantity must be between 1 and {max_quantity}"
                    )
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        ttk.Button(dialog, text="Add", command=confirm).pack(padx=10, pady=10)
        qty_entry.bind('<Return>', lambda e: confirm())
        
        self.root.wait_window(dialog)
        return result[0]
    
    def _update_cart_display(self):
        """Update the cart display"""
        try:
            # Clear existing items
            for item in self.cart_tree.get_children():
                self.cart_tree.delete(item)
            
            for product_id, item_data in self.cart_items.items():
                product = item_data['product']
                quantity = item_data['quantity']
                total_price = product.price * quantity
                
                self.cart_tree.insert(
                    "",
                    "end",
                    iid=product_id,
                    values=(
                        product.name,
                        quantity,
                        f"${product.price:.2f}",
                        f"${total_price:.2f}",
                    ),
                )
        except Exception as e:
            logger.error(f"Error updating cart display: {e}")
    
    def _update_bill_summary(self):
        """Update the bill summary"""
        try:
            subtotal = 0.0
            total_tax = 0.0
            
            for product_id, item_data in self.cart_items.items():
                product = item_data['product']
                quantity = item_data['quantity']
                item_price = product.price * quantity
                item_tax = item_price * product.tax_rate
                
                subtotal += item_price
                total_tax += item_tax
            
            total = subtotal + total_tax
            
            self.subtotal_var.set(f"${subtotal:.2f}")
            self.tax_var.set(f"${total_tax:.2f}")
            self.total_var.set(f"${total:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating bill summary: {e}")
    
    def _remove_from_cart(self):
        """Remove selected item from cart"""
        try:
            selected_item = self.cart_tree.focus()
            if not selected_item:
                messagebox.showwarning(
                    "Warning", "Please select an item to remove"
                )
                return
            
            # selected_item is iid
            product_id = selected_item
            if product_id in self.cart_items:
                del self.cart_items[product_id]
                self._update_cart_display()
                self._update_bill_summary()
        except Exception as e:
            logger.error(f"Error removing from cart: {e}")
    
    def _update_cart_quantity(self):
        """Update quantity of selected cart item"""
        try:
            selected_item = self.cart_tree.focus()
            if not selected_item:
                messagebox.showwarning(
                    "Warning", "Please select an item to update"
                )
                return
            
            # selected_item is iid
            product_id = selected_item
            if product_id not in self.cart_items:
                return
            
            item_data = self.cart_items[product_id]
            product = item_data['product']

            new_quantity = self._get_quantity_dialog(
                product.name, product.quantity
            )
            if new_quantity is not None:
                item_data['quantity'] = new_quantity
                self._update_cart_display()
                self._update_bill_summary()
        except Exception as e:
            logger.error(f"Error updating cart quantity: {e}")
    
    def _clear_cart(self):
        """Clear all items from cart"""
        if messagebox.askyesno(
            "Clear Cart", "Are you sure you want to clear the cart?"
        ):
            self.cart_items = {}
            self._update_cart_display()
            self._update_bill_summary()
    
    def _generate_bill(self):
        """Generate a new bill"""
        try:
            customer_name = self.customer_name_var.get().strip()
            customer_phone = self.customer_phone_var.get().strip()
            customer_email = self.customer_email_var.get().strip()
            
            if not customer_name or not customer_phone:
                messagebox.showerror(
                    "Error", "Customer name and phone are required"
                )
                return
            
            if not self.cart_items:
                messagebox.showerror("Error", "Cart is empty")
                return
            
            # Prepare customer info
            customer_info = {
                "name": customer_name,
                "phone": customer_phone,
                "email": customer_email
            }
            
            # Prepare items
            items_purchased = {
                pid: item_data['quantity']
                for pid, item_data in self.cart_items.items()
            }
            
            # Create bill
            bill = self.billing_service.create_bill(
                customer_info, items_purchased
            )
            
            if bill:
                # Keep reference to last bill so user can print it later
                self._last_bill = bill
                messagebox.showinfo(
                    "Success",
                    "Bill {id} created successfully!\nTotal: ${amt:.2f}".format(
                        id=bill.id,
                        amt=bill.total_amount,
                    ),
                )
                self._new_bill()
            else:
                messagebox.showerror("Error", "Failed to create bill")
                
        except Exception as e:
            logger.error(f"Error generating bill: {e}")
            messagebox.showerror("Error", f"Failed to generate bill: {e}")
    
    def _new_bill(self):
        """Start a new bill"""
        self.customer_name_var.set("")
        self.customer_phone_var.set("")
        self.customer_email_var.set("")
        self.cart_items = {}
        self._update_cart_display()
        self._update_bill_summary()
        # Refresh product listing and inventory listing so quantities reflect recent bill
        try:
            self._load_products_to_tree()
        except Exception:
            pass
        try:
            self._load_inventory_to_tree()
        except Exception:
            pass

        # Ask dashboard to refresh its metrics immediately
        try:
            if hasattr(self, 'dashboard') and self.dashboard:
                try:
                    self.dashboard.update_dashboard()
                except Exception:
                    # dashboard may schedule its own updates; ignore if it fails here
                    pass
        except Exception:
            pass
    
    def _print_bill(self):
        """Print the last created bill or preview the current cart as a receipt.

        On macOS this will send the receipt to the system printer via `lpr` if
        the user chooses Print. The user can also save the receipt to a file.
        """
        try:
            bill = getattr(self, '_last_bill', None)

            # If no saved bill, but cart has items, create a transient bill preview
            if not bill and self.cart_items:
                # Build temporary bill-like object using the Bill dataclass
                from models import Bill, BillItem, Customer

                customer = Customer(
                    name=self.customer_name_var.get() or 'Walk-in',
                    phone=self.customer_phone_var.get() or '',
                    email=self.customer_email_var.get() or None,
                )

                items = []
                subtotal = 0.0
                tax_total = 0.0
                for pid, item_data in self.cart_items.items():
                    prod = item_data['product']
                    qty = item_data['quantity']
                    item_total = prod.price * qty
                    tax_amt = item_total * getattr(prod, 'tax_rate', 0.0)
                    items.append(
                        BillItem(
                            product_id=prod.id,
                            product_name=prod.name,
                            quantity=qty,
                            unit_price=prod.price,
                            total_price=item_total,
                            tax_amount=tax_amt,
                        )
                    )
                    subtotal += item_total
                    tax_total += tax_amt

                bill = Bill(
                    id='PREVIEW',
                    customer=customer,
                    items=items,
                    subtotal=subtotal,
                    tax_amount=tax_total,
                    total_amount=subtotal + tax_total,
                    created_at=datetime.now(),
                    status='preview',
                )

            if not bill:
                messagebox.showinfo("Print Bill", "No bill available to print.")
                return

            # Generate receipt text
            receipt = bill.to_receipt_text()

            # Preview dialog
            dlg = tk.Toplevel(self.root)
            dlg.title(f"Receipt - {bill.id}")
            dlg.geometry("600x700")
            txt = scrolledtext.ScrolledText(dlg, wrap=tk.WORD)
            txt.pack(fill='both', expand=True, padx=10, pady=10)
            txt.insert('1.0', receipt)
            txt.config(state='disabled')

            def do_save():
                reports_dir = os.path.join(os.getcwd(), 'reports')
                os.makedirs(reports_dir, exist_ok=True)
                fname = os.path.join(reports_dir, f"receipt_{bill.id}_{int(datetime.now().timestamp())}.txt")
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(receipt)
                messagebox.showinfo("Saved", f"Receipt saved to {fname}")

            def do_print():
                # Try macOS `lpr` printing first
                try:
                    # write to a temp file and send to lpr
                    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt', encoding='utf-8') as tf:
                        tf.write(receipt)
                        tfname = tf.name
                    system = platform.system()
                    if system == 'Darwin' or shutil.which('lpr'):
                        # Use lpr if available
                        subprocess.run(['lpr', tfname], check=True)
                        messagebox.showinfo('Print', 'Sent to printer')
                    else:
                        # If lpr not available, prompt user to save the file
                        messagebox.showinfo('Print', 'Printing not available on this system. Save the receipt instead.')
                except Exception as e:
                    logger.error(f"Error printing receipt: {e}")
                    messagebox.showerror('Print Error', f'Failed to print: {e}')
                finally:
                    try:
                        os.unlink(tfname)
                    except Exception:
                        pass

            btn_frame = ttk.Frame(dlg)
            btn_frame.pack(fill='x', pady=6)
            ttk.Button(btn_frame, text='Print', command=do_print).pack(side='left', padx=8)
            ttk.Button(btn_frame, text='Save', command=do_save).pack(side='left', padx=8)
            ttk.Button(btn_frame, text='Close', command=dlg.destroy).pack(side='right', padx=8)

        except Exception as e:
            logger.error(f"Error in print_bill: {e}")
            messagebox.showerror('Error', f'Failed to prepare print: {e}')
    
    def _open_barcode_scanner(self):
        """Open the barcode scanner"""
        try:
            if not self.barcode_scanner:
                self.barcode_scanner = BarcodeScanner(
                    self.root, self._on_barcode_scanned
                )
            
            self.barcode_scanner.create_scanner_window()
        except Exception as e:
            logger.error(f"Error opening barcode scanner: {e}")
            messagebox.showerror(
                "Error", f"Failed to open barcode scanner: {e}"
            )
    
    def _on_barcode_scanned(self, barcode, product_info):
        """Handle barcode scan result"""
        try:
            # Find product by name
            products = self.db_manager.get_all_products()
            product = next(
                (
                    p
                    for p in products
                    if p.name.lower() == product_info['name'].lower()
                ),
                None,
            )
            
            if product:
                # Add to cart
                if product.id in self.cart_items:
                    self.cart_items[product.id]['quantity'] += 1
                else:
                    self.cart_items[product.id] = {
                        'product': product,
                        'quantity': 1
                    }
                
                self._update_cart_display()
                self._update_bill_summary()
                messagebox.showinfo("Product Added", f"Added {product.name} to cart")
            else:
                messagebox.showwarning(
                    "Product Not Found",
                    f"Product {product_info['name']} not found in inventory",
                )
                
        except Exception as e:
            logger.error(f"Error handling barcode scan: {e}")
            messagebox.showerror("Error", f"Failed to process barcode: {e}")
    
    def _show_ai_recommendations(self):
        """Show AI recommendations for the current cart"""
        try:
            if not self.cart_items:
                messagebox.showinfo(
                    "AI Recommendations",
                    "Cart is empty. Add some products to get AI recommendations!",
                )
                return
            
            # AI features removed; show a professional placeholder
            insights = {"note": "AI features are disabled in this build."}
            
            # Show recommendations dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("🤖 AI Recommendations")
            dialog.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            
            recommendations = "🤖 AI RECOMMENDATIONS FOR YOUR CART\n"
            recommendations += "=" * 50 + "\n\n"

            # include a short revenue summary from insights (if present)
            revenue_forecast = (
                insights.get('revenue_forecast') if isinstance(insights, dict) else None
            )
            if revenue_forecast:
                recommendations += (
                    "Revenue forecast (30 days): ${val:.2f}\n\n".format(
                        val=revenue_forecast.get('predicted', 0)
                    )
                )
            
            # Add product-specific recommendations
            for product_id, item_data in self.cart_items.items():
                product = item_data['product']
                # AI disabled; show neutral recommendation info
                forecast = {'predicted_demand': 0, 'confidence': 'n/a'}
                recommendations += "{name}\n".format(name=product.name)
                recommendations += (
                    "   Predicted demand (7 days): {demand} units\n".format(
                        demand=forecast.get('predicted_demand', 0)
                    )
                )
                recommendations += (
                    "   Confidence: {conf}\n".format(
                        conf=forecast.get('confidence', 'n/a')
                    )
                )
                recommendations += "   Recommendation: "
                
                if (
                    forecast.get('predicted_demand', 0)
                    > item_data['quantity'] * 2
                ):
                    recommendations += (
                        "Consider ordering more - high demand predicted\n"
                    )
                elif (
                    forecast.get('predicted_demand', 0) < item_data['quantity']
                ):
                    recommendations += "Current quantity seems adequate\n"
                else:
                    recommendations += "Monitor demand closely\n"
                recommendations += "\n"
            
            text_widget.insert('1.0', recommendations)
            text_widget.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Error showing AI recommendations: {e}")
            messagebox.showerror(
                "Error", f"Failed to get AI recommendations: {e}"
            )
    
    def _quick_add_product(self, event=None):
        """Quick add product by name"""
        try:
            product_name = self.quick_add_var.get().strip()
            if not product_name:
                return
            
            # Find product by name
            products = self.db_manager.get_all_products()
            product = next(
                (p for p in products if p.name.lower() == product_name.lower()),
                None,
            )
            
            if product:
                if product.quantity > 0:
                    if product.id in self.cart_items:
                        self.cart_items[product.id]['quantity'] += 1
                    else:
                        self.cart_items[product.id] = {
                            'product': product,
                            'quantity': 1
                        }
                    
                    self._update_cart_display()
                    self._update_bill_summary()
                    self.quick_add_var.set("")
                    messagebox.showinfo(
                        "Added", f"Added {product.name} to cart"
                    )
                else:
                    messagebox.showwarning("Out of Stock", f"{product.name} is out of stock")
            else:
                messagebox.showwarning("Not Found", f"Product '{product_name}' not found")
                
        except Exception as e:
            logger.error(f"Error in quick add: {e}")
            messagebox.showerror("Error", f"Failed to add product: {e}")
    
    # Placeholder methods for other functionality
    def _add_product(self): pass
    def _edit_product(self): pass
    def _delete_product(self): pass
    

    def _check_low_stock(self):
        """Show low stock alerts and offer a purchase order summary"""
        try:
            alerts = self.inventory_service.get_low_stock_alerts()
            if not alerts:
                messagebox.showinfo("Low Stock Check", "No low stock items found.")
                return

            # Build a readable message
            msg = "Low Stock Items:\n\n"
            for alert in alerts:
                msg += (
                    f"{alert.product_name} (ID: {alert.product_id}) - "
                    f"Current: {alert.current_quantity}, Min: {alert.min_required}, "
                    f"Suggested Order: {alert.suggested_order_quantity}\n"
                )

            # Prevent multiple low-stock dialogs
            if getattr(self, '_low_stock_dialog', None):
                # bring existing dialog to front
                try:
                    self._low_stock_dialog.lift()
                    return
                except Exception:
                    self._low_stock_dialog = None

            # Show in a dialog with option to generate a quick purchase order file
            dlg = tk.Toplevel(self.root)
            self._low_stock_dialog = dlg
            dlg.transient(self.root)
            dlg.grab_set()
            dlg.title("Low Stock Alerts")
            txt = scrolledtext.ScrolledText(dlg, wrap=tk.WORD, width=80, height=20)
            txt.pack(fill='both', expand=True, padx=10, pady=10)
            txt.insert('1.0', msg)
            txt.config(state='disabled')

            def save_po():
                po_text = "PURCHASE ORDER\n"
                po_text += "=" * 40 + "\n"
                po_text += msg
                reports_dir = os.path.join(os.getcwd(), 'reports')
                os.makedirs(reports_dir, exist_ok=True)
                fname = os.path.join(reports_dir, f"purchase_order_{int(datetime.now().timestamp())}.txt")
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(po_text)
                messagebox.showinfo("Saved", f"Purchase order saved to {fname}")

            def on_close():
                try:
                    dlg.grab_release()
                except Exception:
                    pass
                try:
                    dlg.destroy()
                except Exception:
                    pass
                self._low_stock_dialog = None

            dlg.protocol('WM_DELETE_WINDOW', on_close)

            btn = ttk.Button(dlg, text="Save Purchase Order", command=save_po)
            btn.pack(pady=6)

        except Exception as e:
            logger.error(f"Error checking low stock: {e}")
            messagebox.showerror("Error", f"Failed to check low stock: {e}")
    def _show_reorder_suggestions(self): pass
    def _predict_demand(self): pass
    def _generate_customer_insights(self): pass
    def _generate_pricing_suggestions(self): pass
    def _detect_anomalies(self): pass
    

    def _generate_report(self):
        """Generate selected report and display it in the reports tab"""
        try:
            rtype = self.report_type_var.get() if hasattr(self, 'report_type_var') else 'Sales Summary'
            out = ""

            if rtype == 'Sales Summary':
                bills = self.billing_service.get_all_bills()
                total_sales = sum(b.total_amount for b in bills)
                total_bills = len(bills)
                out += f"Sales Summary\n\nTotal Sales: ${total_sales:.2f}\nTotal Bills: {total_bills}\n\n"
                # show last 10 bills
                out += "Recent Bills:\n"
                for b in sorted(bills, key=lambda x: x.created_at, reverse=True)[:10]:
                    out += f"{b.id} | {b.created_at.isoformat()} | ${b.total_amount:.2f}\n"

            elif rtype == 'Inventory Report':
                products = self.db_manager.get_all_products()
                inv = self.inventory_service.get_inventory_summary()
                out += "Inventory Report\n\n"
                out += f"Total Products: {inv.get('total_products')}\n"
                out += f"Low Stock Items: {inv.get('low_stock_count')}\n"
                out += f"Total Inventory Value: ${inv.get('total_inventory_value'):.2f}\n\n"
                out += "Products:\n"
                for p in products:
                    out += f"{p.id} | {p.name} | {p.category} | ${p.price:.2f} | Stock: {p.quantity}\n"

            elif rtype == 'Customer Analysis':
                bills = self.billing_service.get_all_bills()
                customers = {}
                for b in bills:
                    name = b.customer.name
                    customers.setdefault(name, 0)
                    customers[name] += b.total_amount
                out += "Customer Analysis\n\nTop Customers by Spend:\n"
                for name, val in sorted(customers.items(), key=lambda x: x[1], reverse=True)[:10]:
                    out += f"{name}: ${val:.2f}\n"

            else:
                # AI features removed; show a placeholder message
                out += "AI features are not available in this build.\n"

            # Display
            self.report_display.delete('1.0', tk.END)
            self.report_display.insert('1.0', out)

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    

    def _export_report(self):
        """Export the currently displayed report to a text file"""
        try:
            content = self.report_display.get('1.0', tk.END).strip()
            if not content:
                messagebox.showinfo("Export Report", "No report content to export")
                return
            reports_dir = os.path.join(os.getcwd(), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            fname = os.path.join(reports_dir, f"report_{int(datetime.now().timestamp())}.txt")
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Exported", f"Report exported to {fname}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            messagebox.showerror("Error", f"Failed to export report: {e}")
    def _save_email_settings(self): pass
    def _start_api_server(self): pass
    def _open_api_docs(self): pass
    def _load_system_info(self): pass
    
    def _on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
