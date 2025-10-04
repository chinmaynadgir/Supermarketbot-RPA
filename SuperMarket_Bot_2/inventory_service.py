"""
Inventory management service for the improved supermarket system
"""
import logging
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from models import Product, InventoryAlert
from database import DatabaseManager

logger = logging.getLogger(__name__)


class InventoryService:
    """Handles inventory management operations"""
    
    def __init__(self, db_manager: DatabaseManager, email_config: Dict = None):
        self.db = db_manager
        self.email_config = email_config or {}
    
    def get_all_products(self) -> List[Product]:
        """Get all products"""
        return self.db.get_all_products()
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return self.db.get_product_by_id(product_id)
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        products = self.db.get_all_products()
        return [product for product in products 
                if product.category.lower() == category.lower()]
    
    def update_product_quantity(self, product_id: str, new_quantity: int) -> bool:
        """Update product quantity"""
        try:
            if new_quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            product = self.db.get_product_by_id(product_id)
            if product:
                product.quantity = new_quantity
                self.db.update_product(product)
                logger.info(f"Updated quantity for product {product_id} to {new_quantity}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating product quantity: {e}")
            return False
    
    def get_inventory_summary(self) -> Dict:
        """Get inventory summary"""
        try:
            products = self.get_all_products()
            total_products = len(products)
            low_stock_count = sum(1 for p in products if p.quantity < p.min_stock_level)
            total_inventory_value = sum(p.price * p.quantity for p in products)
            
            # Calculate stock health percentage
            healthy_products = sum(1 for p in products if p.quantity >= p.min_stock_level)
            stock_health = f"{(healthy_products / total_products * 100):.1f}%" if total_products > 0 else "0%"
            
            return {
                'total_products': total_products,
                'low_stock_count': low_stock_count,
                'total_inventory_value': round(total_inventory_value, 2),
                'stock_health': stock_health
            }
        except Exception as e:
            logger.error(f"Error getting inventory summary: {e}")
            return {'total_products': 0, 'low_stock_count': 0, 'total_inventory_value': 0, 'stock_health': '0%'}
    
    def get_low_stock_products(self) -> List[Product]:
        """Get products with low stock"""
        products = self.get_all_products()
        return [p for p in products if p.quantity < p.min_stock_level]
    
    def check_stock_levels(self) -> List[InventoryAlert]:
        """Check stock levels and generate alerts"""
        try:
            products = self.get_all_products()
            alerts = []
            
            for product in products:
                if product.quantity < product.min_stock_level:
                    alert = InventoryAlert(
                        product_id=product.id,
                        product_name=product.name,
                        current_quantity=product.quantity,
                        min_required=product.min_stock_level,
                        suggested_order_quantity=max(50, product.min_stock_level * 2)
                    )
                    alerts.append(alert)
                    logger.warning(f"Low stock alert for {product.name}: {product.quantity} units left")
            
            return alerts
        except Exception as e:
            logger.error(f"Error checking stock levels: {e}")
            return []
    
    def send_low_stock_alerts(self, alerts: List[InventoryAlert]):
        """Send email alerts for low stock items"""
        if not alerts:
            return
        
        # This would integrate with email service
        logger.info(f"Would send {len(alerts)} low stock alerts via email")
        for alert in alerts:
            logger.info(f"Low stock: {alert.product_name} - {alert.current_quantity} units left")
    
    def add_stock(self, product_id: str, quantity: int) -> bool:
        """Add stock to existing product"""
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")
            
            new_quantity = product.quantity + quantity
            return self.update_product_quantity(product_id, new_quantity)
        except Exception as e:
            logger.error(f"Error adding stock: {e}")
            return False
    
    def get_low_stock_alerts(self) -> List[InventoryAlert]:
        """Get low stock alerts"""
        return self.db.get_low_stock_products()
    
    def check_stock_levels(self) -> Dict[str, List[InventoryAlert]]:
        """Check stock levels and categorize alerts"""
        alerts = self.get_low_stock_alerts()
        
        categorized = {
            'critical': [],  # < 10 items
            'low': [],       # 10-49 items
            'normal': []     # >= 50 items
        }
        
        for alert in alerts:
            if alert.current_quantity < 10:
                categorized['critical'].append(alert)
            elif alert.current_quantity < 50:
                categorized['low'].append(alert)
            else:
                categorized['normal'].append(alert)
        
        return categorized
    
    def generate_purchase_order(self, alerts: List[InventoryAlert]) -> str:
        """Generate purchase order text"""
        if not alerts:
            return "No items need to be ordered."
        
        order_text = "PURCHASE ORDER\n"
        order_text += "=" * 50 + "\n"
        order_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        order_text += "SuperMarket Purchase Order\n"
        order_text += "=" * 50 + "\n"
        order_text += f"{'ITEM':<30} {'CURRENT':<10} {'REQUIRED':<10} {'ORDER':<10}\n"
        order_text += "-" * 60 + "\n"
        
        total_order_value = 0
        
        for alert in alerts:
            order_text += f"{alert.product_name:<30} {alert.current_quantity:<10} {alert.min_required:<10} {alert.suggested_order_quantity:<10}\n"
            # Assuming average cost of 5 per item for calculation
            total_order_value += alert.suggested_order_quantity * 5
        
        order_text += "-" * 60 + "\n"
        order_text += f"Estimated Total Order Value: ${total_order_value:.2f}\n"
        order_text += "=" * 50
        
        return order_text
    
    def send_low_stock_email(self, email_config: Dict, alerts: List[InventoryAlert]) -> bool:
        """Send low stock alert email"""
        try:
            if not alerts:
                return True
            
            order_text = self.generate_purchase_order(alerts)
            
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']
            msg['Subject'] = "Low Stock Alert - Purchase Order Required"
            
            body = f"""
Dear Manager,

The following items are running low on stock and need to be reordered:

{order_text}

Please process this order as soon as possible to avoid stockouts.

Best regards,
Supermarket Inventory System
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['from_email'], email_config['password'])
            text = msg.as_string()
            server.sendmail(email_config['from_email'], email_config['to_email'], text)
            server.quit()
            
            logger.info("Low stock email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def get_inventory_summary(self) -> Dict:
        """Get inventory summary statistics"""
        products = self.db.load_products()
        alerts = self.get_low_stock_alerts()
        
        total_products = len(products)
        low_stock_count = len(alerts)
        total_value = sum(product.price * product.quantity for product in products.values())
        
        categories = {}
        for product in products.values():
            if product.category not in categories:
                categories[product.category] = {'count': 0, 'value': 0}
            categories[product.category]['count'] += 1
            categories[product.category]['value'] += product.price * product.quantity
        
        return {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'total_inventory_value': total_value,
            'categories': categories,
            'stock_health': 'Good' if low_stock_count == 0 else 'Needs Attention'
        }
    
    def bulk_update_inventory(self, updates: Dict[str, int]) -> Dict[str, bool]:
        """Bulk update inventory quantities"""
        results = {}
        
        for product_id, new_quantity in updates.items():
            try:
                success = self.update_product_quantity(product_id, new_quantity)
                results[product_id] = success
            except Exception as e:
                logger.error(f"Error updating {product_id}: {e}")
                results[product_id] = False
        
        return results
