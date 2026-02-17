# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Strategic Finance Intelligence API Endpoints
"""

import frappe
from typing import Dict, Any
from insights.api.response import success, error


@frappe.whitelist()
def strategic_finance_intelligence(refresh: bool = False, date_filter: str = "12m") -> Dict[str, Any]:
    """Get strategic finance intelligence analysis"""
    try:
        from insights.ml.strategic_finance_intelligence import run_strategic_finance_intelligence
        return run_strategic_finance_intelligence(refresh=refresh)
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_budget_variance_overview(company: str = None, fiscal_year: str = None) -> Dict[str, Any]:
    """Get budget variance overview"""
    try:
        from insights.ml.budget_variance_intelligence import BudgetVarianceIntelligence

        model = BudgetVarianceIntelligence()
        result = model.get_budget_variance_overview()
        return success(result)
    except Exception as e:
        return error(str(e))
