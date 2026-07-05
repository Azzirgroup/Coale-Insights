# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Sales Intelligence API Endpoints
"""

import frappe
from typing import Dict, Any, List
from insights.api.response import success, error


@frappe.whitelist()
def sales_forecast(periods: int = 30, refresh: bool = False) -> Dict[str, Any]:
    """Get sales forecast"""
    try:
        from insights.ml.sales_forecasting import SalesForecasting
        model = SalesForecasting()
        if not refresh:
            cached = model.get_cached_results("sales_forecast")
            if cached:
                return success(cached)
        result = model.train(periods=int(periods))
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_forecast_chart_data() -> Dict[str, Any]:
    """Get forecast data formatted for charts"""
    try:
        from insights.ml.sales_forecasting import SalesForecasting
        model = SalesForecasting()
        result = model.predict()
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def sales_intelligence(refresh: bool = False, date_filter: str = '12m') -> Dict[str, Any]:
    """Get comprehensive sales intelligence.

    Runs in a background job (returns {status: 'queued'} on a cache miss) so the
    heavy computation never times out the web worker. Poll sales_intelligence_status.
    """
    try:
        from insights.api.ml.async_runner import get_or_enqueue

        return get_or_enqueue(
            "sales_intelligence",
            "sales_intelligence",
            {"date_filter": date_filter},
            refresh=bool(refresh),
        )
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def sales_intelligence_status() -> Dict[str, Any]:
    """Get sales intelligence processing status"""
    try:
        from insights.api.ml.async_runner import job_status

        return job_status("sales_intelligence")
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def payment_mix() -> Dict[str, Any]:
    """Analyze payment method mix"""
    try:
        from insights.ml.sales_intelligence import SalesIntelligence
        model = SalesIntelligence()
        full_result = model.train()
        result = full_result.get("payment_mix", full_result)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def sales_rep_performance() -> Dict[str, Any]:
    """Get sales representative performance analysis"""
    try:
        from insights.ml.sales_intelligence import SalesIntelligence
        model = SalesIntelligence()
        full_result = model.train()
        result = full_result.get("sales_reps", full_result)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def revenue_breakdown() -> Dict[str, Any]:
    """Get revenue breakdown by various dimensions"""
    try:
        from insights.ml.sales_intelligence import SalesIntelligence
        model = SalesIntelligence()
        full_result = model.train()
        result = full_result.get("dimensions", full_result)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def margin_analysis() -> Dict[str, Any]:
    """Analyze profit margins"""
    try:
        from insights.ml.sales_intelligence import SalesIntelligence
        model = SalesIntelligence()
        full_result = model.train()
        result = full_result.get("margins", full_result)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def sales_comparisons() -> Dict[str, Any]:
    """Compare sales across periods and dimensions"""
    try:
        from insights.ml.sales_intelligence import SalesIntelligence
        model = SalesIntelligence()
        full_result = model.train()
        result = full_result.get("comparisons", full_result)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def train_forecast_models(model_type: str = 'all') -> Dict[str, Any]:
    """Train forecasting models"""
    try:
        from insights.ml.sales_forecasting import SalesForecasting
        model = SalesForecasting()
        result = model.train()
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_historical_and_forecast_by_dimension(dimension: str = 'product_group') -> Dict[str, Any]:
    """Get historical and forecast data by dimension"""
    try:
        from insights.ml.sales_forecasting import get_grouped_forecast
        result = get_grouped_forecast(group_by=dimension)
        return success(result)
    except Exception as e:
        return error(str(e))
