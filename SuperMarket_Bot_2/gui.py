"""
Modern GUI for the improved supermarket system using tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import datetime
import threading
import webbrowser

from models import Customer, Bill
from database import DatabaseManager
from billing_service import BillingService
from inventory_service import InventoryService
from dashboard import RealTimeDashboard
from barcode_scanner import BarcodeScanner
# AI features removed: keep GUI focused on core functionality

logger = logging.getLogger(__name__)


class ModernSupermarketGUI:
    """Modern GUI for the supermarket system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modern Supermarket Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize services
        self.db_manager = DatabaseManager()
        self.billing_service = BillingService(self.db_manager)
        self.inventory_service = InventoryService(self.db_manager)
        
        # Initialize database
        self.db_manager.initialize_default_products()
        
        # Variables
        self.current_bill_items = []
        self.products = self.inventory_service.get_all_products()
        
        self.setup_ui()
        self.load_products_to_tree()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_billing_tab()
        self.create_inventory_tab()
        self.create_reports_tab()
        self.create_settings_tab()
    
    def create_billing_tab(self):
        """Create billing tab"""
        billing_frame = ttk.Frame(self.notebook)
        self.notebook.add(billing_frame, text="Billing")
        
        # Customer details frame
        customer_frame = ttk.LabelFrame(billing_frame, text="Customer Details", padding=10)
        customer_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(customer_frame, text="Customer Name:").grid(row=0, column=0, sticky='w', padx=5)
        self.customer_name_var = tk.StringVar()
        ttk.Entry(customer_frame, textvariable=self.customer_name_var, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(customer_frame, text="Phone:").grid(row=0, column=2, sticky='w', padx=5)
        self.customer_phone_var = tk.StringVar()
        ttk.Entry(customer_frame, textvariable=self.customer_phone_var, width=20).grid(row=0, column=3, padx=5)
        
        # Products frame
        products_frame = ttk.LabelFrame(billing_frame, text="Products", padding=10)
        products_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Product selection
        selection_frame = ttk.Frame(products_frame)
        selection_frame.pack(fill='x', pady=5)
        
        ttk.Label(selection_frame, text="Category:").pack(side='left', padx=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(selection_frame, textvariable=self.category_var, 
                                          values=["All", "Medical", "Grocery", "Cold Drinks"])
        self.category_combo.pack(side='left', padx=5)
        self.category_combo.set("All")
        self.category_combo.bind('<<ComboboxSelected>>', self.filter_products)
        
        ttk.Label(selection_frame, text="Product:").pack(side='left', padx=5)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(selection_frame, textvariable=self.product_var, width=30)
        self.product_combo.pack(side='left', padx=5)
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        ttk.Label(selection_frame, text="Quantity:").pack(side='left', padx=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.quantity_var, width=10).pack(side='left', padx=5)
        
        ttk.Button(selection_frame, text="Add to Bill", command=self.add_to_bill).pack(side='left', padx=5)
        
        # Current bill items
        bill_frame = ttk.LabelFrame(products_frame, text="Current Bill", padding=10)
        bill_frame.pack(fill='both', expand=True, pady=5)
        
        # Bill items tree
        columns = ('Product', 'Quantity', 'Unit Price', 'Total')
        self.bill_tree = ttk.Treeview(bill_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.bill_tree.heading(col, text=col)
            self.bill_tree.column(col, width=120)
        
        self.bill_tree.pack(fill='both', expand=True)
        
        # Bill summary
        summary_frame = ttk.Frame(bill_frame)
        summary_frame.pack(fill='x', pady=5)
        
        self.subtotal_var = tk.StringVar(value="Subtotal: $0.00")
        self.tax_var = tk.StringVar(value="Tax: $0.00")
        self.total_var = tk.StringVar(value="Total: $0.00")
        
        ttk.Label(summary_frame, textvariable=self.subtotal_var).pack(side='left', padx=10)
        ttk.Label(summary_frame, textvariable=self.tax_var).pack(side='left', padx=10)
        ttk.Label(summary_frame, textvariable=self.total_var, font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        
        # Bill actions
        actions_frame = ttk.Frame(bill_frame)
        actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(actions_frame, text="Generate Bill", command=self.generate_bill).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Clear Bill", command=self.clear_bill).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Remove Item", command=self.remove_item).pack(side='left', padx=5)
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="Inventory")
        
        # Inventory tree
        tree_frame = ttk.Frame(inventory_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Name', 'Category', 'Price', 'Quantity', 'Min Stock', 'Status')
        self.inventory_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=100)
        
        self.inventory_tree.pack(fill='both', expand=True)
        
        # Inventory actions
        actions_frame = ttk.Frame(inventory_frame)
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Refresh", command=self.refresh_inventory).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Check Low Stock", command=self.check_low_stock).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Update Stock", command=self.update_stock_dialog).pack(side='left', padx=5)
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Reports controls
        controls_frame = ttk.Frame(reports_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Daily Sales", command=self.show_daily_sales).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Inventory Summary", command=self.show_inventory_summary).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Low Stock Report", command=self.show_low_stock_report).pack(side='left', padx=5)
        
        # Reports display
        self.reports_text = scrolledtext.ScrolledText(reports_frame, height=20, width=80)
        self.reports_text.pack(fill='both', expand=True, padx=10, pady=5)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Email settings
        email_frame = ttk.LabelFrame(settings_frame, text="Email Settings", padding=10)
        email_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(email_frame, text="SMTP Server:").grid(row=0, column=0, sticky='w', padx=5)
        self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(email_frame, textvariable=self.smtp_server_var, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(email_frame, text="Port:").grid(row=0, column=2, sticky='w', padx=5)
        self.smtp_port_var = tk.StringVar(value="587")
        ttk.Entry(email_frame, textvariable=self.smtp_port_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(email_frame, text="From Email:").grid(row=1, column=0, sticky='w', padx=5)
        self.from_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.from_email_var, width=30).grid(row=1, column=1, padx=5)
        
        ttk.Label(email_frame, text="To Email:").grid(row=1, column=2, sticky='w', padx=5)
        self.to_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.to_email_var, width=30).grid(row=1, column=3, padx=5)
        
        ttk.Label(email_frame, text="Password:").grid(row=2, column=0, sticky='w', padx=5)
        self.email_password_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.email_password_var, show="*", width=30).grid(row=2, column=1, padx=5)
        
        ttk.Button(email_frame, text="Test Email", command=self.test_email).grid(row=2, column=2, padx=5)
        ttk.Button(email_frame, text="Send Low Stock Alert", command=self.send_low_stock_alert).grid(row=2, column=3, padx=5)
    
    def load_products_to_tree(self):
        """Load products into the product combobox"""
        self.products = self.inventory_service.get_all_products()
        product_names = [f"{product.name} (${product.price})" for product in self.products.values()]
        self.product_combo['values'] = product_names
    
    def filter_products(self, event=None):
        """Filter products by category"""
        category = self.category_var.get()
        if category == "All":
            self.load_products_to_tree()
        else:
            filtered_products = self.inventory_service.get_products_by_category(category)
            product_names = [f"{product.name} (${product.price})" for product in filtered_products.values()]
            self.product_combo['values'] = product_names
    
    def on_product_selected(self, event=None):
        """Handle product selection"""
        selected = self.product_var.get()
        if selected:
            # Extract product name from the selection
            product_name = selected.split(' (')[0]
            # Find the product
            for product in self.products.values():
                if product.name == product_name:
                    self.quantity_var.set("1")
                    break
    
    def add_to_bill(self):
        """Add selected product to bill"""
        try:
            selected = self.product_var.get()
            quantity = int(self.quantity_var.get())
            
            if not selected or quantity <= 0:
                messagebox.showerror("Error", "Please select a product and enter valid quantity")
                return
            
            # Extract product name and find product
            product_name = selected.split(' (')[0]
            product = None
            for p in self.products.values():
                if p.name == product_name:
                    product = p
                    break
            
            if not product:
                messagebox.showerror("Error", "Product not found")
                return
            
            # Validate quantity
            is_valid, message = self.billing_service.validate_quantity(product.id, quantity)
            if not is_valid:
                messagebox.showerror("Error", message)
                return
            
            # Add to current bill items
            self.current_bill_items.append((product.id, quantity))
            
            # Update bill tree
            self.update_bill_tree()
            self.update_bill_summary()
            
            # Clear selection
            self.product_var.set("")
            self.quantity_var.set("")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding item: {e}")
    
    def update_bill_tree(self):
        """Update the bill items tree"""
        # Clear existing items
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        
        # Add current items
        for product_id, quantity in self.current_bill_items:
            product = self.products[product_id]
            total = product.price * quantity
            self.bill_tree.insert('', 'end', values=(
                product.name, quantity, f"${product.price:.2f}", f"${total:.2f}"
            ))
    
    def update_bill_summary(self):
        """Update bill summary"""
        subtotal = 0
        total_tax = 0
        
        for product_id, quantity in self.current_bill_items:
            product = self.products[product_id]
            item_total = product.price * quantity
            subtotal += item_total
            total_tax += item_total * product.tax_rate
        
        total = subtotal + total_tax
        
        self.subtotal_var.set(f"Subtotal: ${subtotal:.2f}")
        self.tax_var.set(f"Tax: ${total_tax:.2f}")
        self.total_var.set(f"Total: ${total:.2f}")
    
    def remove_item(self):
        """Remove selected item from bill"""
        selection = self.bill_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        # Get the index of selected item
        item_index = self.bill_tree.index(selection[0])
        if 0 <= item_index < len(self.current_bill_items):
            del self.current_bill_items[item_index]
            self.update_bill_tree()
            self.update_bill_summary()
    
    def clear_bill(self):
        """Clear current bill"""
        self.current_bill_items = []
        self.update_bill_tree()
        self.update_bill_summary()
        self.customer_name_var.set("")
        self.customer_phone_var.set("")
    
    def generate_bill(self):
        """Generate and save bill"""
        try:
            # Validate customer data
            name = self.customer_name_var.get().strip()
            phone = self.customer_phone_var.get().strip()
            
            is_valid, message = self.billing_service.validate_customer_data(name, phone)
            if not is_valid:
                messagebox.showerror("Error", message)
                return
            
            if not self.current_bill_items:
                messagebox.showerror("Error", "No items in the bill")
                return
            
            # Create customer
            customer = Customer(name=name, phone=phone)
            
            # Create bill
            bill = self.billing_service.create_bill(customer, self.current_bill_items)
            
            # Show bill receipt
            self.show_bill_receipt(bill)
            
            # Clear bill
            self.clear_bill()
            
            messagebox.showinfo("Success", f"Bill {bill.bill_id} generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating bill: {e}")
    
    def show_bill_receipt(self, bill: Bill):
        """Show bill receipt in a new window"""
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title(f"Bill Receipt - {bill.bill_id}")
        receipt_window.geometry("500x600")
        
        receipt_text = scrolledtext.ScrolledText(receipt_window, height=30, width=60)
        receipt_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        receipt_text.insert('1.0', bill.to_receipt_text())
        receipt_text.config(state='disabled')
        
        # Save button
        ttk.Button(receipt_window, text="Save Receipt", 
                  command=lambda: self.save_receipt(bill)).pack(pady=5)
    
    def save_receipt(self, bill: Bill):
        """Save receipt to file"""
        try:
            filename = f"bills/bill_{bill.bill_id}.txt"
            with open(filename, 'w') as f:
                f.write(bill.to_receipt_text())
            messagebox.showinfo("Success", f"Receipt saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving receipt: {e}")
    
    def refresh_inventory(self):
        """Refresh inventory display"""
        # Clear tree
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Load products
        products = self.inventory_service.get_all_products()
        
        for product in products.values():
            status = "Low Stock" if product.quantity < product.min_stock_level else "OK"
            self.inventory_tree.insert('', 'end', values=(
                product.id, product.name, product.category, 
                f"${product.price:.2f}", product.quantity, 
                product.min_stock_level, status
            ))
    
    def check_low_stock(self):
        """Check and display low stock items"""
        alerts = self.inventory_service.get_low_stock_alerts()
        
        if not alerts:
            messagebox.showinfo("Stock Check", "All items are well stocked!")
        else:
            alert_text = "Low Stock Items:\n\n"
            for alert in alerts:
                alert_text += f"{alert.product_name}: {alert.current_quantity} (Min: {alert.min_required})\n"
            
            messagebox.showwarning("Low Stock Alert", alert_text)
    
    def update_stock_dialog(self):
        """Show dialog to update stock"""
        # This would open a dialog to update stock quantities
        messagebox.showinfo("Info", "Stock update dialog would open here")
    
    def show_daily_sales(self):
        """Show daily sales report"""
        today = datetime.now()
        summary = self.billing_service.get_daily_sales_summary(today)
        
        report = f"""
Daily Sales Report - {summary['date']}
{'='*50}
Total Sales: ${summary['total_sales']:.2f}
Total Bills: {summary['total_bills']}
Total Items Sold: {summary['total_items']}
Average Bill Value: ${summary['average_bill_value']:.2f}
"""
        
        self.reports_text.delete('1.0', tk.END)
        self.reports_text.insert('1.0', report)
    
    def show_inventory_summary(self):
        """Show inventory summary"""
        summary = self.inventory_service.get_inventory_summary()
        
        report = f"""
Inventory Summary
{'='*50}
Total Products: {summary['total_products']}
Low Stock Items: {summary['low_stock_count']}
Total Inventory Value: ${summary['total_inventory_value']:.2f}
Stock Health: {summary['stock_health']}

Category Breakdown:
"""
        
        for category, data in summary['categories'].items():
            report += f"{category}: {data['count']} items, ${data['value']:.2f}\n"
        
        self.reports_text.delete('1.0', tk.END)
        self.reports_text.insert('1.0', report)
    
    def show_low_stock_report(self):
        """Show low stock report"""
        alerts = self.inventory_service.get_low_stock_alerts()
        
        if not alerts:
            report = "No low stock items found."
        else:
            report = "Low Stock Report\n" + "="*50 + "\n\n"
            for alert in alerts:
                report += f"{alert.product_name}: {alert.current_quantity} (Min: {alert.min_required})\n"
                report += f"Suggested Order: {alert.suggested_order_quantity} units\n\n"
        
        self.reports_text.delete('1.0', tk.END)
        self.reports_text.insert('1.0', report)
    
    def test_email(self):
        """Test email configuration"""
        messagebox.showinfo("Info", "Email test functionality would be implemented here")
    
    def send_low_stock_alert(self):
        """Send low stock alert email"""
        alerts = self.inventory_service.get_low_stock_alerts()
        
        if not alerts:
            messagebox.showinfo("Info", "No low stock items to report")
            return
        
        email_config = {
            'smtp_server': self.smtp_server_var.get(),
            'smtp_port': int(self.smtp_port_var.get()),
            'from_email': self.from_email_var.get(),
            'to_email': self.to_email_var.get(),
            'password': self.email_password_var.get()
        }
        
        success = self.inventory_service.send_low_stock_email(email_config, alerts)
        
        if success:
            messagebox.showinfo("Success", "Low stock alert email sent successfully!")
        else:
            messagebox.showerror("Error", "Failed to send email. Please check your settings.")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run the application
    app = ModernSupermarketGUI()
    app.run()
