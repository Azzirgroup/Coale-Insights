# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
ESG Intelligence API Endpoints
"""

import frappe
from typing import Dict, Any
from insights.api.response import success, error


@frappe.whitelist()
def get_esg_overview(period: str = "YTD") -> Dict[str, Any]:
    """Get ESG intelligence overview"""
    try:
        from insights.ml.esg_intelligence import ESGIntelligence
        model = ESGIntelligence()
        result = model.get_esg_overview()
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def export_esg_report(format: str = "pdf") -> Dict[str, Any]:
    """Export ESG report"""
    try:
        from insights.ml.esg_intelligence import ESGIntelligence
        model = ESGIntelligence()
        result = model.export_esg_report(report_format=format)
        return success(result)
    except Exception as e:
        return error(str(e))
