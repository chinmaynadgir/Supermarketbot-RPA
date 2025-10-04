"""
Database operations for the improved supermarket system
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

from models import Product, Bill, Customer, InventoryAlert

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.products_file = os.path.join(data_dir, "products.json")
        self.bills_file = os.path.join(data_dir, "bills.json")
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_products(self) -> Dict[str, Product]:
        """Load products from JSON file"""
        try:
            if os.path.exists(self.products_file):
                with open(self.products_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {pid: Product.from_dict(pdata) for pid, pdata in data.items()}
            return {}
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            return {}
    
    def get_all_products(self) -> List[Product]:
        """Get all products as a list"""
        products_dict = self.load_products()
        return list(products_dict.values())
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by its ID"""
        products = self.load_products()
        return products.get(product_id)
    
    def add_product(self, product: Product):
        """Add a new product"""
        products = self.load_products()
        products[product.id] = product
        self.save_products(products)
    
    def update_product(self, product: Product):
        """Update an existing product"""
        products = self.load_products()
        products[product.id] = product
        self.save_products(products)
    
    def delete_product(self, product_id: str):
        """Delete a product by ID"""
        products = self.load_products()
        if product_id in products:
            del products[product_id]
            self.save_products(products)
    
    def load_bills(self) -> List[Bill]:
        """Load bills from JSON file"""
        try:
            if os.path.exists(self.bills_file):
                with open(self.bills_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    bills = []
                    for bill_data in data:
                        try:
                            # Handle both old and new format
                            if 'bill_id' in bill_data:
                                bill_data['id'] = bill_data.pop('bill_id')
                            bills.append(Bill.from_dict(bill_data))
                        except Exception as e:
                            logger.warning(f"Skipping invalid bill data: {e}")
                            continue
                    return bills
            return []
        except Exception as e:
            logger.error(f"Error loading bills: {e}")
            return []
    
    def save_bills(self, bills: List[Bill]):
        """Save bills to JSON file"""
        try:
            data = [bill.to_dict() for bill in bills]
            with open(self.bills_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Error saving bills: {e}")
            raise
    
    def add_bill(self, bill: Bill):
        """Add a new bill"""
        bills = self.load_bills()
        bills.append(bill)
        self.save_bills(bills)
    
    def get_bill_by_id(self, bill_id: str) -> Optional[Bill]:
        """Get a bill by its ID"""
        bills = self.load_bills()
        for bill in bills:
            if bill.id == bill_id:
                return bill
        return None
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """Get a customer by phone number"""
        bills = self.load_bills()
        for bill in bills:
            if bill.customer.phone == phone:
                return bill.customer
        return None
    
    def initialize_default_products(self):
        """Initialize with default products if none exist"""
        products = self.load_products()
        if not products:
            default_products = [
                Product(id="med001", name="Hand Sanitizer 100ml", category="Medical", price=4.50, quantity=100, min_stock_level=20, tax_rate=0.05),
                Product(id="med002", name="Face Mask (Pack of 10)", category="Medical", price=5.00, quantity=100, min_stock_level=20, tax_rate=0.05),
                Product(id="med003", name="Thermal Gun", category="Medical", price=25.00, quantity=100, min_stock_level=10, tax_rate=0.05),
                Product(id="med004", name="Hand Gloves (Box of 100)", category="Medical", price=12.00, quantity=100, min_stock_level=20, tax_rate=0.05),
                Product(id="med005", name="Cough Syrup 100ml", category="Medical", price=8.00, quantity=100, min_stock_level=20, tax_rate=0.05),
                Product(id="med006", name="Antiseptic Cream 50g", category="Medical", price=6.00, quantity=100, min_stock_level=20, tax_rate=0.05),
                
                Product(id="gro001", name="Rice 1kg", category="Grocery", price=3.00, quantity=100, min_stock_level=30, tax_rate=0.05),
                Product(id="gro002", name="Cooking Oil 1L", category="Grocery", price=4.00, quantity=100, min_stock_level=30, tax_rate=0.05),
                Product(id="gro003", name="Wheat Flour 1kg", category="Grocery", price=2.00, quantity=100, min_stock_level=30, tax_rate=0.05),
                Product(id="gro004", name="Spices Pack", category="Grocery", price=3.00, quantity=100, min_stock_level=25, tax_rate=0.05),
                Product(id="gro005", name="Sugar 1kg", category="Grocery", price=2.50, quantity=100, min_stock_level=30, tax_rate=0.05),
                Product(id="gro006", name="Salt 1kg", category="Grocery", price=1.50, quantity=100, min_stock_level=30, tax_rate=0.05),
                Product(id="gro007", name="Maggi Noodles", category="Grocery", price=1.50, quantity=100, min_stock_level=30, tax_rate=0.05),
                Product(id="gro008", name="Bread Loaf", category="Grocery", price=2.00, quantity=100, min_stock_level=25, tax_rate=0.05),
                
                Product(id="cld001", name="Coca Cola 500ml", category="Cold Drinks", price=2.50, quantity=100, min_stock_level=40, tax_rate=0.10),
                Product(id="cld002", name="Sprite 500ml", category="Cold Drinks", price=2.50, quantity=100, min_stock_level=40, tax_rate=0.10),
                Product(id="cld003", name="Mineral Water 1L", category="Cold Drinks", price=1.50, quantity=100, min_stock_level=50, tax_rate=0.10),
                Product(id="cld004", name="Mango Juice 1L", category="Cold Drinks", price=3.50, quantity=100, min_stock_level=30, tax_rate=0.10),
                Product(id="cld005", name="Lassi 200ml", category="Cold Drinks", price=2.00, quantity=100, min_stock_level=30, tax_rate=0.10),
                Product(id="cld006", name="Mountain Dew 500ml", category="Cold Drinks", price=2.25, quantity=100, min_stock_level=40, tax_rate=0.10),
            ]
            
            for product in default_products:
                products[product.id] = product
            
            self.save_products(products)
            logger.info("Default products initialized successfully")
    
    def save_products(self, products: Dict[str, Product]):
        """Save products to JSON file"""
        try:
            data = {pid: product.to_dict() for pid, product in products.items()}
            with open(self.products_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving products: {e}")
            raise
    def update_product_quantity(self, product_id: str, new_quantity: int):
        """Update product quantity in inventory"""
        products = self.load_products()
        if product_id in products:
            products[product_id].quantity = new_quantity
            self.save_products(products)
            return True
        return False

    def get_low_stock_products(self) -> List[InventoryAlert]:
        """Get products that are below minimum stock level"""
        products = self.load_products()
        alerts = []

        for product in products.values():
            if product.quantity < product.min_stock_level:
                alert = InventoryAlert(
                    product_id=product.id,
                    product_name=product.name,
                    current_quantity=product.quantity,
                    min_required=product.min_stock_level,
                    suggested_order_quantity=(100 - product.quantity)
                )
                alerts.append(alert)

        return alerts

    # initialize_default_products defined earlier; keep single implementation
