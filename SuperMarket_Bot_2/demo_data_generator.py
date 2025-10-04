"""
Demo Data Generator for Supermarket Management System
Creates realistic demo data for showcasing all features
"""
import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

from models import Product, Bill, Customer, BillItem
from database import DatabaseManager

class DemoDataGenerator:
    """Generates realistic demo data for the supermarket system"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Sample customer data
        self.customers = [
            {"name": "John Smith", "phone": "555-0101", "email": "john.smith@email.com"},
            {"name": "Sarah Johnson", "phone": "555-0102", "email": "sarah.j@email.com"},
            {"name": "Mike Davis", "phone": "555-0103", "email": "mike.davis@email.com"},
            {"name": "Emily Brown", "phone": "555-0104", "email": "emily.brown@email.com"},
            {"name": "David Wilson", "phone": "555-0105", "email": "david.w@email.com"},
            {"name": "Lisa Anderson", "phone": "555-0106", "email": "lisa.anderson@email.com"},
            {"name": "Robert Taylor", "phone": "555-0107", "email": "robert.t@email.com"},
            {"name": "Jennifer Martinez", "phone": "555-0108", "email": "j.martinez@email.com"},
            {"name": "William Garcia", "phone": "555-0109", "email": "will.garcia@email.com"},
            {"name": "Amanda Rodriguez", "phone": "555-0110", "email": "amanda.r@email.com"},
            {"name": "Christopher Lee", "phone": "555-0111", "email": "chris.lee@email.com"},
            {"name": "Michelle White", "phone": "555-0112", "email": "michelle.white@email.com"},
            {"name": "Daniel Harris", "phone": "555-0113", "email": "daniel.h@email.com"},
            {"name": "Ashley Clark", "phone": "555-0114", "email": "ashley.clark@email.com"},
            {"name": "Matthew Lewis", "phone": "555-0115", "email": "matt.lewis@email.com"},
        ]
        
        # Product categories with realistic pricing
        self.product_categories = {
            "Medical": [
                {"name": "Hand Sanitizer 100ml", "price": 4.50, "min_stock": 20},
                {"name": "Face Mask (Pack of 10)", "price": 5.00, "min_stock": 20},
                {"name": "Thermal Gun", "price": 25.00, "min_stock": 10},
                {"name": "Hand Gloves (Box of 100)", "price": 12.00, "min_stock": 20},
                {"name": "Cough Syrup 100ml", "price": 8.00, "min_stock": 20},
                {"name": "Antiseptic Cream 50g", "price": 6.00, "min_stock": 20},
                {"name": "Band-Aids (Box of 50)", "price": 3.50, "min_stock": 25},
                {"name": "Pain Relief Tablets", "price": 7.50, "min_stock": 30},
            ],
            "Grocery": [
                {"name": "Rice 1kg", "price": 3.00, "min_stock": 30},
                {"name": "Cooking Oil 1L", "price": 4.00, "min_stock": 30},
                {"name": "Wheat Flour 1kg", "price": 2.00, "min_stock": 30},
                {"name": "Spices Pack", "price": 3.00, "min_stock": 25},
                {"name": "Sugar 1kg", "price": 2.50, "min_stock": 30},
                {"name": "Salt 1kg", "price": 1.50, "min_stock": 30},
                {"name": "Maggi Noodles", "price": 1.50, "min_stock": 30},
                {"name": "Bread Loaf", "price": 2.00, "min_stock": 25},
                {"name": "Milk 1L", "price": 2.50, "min_stock": 40},
                {"name": "Eggs (Dozen)", "price": 3.50, "min_stock": 35},
            ],
            "Cold Drinks": [
                {"name": "Coca Cola 500ml", "price": 2.50, "min_stock": 40},
                {"name": "Sprite 500ml", "price": 2.50, "min_stock": 40},
                {"name": "Mineral Water 1L", "price": 1.50, "min_stock": 50},
                {"name": "Mango Juice 1L", "price": 3.50, "min_stock": 30},
                {"name": "Lassi 200ml", "price": 2.00, "min_stock": 30},
                {"name": "Mountain Dew 500ml", "price": 2.25, "min_stock": 40},
                {"name": "Orange Juice 1L", "price": 3.00, "min_stock": 30},
                {"name": "Energy Drink 250ml", "price": 4.50, "min_stock": 25},
            ]
        }
    
    def generate_products(self):
        """Generate realistic product data"""
        print("🛍️  Generating product data...")
        
        products = {}
        product_id = 1
        
        for category, items in self.product_categories.items():
            for item in items:
                # Create realistic stock levels (some low, some high)
                if random.random() < 0.2:  # 20% chance of low stock
                    quantity = random.randint(5, item["min_stock"] - 5)
                else:
                    quantity = random.randint(item["min_stock"], item["min_stock"] + 50)
                
                product = Product(
                    id=f"{category[:3].lower()}{product_id:03d}",
                    name=item["name"],
                    category=category,
                    price=item["price"],
                    quantity=quantity,
                    min_stock_level=item["min_stock"],
                    tax_rate=0.05 if category != "Cold Drinks" else 0.10
                )
                
                products[product.id] = product
                product_id += 1
        
        # Save products
        self.db.save_products(products)
        print(f"✅ Generated {len(products)} products")
        return products
    
    def generate_bills(self, num_bills: int = 50):
        """Generate realistic bill data for the last 30 days"""
        print(f"🧾 Generating {num_bills} bills...")
        
        products = self.db.load_products()
        bills = []
        
        # Generate bills over the last 30 days
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(num_bills):
            # Random date within last 30 days
            bill_date = start_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(8, 20),  # Business hours
                minutes=random.randint(0, 59)
            )
            
            # Random customer
            customer_data = random.choice(self.customers)
            customer = Customer(
                name=customer_data["name"],
                phone=customer_data["phone"],
                email=customer_data["email"]
            )
            
            # Generate 1-8 items per bill
            num_items = random.randint(1, 8)
            bill_items = []
            subtotal = 0.0
            total_tax = 0.0
            
            selected_products = random.sample(list(products.keys()), min(num_items, len(products)))
            
            for product_id in selected_products:
                product = products[product_id]
                if product.quantity <= 0:
                    continue  # Skip products with no stock
                quantity = random.randint(1, min(5, product.quantity))  # Don't exceed stock
                
                unit_price = product.price
                item_total = unit_price * quantity
                tax_amount = item_total * product.tax_rate
                
                bill_item = BillItem(
                    product_id=product_id,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=item_total,
                    tax_amount=tax_amount
                )
                
                bill_items.append(bill_item)
                subtotal += item_total
                total_tax += tax_amount
                
                # Update product quantity (simulate sales)
                product.quantity -= quantity
                if product.quantity < 0:
                    product.quantity = 0
            
            total_amount = subtotal + total_tax
            
            bill = Bill(
                id=f"BILL{random.randint(1000, 9999)}",
                customer=customer,
                items=bill_items,
                subtotal=subtotal,
                tax_amount=total_tax,
                total_amount=total_amount,
                created_at=bill_date,
                status="completed"
            )
            
            bills.append(bill)
        
        # Save bills
        self.db.save_bills(bills)
        print(f"✅ Generated {len(bills)} bills")
        return bills
    
    def generate_demo_data(self):
        """Generate complete demo dataset"""
        print("🚀 Generating comprehensive demo data...")
        print("=" * 50)
        
        # Generate products
        products = self.generate_products()
        
        # Generate bills
        bills = self.generate_bills(75)  # 75 bills for good analytics
        
        # Update product quantities based on sales
        print("📊 Updating inventory based on sales...")
        self.db.save_products(products)
        
        print("=" * 50)
        print("🎉 Demo data generation complete!")
        print(f"📦 Products: {len(products)}")
        print(f"🧾 Bills: {len(bills)}")
        print(f"👥 Customers: {len(self.customers)}")
        
        # Print some statistics
        total_sales = sum(bill.total_amount for bill in bills)
        avg_bill = total_sales / len(bills) if bills else 0
        
        print(f"💰 Total Sales: ${total_sales:.2f}")
        print(f"📈 Average Bill: ${avg_bill:.2f}")
        
        # Show low stock items
        low_stock = [p for p in products.values() if p.quantity < p.min_stock_level]
        if low_stock:
            print(f"⚠️  Low Stock Items: {len(low_stock)}")
            for product in low_stock[:3]:  # Show first 3
                print(f"   - {product.name}: {product.quantity} units")
        
        return {
            'products': products,
            'bills': bills,
            'customers': self.customers
        }

def main():
    """Generate demo data"""
    db_manager = DatabaseManager()
    generator = DemoDataGenerator(db_manager)
    generator.generate_demo_data()

if __name__ == "__main__":
    main()
