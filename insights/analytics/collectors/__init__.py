# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Data Collectors for ERPNext Modules
Aggregates data from various ERPNext modules for AI analysis
"""

import frappe
from frappe import _
from frappe.utils import (
    nowdate, add_days, add_months, getdate, flt, cint,
    get_first_day, get_last_day, date_diff
)
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class BaseCollector:
    """Base class for data collectors"""

    def __init__(self, filters: Optional[Dict] = None):
        self.filters = filters or {}
        self.company = (filters.get("company") if filters else None) or frappe.defaults.get_user_default("Company")
        self.from_date = filters.get("from_date") if filters else add_months(nowdate(), -12)
        self.to_date = filters.get("to_date") if filters else nowdate()

    def collect(self) -> Dict[str, Any]:
        """Override in subclass"""
        raise NotImplementedError


# Import all collector classes for re-export
from .financial import FinancialDataCollector
from .sales import SalesDataCollector
from .procurement import ProcurementDataCollector
from .inventory import InventoryDataCollector
from .production import ProductionDataCollector
from .customer import CustomerDataCollector
from .hr import HRDataCollector


# Factory function to get collector
def get_collector(collector_type: str, filters: Optional[Dict] = None) -> BaseCollector:
    """Get data collector by type"""
    collectors = {
        "financial": FinancialDataCollector,
        "sales": SalesDataCollector,
        "procurement": ProcurementDataCollector,
        "inventory": InventoryDataCollector,
        "production": ProductionDataCollector,
        "customer": CustomerDataCollector,
        "hr": HRDataCollector
    }

    collector_class = collectors.get(collector_type)
    if not collector_class:
        raise ValueError(f"Unknown collector type: {collector_type}")

    return collector_class(filters)


# API endpoints
@frappe.whitelist()
def get_analytics_data(analytics_type: str, filters: str = None) -> Dict[str, Any]:
    """
    Get analytics data for a specific type

    Args:
        analytics_type: Type of analytics (financial, sales, etc.)
        filters: JSON string of filters

    Returns:
        Collected data
    """
    filter_dict = {}
    if filters:
        try:
            filter_dict = frappe.parse_json(filters)
        except:
            pass

    collector = get_collector(analytics_type, filter_dict)
    return collector.collect()


@frappe.whitelist()
def get_all_analytics_data(filters: str = None) -> Dict[str, Any]:
    """
    Get all analytics data for all types

    Args:
        filters: JSON string of filters

    Returns:
        All collected data by type
    """
    filter_dict = {}
    if filters:
        try:
            filter_dict = frappe.parse_json(filters)
        except:
            pass

    result = {}
    for analytics_type in ["financial", "sales", "procurement", "inventory", "production", "customer", "hr"]:
        try:
            collector = get_collector(analytics_type, filter_dict)
            result[analytics_type] = collector.collect()
        except Exception as e:
            frappe.log_error(f"Error collecting {analytics_type} data: {str(e)}", "Analytics Collector")
            result[analytics_type] = {"error": str(e)}

    return result


# Ensure all public names are available for backward-compatible imports
__all__ = [
    "BaseCollector",
    "FinancialDataCollector",
    "SalesDataCollector",
    "ProcurementDataCollector",
    "InventoryDataCollector",
    "ProductionDataCollector",
    "CustomerDataCollector",
    "HRDataCollector",
    "get_collector",
    "get_analytics_data",
    "get_all_analytics_data",
]
