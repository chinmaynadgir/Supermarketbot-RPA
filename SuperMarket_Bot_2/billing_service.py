"""
Billing service for the improved supermarket system
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid

from models import Bill, BillItem, Customer
from database import DatabaseManager

logger = logging.getLogger(__name__)


class BillingService:
    """Handles all billing operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_bill(self, customer_info: Dict, items_purchased: Dict[str, int]) -> Optional[Bill]:
        """Create a new bill with given items"""
        try:
            # Create customer object
            customer = Customer(
                name=customer_info.get("name", ""),
                phone=customer_info.get("phone", ""),
                email=customer_info.get("email")
            )
            
            products = self.db.load_products()
            bill_items = []
            subtotal = 0.0
            total_tax = 0.0
            
            for product_id, quantity in items_purchased.items():
                if product_id not in products:
                    logger.error(f"Product {product_id} not found")
                    return None
                
                product = products[product_id]
                if product.quantity < quantity:
                    logger.error(f"Insufficient stock for {product.name}. Available: {product.quantity}")
                    return None
                
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
                
                # Update product quantity
                product.quantity -= quantity
                self.db.update_product(product)
            
            total_amount = subtotal + total_tax
            
            bill = Bill(
                id=str(uuid.uuid4())[:8].upper(),
                customer=customer,
                items=bill_items,
                subtotal=subtotal,
                tax_amount=total_tax,
                total_amount=total_amount,
                created_at=datetime.now(),
                status="completed"
            )
            
            # Save bill
            self.db.add_bill(bill)
            
            logger.info(f"Bill {bill.id} created successfully")
            return bill
            
        except Exception as e:
            logger.error(f"Error creating bill: {e}")
            raise
    
    
    def get_bill_by_id(self, bill_id: str) -> Optional[Bill]:
        """Get bill by ID"""
        return self.db.get_bill_by_id(bill_id)
    
    def get_all_bills(self) -> List[Bill]:
        """Get all bills"""
        return self.db.load_bills()
    
    def search_bills_by_customer(self, customer_name: str) -> List[Bill]:
        """Search bills by customer name"""
        bills = self.db.load_bills()
        return [bill for bill in bills if customer_name.lower() in bill.customer.name.lower()]
    
    def get_daily_sales_summary(self, date: datetime) -> Dict:
        """Get daily sales summary"""
        bills = self.db.load_bills()
        daily_bills = [bill for bill in bills if bill.created_at.date() == date.date()]
        
        total_sales = sum(bill.total_amount for bill in daily_bills)
        total_bills = len(daily_bills)
        total_items = sum(len(bill.items) for bill in daily_bills)
        
        return {
            'date': date.date().isoformat(),
            'total_sales': total_sales,
            'total_bills': total_bills,
            'total_items': total_items,
            'average_bill_value': total_sales / total_bills if total_bills > 0 else 0
        }
    
    def get_bill_details(self, bill_id: str) -> Optional[Bill]:
        """Get bill details by ID"""
        return self.get_bill_by_id(bill_id)
    
    def get_customer_bills(self, customer_id: str) -> List[Bill]:
        """Get bills for a customer"""
        bills = self.db.load_bills()
        return [bill for bill in bills if bill.customer.phone == customer_id]
    
    def validate_customer_data(self, name: str, phone: str) -> Tuple[bool, str]:
        """Validate customer data"""
        if not name or not name.strip():
            return False, "Customer name is required"
        
        if not phone or not phone.strip():
            return False, "Phone number is required"
        
        # Basic phone validation (you can enhance this)
        if len(phone) < 10:
            return False, "Phone number must be at least 10 digits"
        
        return True, "Valid"
    
    def validate_quantity(self, product_id: str, quantity: int) -> Tuple[bool, str]:
        """Validate product quantity"""
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        products = self.db.load_products()
        if product_id not in products:
            return False, "Product not found"
        
        if products[product_id].quantity < quantity:
            return False, f"Insufficient stock. Available: {products[product_id].quantity}"
        
        return True, "Valid"
