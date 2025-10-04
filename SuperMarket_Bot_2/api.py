"""
REST API for Supermarket Management System
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import uvicorn
from contextlib import asynccontextmanager

from models import Product, Bill, Customer, BillItem
from database import DatabaseManager
from billing_service import BillingService
from inventory_service import InventoryService
# AI features removed for this release

logger = logging.getLogger(__name__)

# Global instances
db_manager = None
billing_service = None
inventory_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global db_manager, billing_service, inventory_service
    
    # Initialize services
    db_manager = DatabaseManager()
    billing_service = BillingService(db_manager)
    inventory_service = InventoryService(db_manager, {})
    
    logger.info("API services initialized")
    yield
    
    # Cleanup on shutdown
    logger.info("API services shutdown")

# Create FastAPI app
app = FastAPI(
    title="Supermarket Management API",
    description="REST API for modern supermarket management system",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    quantity: int
    min_stock_level: int = 50
    tax_rate: float = 0.0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    tax_rate: Optional[float] = None

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None

class BillItemCreate(BaseModel):
    product_id: str
    quantity: int

class BillCreate(BaseModel):
    customer: CustomerCreate
    items: List[BillItemCreate]

class BillResponse(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    total_amount: float
    total_tax: float
    timestamp: datetime
    items: List[Dict[str, Any]]

# Dependency to get services
def get_services():
    return {
        'db': db_manager,
        'billing': billing_service,
        'inventory': inventory_service
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Product endpoints
@app.get("/products", response_model=List[Dict[str, Any]])
async def get_products(services: Dict = Depends(get_services)):
    """Get all products"""
    try:
        products = services['db'].load_products()
        return [product.__dict__ for product in products.values()]
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(product_id: str, services: Dict = Depends(get_services)):
    """Get a specific product"""
    try:
        product = services['db'].get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product.__dict__
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products")
async def create_product(product: ProductCreate, services: Dict = Depends(get_services)):
    """Create a new product"""
    try:
        import uuid
        product_id = str(uuid.uuid4())
        
        new_product = Product(
            id=product_id,
            name=product.name,
            category=product.category,
            price=product.price,
            quantity=product.quantity,
            min_stock_level=product.min_stock_level,
            tax_rate=product.tax_rate
        )
        
        services['db'].add_product(new_product)
        return {"message": "Product created successfully", "product_id": product_id}
        
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{product_id}")
async def update_product(product_id: str, product_update: ProductUpdate, services: Dict = Depends(get_services)):
    """Update a product"""
    try:
        product = services['db'].get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update fields if provided
        if product_update.name is not None:
            product.name = product_update.name
        if product_update.category is not None:
            product.category = product_update.category
        if product_update.price is not None:
            product.price = product_update.price
        if product_update.quantity is not None:
            product.quantity = product_update.quantity
        if product_update.min_stock_level is not None:
            product.min_stock_level = product_update.min_stock_level
        if product_update.tax_rate is not None:
            product.tax_rate = product_update.tax_rate
        
        services['db'].update_product(product)
        return {"message": "Product updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/products/{product_id}")
async def delete_product(product_id: str, services: Dict = Depends(get_services)):
    """Delete a product"""
    try:
        product = services['db'].get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        services['db'].delete_product(product_id)
        return {"message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Bill endpoints
@app.get("/bills", response_model=List[BillResponse])
async def get_bills(services: Dict = Depends(get_services)):
    """Get all bills"""
    try:
        bills = services['db'].load_bills()
        result = []
        
        for bill in bills:
            bill_data = {
                "id": bill.id,
                "customer_name": bill.customer.name,
                "customer_phone": bill.customer.phone,
                "total_amount": bill.total_amount,
                "total_tax": bill.total_tax,
                "timestamp": bill.created_at,
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "total_price": item.total_price,
                        "tax_amount": item.tax_amount
                    }
                    for item in bill.items
                ]
            }
            result.append(bill_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting bills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bills")
async def create_bill(bill_data: BillCreate, services: Dict = Depends(get_services)):
    """Create a new bill"""
    try:
        # Prepare customer info
        customer_info = {
            "name": bill_data.customer.name,
            "phone": bill_data.customer.phone,
            "email": bill_data.customer.email
        }
        
        # Prepare items
        items_purchased = {item.product_id: item.quantity for item in bill_data.items}
        
        # Create bill
        bill = services['billing'].create_bill(customer_info, items_purchased)
        
        if not bill:
            raise HTTPException(status_code=400, detail="Failed to create bill")
        
        return {
            "message": "Bill created successfully",
            "bill_id": bill.id,
            "total_amount": bill.total_amount
        }
        
    except Exception as e:
        logger.error(f"Error creating bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bills/{bill_id}")
async def get_bill(bill_id: str, services: Dict = Depends(get_services)):
    """Get a specific bill"""
    try:
        bill = services['billing'].get_bill_details(bill_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        return {
            "id": bill.id,
            "customer_name": bill.customer_name,
            "customer_phone": bill.customer_phone,
            "total_amount": bill.total_amount,
            "total_tax": bill.total_tax,
            "timestamp": bill.timestamp,
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price,
                    "tax_amount": item.tax_amount
                }
                for item in bill.items
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bill {bill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Inventory endpoints
@app.get("/inventory/summary")
async def get_inventory_summary(services: Dict = Depends(get_services)):
    """Get inventory summary"""
    try:
        summary = services['inventory'].get_inventory_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting inventory summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inventory/low-stock")
async def get_low_stock_products(services: Dict = Depends(get_services)):
    """Get products with low stock"""
    try:
        low_stock_products = services['inventory'].get_low_stock_products()
        return [product.__dict__ for product in low_stock_products]
    except Exception as e:
        logger.error(f"Error getting low stock products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inventory/check-alerts")
async def check_inventory_alerts(background_tasks: BackgroundTasks, services: Dict = Depends(get_services)):
    """Check and send inventory alerts"""
    try:
        alerts = services['inventory'].check_stock_levels()
        if alerts:
            background_tasks.add_task(services['inventory'].send_low_stock_alerts, alerts)
        
        return {
            "message": f"Checked {len(alerts)} low stock items",
            "alerts_processed": len(alerts)
        }
    except Exception as e:
        logger.error(f"Error checking inventory alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI/ML endpoints
@app.get("/ai/demand-forecast/{product_name}")
async def get_demand_forecast(product_name: str, days: int = 7, services: Dict = Depends(get_services)):
    """Get AI-powered demand forecast for a product"""
    try:
        forecast = services['ai'].predict_demand(product_name, days)
        return forecast
    except Exception as e:
        logger.error(f"Error getting demand forecast for {product_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/reorder-suggestions")
async def get_reorder_suggestions(services: Dict = Depends(get_services)):
    """Get AI-powered reorder suggestions"""
    try:
        suggestions = services['ai'].get_smart_reorder_suggestions()
        return suggestions
    except Exception as e:
        logger.error(f"Error getting reorder suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/customer-insights")
async def get_customer_insights(services: Dict = Depends(get_services)):
    """Get AI-powered customer insights"""
    try:
        insights = services['ai'].get_customer_insights()
        return insights
    except Exception as e:
        logger.error(f"Error getting customer insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/revenue-forecast")
async def get_revenue_forecast(days: int = 30, services: Dict = Depends(get_services)):
    """Get AI-powered revenue forecast"""
    try:
        forecast = services['ai'].get_revenue_forecast(days)
        return forecast
    except Exception as e:
        logger.error(f"Error getting revenue forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/pricing-suggestions")
async def get_pricing_suggestions(services: Dict = Depends(get_services)):
    """Get AI-powered pricing suggestions"""
    try:
        suggestions = services['ai'].get_optimal_pricing_suggestions()
        return suggestions
    except Exception as e:
        logger.error(f"Error getting pricing suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/anomalies")
async def get_sales_anomalies(services: Dict = Depends(get_services)):
    """Get detected sales anomalies"""
    try:
        anomalies = services['ai'].detect_sales_anomalies()
        return anomalies
    except Exception as e:
        logger.error(f"Error getting sales anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/summary")
async def get_ai_summary(services: Dict = Depends(get_services)):
    """Get comprehensive AI analysis summary"""
    try:
        summary = services['ai'].get_ai_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting AI summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/analytics/sales-summary")
async def get_sales_summary(days: int = 30, services: Dict = Depends(get_services)):
    """Get sales summary for specified period"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        bills = services['db'].load_bills()
        period_bills = [bill for bill in bills if start_date <= bill.created_at <= end_date]
        
        total_sales = sum(bill.total_amount for bill in period_bills)
        total_bills = len(period_bills)
        avg_bill_value = total_sales / total_bills if total_bills > 0 else 0
        
        # Top products
        product_sales = {}
        for bill in period_bills:
            for item in bill.items:
                if item.product_name not in product_sales:
                    product_sales[item.product_name] = {'quantity': 0, 'revenue': 0}
                product_sales[item.product_name]['quantity'] += item.quantity
                product_sales[item.product_name]['revenue'] += item.total_price
        
        top_products = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]
        
        return {
            "period_days": days,
            "total_sales": round(total_sales, 2),
            "total_bills": total_bills,
            "average_bill_value": round(avg_bill_value, 2),
            "top_products": [
                {"product": name, "quantity": data['quantity'], "revenue": round(data['revenue'], 2)}
                for name, data in top_products
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sales summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Barcode endpoints
@app.get("/barcode/{barcode}")
async def lookup_barcode(barcode: str, services: Dict = Depends(get_services)):
    """Lookup product by barcode"""
    try:
        # This would integrate with the barcode scanner
        # For now, return a mock response
        return {
            "barcode": barcode,
            "found": False,
            "message": "Barcode lookup not implemented in API"
        }
    except Exception as e:
        logger.error(f"Error looking up barcode {barcode}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
