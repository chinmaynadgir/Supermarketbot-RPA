"""
Main entry point for the improved supermarket system
"""
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_gui import EnhancedSupermarketGUI
from database import DatabaseManager
from billing_service import BillingService
from inventory_service import InventoryService
import tkinter as tk

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('supermarket.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to run the application"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting AI-Powered Supermarket Management System v2.0")
        
        # Initialize services
        db_manager = DatabaseManager()
        billing_service = BillingService(db_manager)
        inventory_service = InventoryService(db_manager, {})
        
        # Create and run the GUI application
        root = tk.Tk()
        app = EnhancedSupermarketGUI(root, db_manager, billing_service, inventory_service)
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
