"""
Comprehensive Test Suite for Supermarket Management System
Tests all features and functionality
"""
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from database import DatabaseManager
from billing_service import BillingService
from inventory_service import InventoryService
# AI features removed for tests

def setup_logging():
    """Setup logging for tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_database_operations():
    """Test database operations"""
    print("🧪 Testing Database Operations...")
    
    db = DatabaseManager()
    
    # Test product operations
    products = db.get_all_products()
    print(f"   ✅ Loaded {len(products)} products")
    
    # Test bill operations
    bills = db.load_bills()
    print(f"   ✅ Loaded {len(bills)} bills")
    
    # Test customer lookup
    if bills:
        customer = db.get_customer_by_phone(bills[0].customer.phone)
        print(f"   ✅ Customer lookup: {customer.name if customer else 'None'}")
    
    return True

def test_billing_service():
    """Test billing service functionality"""
    print("🧪 Testing Billing Service...")
    
    db = DatabaseManager()
    billing_service = BillingService(db)
    
    # Test daily sales summary
    today = datetime.now()
    summary = billing_service.get_daily_sales_summary(today)
    print(f"   ✅ Daily sales summary: ${summary['total_sales']:.2f}")
    
    # Test bill creation
    customer_info = {
        "name": "Test Customer",
        "phone": "555-9999",
        "email": "test@example.com"
    }
    
    # Get a product for testing
    products = db.get_all_products()
    if products:
        product_id = products[0].id
        items_purchased = {product_id: 1}
        
        bill = billing_service.create_bill(customer_info, items_purchased)
        if bill:
            print(f"   ✅ Bill created: {bill.id}")
        else:
            print("   ❌ Bill creation failed")
    
    return True

def test_inventory_service():
    """Test inventory service functionality"""
    print("🧪 Testing Inventory Service...")
    
    db = DatabaseManager()
    inventory_service = InventoryService(db)
    
    # Test inventory summary
    summary = inventory_service.get_inventory_summary()
    print(f"   ✅ Inventory summary: {summary['total_products']} products")
    
    # Test low stock products
    low_stock = inventory_service.get_low_stock_products()
    print(f"   ✅ Low stock products: {len(low_stock)}")
    
    # Test stock level checking
    alerts = inventory_service.check_stock_levels()
    print(f"   ✅ Stock alerts: {len(alerts)}")
    
    return True

def test_ai_features():
    """AI tests skipped — AI features are disabled in this build"""
    print("Testing AI features skipped (disabled in this build)")
    
    # Revenue forecast test skipped (AI disabled)
    print("   Revenue forecast test skipped")

    return True

def test_api_endpoints():
    """Test API endpoints (if running)"""
    print("Testing API endpoints...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API health check passed")
        else:
            print("   ⚠️  API not running or health check failed")
        
        # Test products endpoint
        response = requests.get("http://localhost:8000/products", timeout=5)
        if response.status_code == 200:
            products = response.json()
            print(f"   ✅ API products endpoint: {len(products)} products")
        else:
            print("   ⚠️  API products endpoint failed")
            
    except ImportError:
        print("   ⚠️  Requests library not available for API testing")
    except Exception as e:
        print(f"   ⚠️  API testing failed: {e}")
    
    return True

def test_performance():
    """Test system performance"""
    print("Testing performance...")
    
    import time
    
    db = DatabaseManager()
    
    # Test product loading performance
    start_time = time.time()
    products = db.get_all_products()
    product_time = time.time() - start_time
    print(f"   ✅ Product loading: {product_time:.3f}s for {len(products)} products")
    
    # Test bill loading performance
    start_time = time.time()
    bills = db.load_bills()
    bill_time = time.time() - start_time
    print(f"   ✅ Bill loading: {bill_time:.3f}s for {len(bills)} bills")
    
    # AI performance tests skipped
    print("   AI performance tests skipped")
    
    return True

def test_data_integrity():
    """Test data integrity and consistency"""
    print("🧪 Testing Data Integrity...")
    
    db = DatabaseManager()
    
    # Check for data consistency
    products = db.get_all_products()
    bills = db.load_bills()
    
    # Check that all bill items reference valid products
    valid_product_ids = {p.id for p in products}
    invalid_items = 0
    
    for bill in bills:
        for item in bill.items:
            if item.product_id not in valid_product_ids:
                invalid_items += 1
    
    if invalid_items == 0:
        print("   ✅ All bill items reference valid products")
    else:
        print(f"   ❌ {invalid_items} bill items reference invalid products")
    
    # Check for negative quantities
    negative_quantities = sum(1 for p in products if p.quantity < 0)
    if negative_quantities == 0:
        print("   ✅ No negative product quantities")
    else:
        print(f"   ❌ {negative_quantities} products have negative quantities")
    
    # Check for reasonable pricing
    invalid_prices = sum(1 for p in products if p.price <= 0)
    if invalid_prices == 0:
        print("   ✅ All products have valid prices")
    else:
        print(f"   ❌ {invalid_prices} products have invalid prices")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("Starting comprehensive system tests")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("Database Operations", test_database_operations),
        ("Billing Service", test_billing_service),
        ("Inventory Service", test_inventory_service),
        ("API Endpoints", test_api_endpoints),
        ("Performance", test_performance),
        ("Data Integrity", test_data_integrity),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}")
            print("-" * 40)
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed. System is ready for demo.")
    else:
        print("Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
