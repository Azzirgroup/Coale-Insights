# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Manufacturing Intelligence API Endpoints
"""

import frappe
from typing import Dict, Any
from insights.api.response import success, error


@frappe.whitelist()
def get_manufacturing_overview(period: str = "YTD") -> Dict[str, Any]:
    """Get manufacturing overview"""
    try:
        from insights.ml.manufacturing_intelligence import (
            get_manufacturing_overview as _get_manufacturing_overview,
        )

        result = _get_manufacturing_overview(period=period)
        return success(result) if isinstance(result, dict) and "status" not in result else result
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_oee_analysis(period: str = "YTD") -> Dict[str, Any]:
    """Get OEE analysis"""
    try:
        from insights.ml.manufacturing_intelligence import (
            get_oee_analysis as _get_oee_analysis,
        )

        result = _get_oee_analysis(period=period)
        return success(result) if isinstance(result, dict) and "status" not in result else result
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_capacity_analysis() -> Dict[str, Any]:
    """Get capacity analysis"""
    try:
        from insights.ml.manufacturing_intelligence import (
            get_capacity_analysis as _get_capacity_analysis,
        )

        result = _get_capacity_analysis()
        return success(result) if isinstance(result, dict) and "status" not in result else result
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_production_forecast() -> Dict[str, Any]:
    """Get production forecast"""
    try:
        from insights.ml.manufacturing_intelligence import (
            get_production_forecast as _get_production_forecast,
        )

        result = _get_production_forecast()
        return success(result) if isinstance(result, dict) and "status" not in result else result
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_manufacturing_recommendations() -> Dict[str, Any]:
    """Get manufacturing recommendations"""
    try:
        from insights.ml.manufacturing_intelligence import (
            get_manufacturing_recommendations as _get_manufacturing_recommendations,
        )

        result = _get_manufacturing_recommendations()
        return success(result) if isinstance(result, dict) and "status" not in result else result
    except Exception as e:
        return error(str(e))
