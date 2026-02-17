# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
HR Intelligence API Endpoints
"""

import frappe
from typing import Dict, Any
from insights.api.response import success, error


@frappe.whitelist()
def get_hr_overview(period: str = "YTD") -> Dict[str, Any]:
    """Get HR overview"""
    try:
        from insights.ml.hr_intelligence import HRIntelligence
        model = HRIntelligence()
        result = model.get_hr_overview(period)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_headcount_analytics(period: str = "YTD") -> Dict[str, Any]:
    """Get headcount analytics"""
    try:
        from insights.ml.hr_intelligence import get_headcount_analytics as _get_headcount
        result = _get_headcount(period)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_attrition_analytics(period: str = "YTD") -> Dict[str, Any]:
    """Get attrition analytics"""
    try:
        from insights.ml.hr_intelligence import get_attrition_prediction
        result = get_attrition_prediction()
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_payroll_analytics(period: str = "YTD") -> Dict[str, Any]:
    """Get payroll analytics"""
    try:
        from insights.ml.hr_intelligence import HRIntelligence
        model = HRIntelligence()
        overview = model.get_hr_overview(period)
        payroll = overview.get("payroll", overview)
        return success(payroll)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_workforce_planning() -> Dict[str, Any]:
    """Get workforce planning insights"""
    try:
        from insights.ml.hr_intelligence import HRIntelligence
        model = HRIntelligence()
        overview = model.get_hr_overview("YTD")
        planning = overview.get("workforce_planning", overview.get("predictions", {}))
        return success(planning)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_hr_insights(query: str, complexity: str = "Medium") -> Dict[str, Any]:
    """Get HR insights based on query"""
    try:
        from insights.ml.hr_intelligence import HRIntelligence
        model = HRIntelligence()
        result = model.get_hr_overview("YTD")
        return success({"query": query, "complexity": complexity, "insights": result})
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_talent_analytics(focus_area: str = "retention") -> Dict[str, Any]:
    """Get talent analytics"""
    try:
        from insights.ml.hr_intelligence import get_hr_recommendations
        result = get_hr_recommendations()
        return success({"focus_area": focus_area, "analytics": result})
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def analyze_hr_query(query: str) -> Dict[str, Any]:
    """Analyze HR query"""
    try:
        from insights.ml.hr_intelligence import HRIntelligence
        model = HRIntelligence()
        result = model.get_hr_overview("YTD")
        return success({"query": query, "analysis": result})
    except Exception as e:
        return error(str(e))
