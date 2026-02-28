# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Base Data Collector
Abstract base class for ERPNext module-specific data collectors.
"""

from typing import Dict, Any, Optional

import frappe
from frappe.utils import nowdate, add_months


class BaseCollector:
    """Base class for data collectors"""

    def __init__(self, filters: Optional[Dict] = None):
        self.filters = filters or {}
        self.company = (
            (filters.get("company") if filters else None)
            or frappe.defaults.get_user_default("Company")
        )
        self.from_date = (
            filters.get("from_date") if filters else add_months(nowdate(), -12)
        )
        self.to_date = filters.get("to_date") if filters else nowdate()

    def collect(self) -> Dict[str, Any]:
        """Override in subclass to return collected data."""
        raise NotImplementedError
