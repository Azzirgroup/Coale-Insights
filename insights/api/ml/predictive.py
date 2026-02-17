# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Predictive Intelligence API Endpoints
"""

import frappe
from typing import Dict, Any, List
from insights.api.response import success, error


@frappe.whitelist()
def generate_comprehensive_forecasts(domain: str = "all", forecast_horizon: int = 12, include_scenarios: bool = False) -> Dict[str, Any]:
    """Generate comprehensive forecasts"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        result = model.generate_comprehensive_forecasts(domain, forecast_horizon, include_scenarios)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def detect_anomalies_and_risks(domain: str = "all", sensitivity: str = "medium") -> Dict[str, Any]:
    """Detect anomalies and risks"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        result = model.detect_anomalies_and_risks(domain, sensitivity)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def analyze_predictive_patterns(lookback_months: int = 24, include_correlations: bool = True) -> Dict[str, Any]:
    """Analyze predictive patterns"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        result = model.analyze_predictive_patterns(lookback_months, include_correlations)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_real_time_predictions(metrics: List[str] = None, confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """Get real-time predictions"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        result = model.get_real_time_predictions(metrics, confidence_threshold)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def optimize_prediction_models(domain: str = "all", optimization_metric: str = "rmse") -> Dict[str, Any]:
    """Optimize prediction models"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        result = model.optimize_prediction_models(domain, optimization_metric)
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_predictive_insights(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get predictive insights"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        forecasts = model.generate_comprehensive_forecasts("all", 12, False)
        return success({"query": query, "context": context, "insights": forecasts})
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_risk_assessment(domain: str = "all", include_forecasts: bool = True, include_anomalies: bool = True) -> Dict[str, Any]:
    """Get risk assessment"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        result = model.detect_anomalies_and_risks(domain, "medium")
        return success(result)
    except Exception as e:
        return error(str(e))


@frappe.whitelist()
def get_domain_comparison(domains: List[str], analysis_type: str = "forecasts", horizon: int = 12) -> Dict[str, Any]:
    """Get domain comparison"""
    try:
        from insights.ml.advanced_predictive_analytics import AdvancedPredictiveAnalyticsEngine
        model = AdvancedPredictiveAnalyticsEngine()
        results = {}
        for domain in (domains or []):
            try:
                results[domain] = model.generate_comprehensive_forecasts(domain, horizon, False)
            except Exception:
                results[domain] = {"status": "error"}
        return success({"domains": results, "analysis_type": analysis_type})
    except Exception as e:
        return error(str(e))
