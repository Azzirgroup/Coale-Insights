# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Base ML Engine for Frappe Insights
Provides common utilities and base classes for ML models
"""

import frappe
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod


class BaseMLModel(ABC):
    """Base class for all ML models"""
    
    def __init__(self):
        self.model_name = self.__class__.__name__
        self.last_trained = None
        self.model_version = "1.0"
        
    @abstractmethod
    def train(self) -> Dict[str, Any]:
        """Train the model"""
        pass
    
    @abstractmethod
    def predict(self, data: Any) -> Dict[str, Any]:
        """Make predictions"""
        pass
    
    def get_training_data(self, query: str) -> pd.DataFrame:
        """Execute SQL and return as DataFrame"""
        result = frappe.db.sql(query, as_dict=True)
        # Convert frappe._dict objects to regular dicts for pandas compatibility
        if result:
            result = [dict(row) for row in result]
        return pd.DataFrame(result)
    
    def save_results(self, doctype: str, results: List[Dict]):
        """Save ML results to database"""
        for result in results:
            try:
                if frappe.db.exists(doctype, result.get("name")):
                    doc = frappe.get_doc(doctype, result.get("name"))
                    doc.update(result)
                    doc.save(ignore_permissions=True)
                else:
                    doc = frappe.get_doc({"doctype": doctype, **result})
                    doc.insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Error saving ML result: {str(e)}", self.model_name)
        frappe.db.commit()
    
    def log_training(self, metrics: Dict[str, Any]):
        """Log training run - logs to frappe error log if ML Training Log doctype doesn't exist"""
        try:
            # Check if ML Training Log doctype exists
            if frappe.db.exists("DocType", "ML Training Log"):
                frappe.get_doc({
                    "doctype": "ML Training Log",
                    "model_name": self.model_name,
                    "model_version": self.model_version,
                    "training_date": frappe.utils.now(),
                    "metrics": json.dumps(metrics),
                    "status": "Completed"
                }).insert(ignore_permissions=True)
                frappe.db.commit()
            else:
                # Log to system log instead
                frappe.logger().info(f"ML Training: {self.model_name} v{self.model_version} - {json.dumps(metrics)}")
        except Exception as e:
            # Don't fail training if logging fails
            frappe.logger().warning(f"Failed to log ML training: {str(e)}")
    
    def get_cached_results(self, cache_key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Get cached results if still valid"""
        cached = frappe.cache.get_value(cache_key)
        if cached:
            cached_time = cached.get("cached_at")
            if cached_time:
                age = datetime.now() - datetime.fromisoformat(cached_time)
                if age.total_seconds() < max_age_hours * 3600:
                    return cached.get("data")
        return None
    
    def cache_results(self, cache_key: str, data: Dict, expires_in_hours: int = 24):
        """Cache results"""
        frappe.cache.set_value(
            cache_key,
            {
                "data": data,
                "cached_at": datetime.now().isoformat()
            },
            expires_in_sec=expires_in_hours * 3600
        )


def ensure_dependencies():
    """Check and report on ML dependencies"""
    dependencies = {
        "pandas": False,
        "numpy": False,
        "scikit-learn": False,
        "prophet": False,
        "xgboost": False
    }
    
    try:
        import pandas
        dependencies["pandas"] = True
    except ImportError:
        pass
    
    try:
        import numpy
        dependencies["numpy"] = True
    except ImportError:
        pass
    
    try:
        import sklearn
        dependencies["scikit-learn"] = True
    except ImportError:
        pass
    
    try:
        from prophet import Prophet
        dependencies["prophet"] = True
    except ImportError:
        pass
    
    try:
        import xgboost
        dependencies["xgboost"] = True
    except ImportError:
        pass
    
    return dependencies


def get_date_range(months_back: int = 12) -> Tuple[str, str]:
    """Get date range for queries"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 30)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
