"""
ai_features.py
Minimal compatibility stub kept for imports. This file intentionally provides
no-op methods and minimal structures so the rest of the application can run
without the original heavy AI implementation or extra dependencies.
"""
from typing import Dict, Any


class AIFeatures:
    def __init__(self, db_manager=None):
        self.db = db_manager

    def load_sales_history(self):
        return []

    def get_ai_summary(self) -> Dict[str, Any]:
        return {"note": "AI features are disabled in this build."}

    def predict_demand(self, product_name: str, days: int = 7) -> Dict[str, Any]:
        return {"predicted_demand": 0, "confidence": "n/a"}

    def get_smart_reorder_suggestions(self):
        return []

    def get_customer_insights(self):
        return {}

    def get_revenue_forecast(self, days: int = 30):
        return {"predicted": 0}

