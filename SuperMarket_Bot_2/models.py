"""
Data models for the improved supermarket system
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Product:
    """Product model with all necessary attributes"""
    id: str
    name: str
    category: str
    price: float
    quantity: int
    min_stock_level: int = 50
    tax_rate: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'quantity': self.quantity,
            'min_stock_level': self.min_stock_level,
            'tax_rate': self.tax_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Product':
        return cls(**data)


@dataclass
class Customer:
    """Customer model"""
    name: str
    phone: str
    email: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email
        }


@dataclass
class BillItem:
    """Individual item in a bill"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    tax_amount: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'tax_amount': self.tax_amount
        }


@dataclass
class Bill:
    """Complete bill model"""
    id: str
    customer: Customer
    items: List[BillItem]
    subtotal: float
    tax_amount: float
    total_amount: float
    created_at: datetime
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'customer': self.customer.to_dict(),
            'items': [item.to_dict() for item in self.items],
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat(),
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Bill':
        # Parse datetime
        created_at = datetime.fromisoformat(
            data['created_at'].replace('Z', '+00:00')
        )

        # Parse customer
        customer = Customer(**data['customer'])

        # Parse items
        items = [BillItem(**item) for item in data['items']]

        # Support both 'id' and legacy 'bill_id' keys
        bill_id = data.get('id') or data.get('bill_id')

        return cls(
            id=bill_id,
            customer=customer,
            items=items,
            subtotal=data['subtotal'],
            tax_amount=data['tax_amount'],
            total_amount=data['total_amount'],
            created_at=created_at,
            status=data.get('status', 'pending'),
        )

    @property
    def bill_id(self) -> str:
        """Backward-compatible alias for the bill id"""
        return self.id
    
    def to_receipt_text(self) -> str:
        """Generate receipt text format"""
        receipt = f"""
{'='*50}
SUPERMARKET BILLING SYSTEM
{'='*50}
Bill ID: {self.id}
Date: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Customer: {self.customer.name}
Phone: {self.customer.phone}
{'='*50}
ITEMS:
"""
        for item in self.items:
            receipt += (
                f"{item.product_name:<20} {item.quantity:>3} x "
                f"{item.unit_price:>8.2f} = {item.total_price:>8.2f}\n"
            )
        
        receipt += f"""
{'='*50}
Subtotal: {self.subtotal:>8.2f}
Tax:      {self.tax_amount:>8.2f}
Total:    {self.total_amount:>8.2f}
{'='*50}
Thank you for shopping with us!
"""
        return receipt


@dataclass
class InventoryAlert:
    """Alert for low stock items"""
    product_id: str
    product_name: str
    current_quantity: int
    min_required: int
    suggested_order_quantity: int
    
    def to_dict(self) -> Dict:
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'current_quantity': self.current_quantity,
            'min_required': self.min_required,
            'suggested_order_quantity': self.suggested_order_quantity
        }
