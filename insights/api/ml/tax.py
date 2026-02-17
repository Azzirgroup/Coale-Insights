# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Tax Intelligence API Endpoints
"""

import frappe
from typing import Dict, Any
from insights.api.response import success, error


@frappe.whitelist()
def tax_intelligence(refresh: bool = False, date_filter: str = "12m") -> Dict[str, Any]:
    """Get tax intelligence analysis"""
    try:
        from insights.ml.tax_intelligence import run_tax_intelligence
        return run_tax_intelligence(refresh=refresh)
    except Exception as e:
        return {"status": "error", "message": str(e)}
