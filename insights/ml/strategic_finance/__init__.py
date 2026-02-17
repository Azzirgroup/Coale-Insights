# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Strategic Finance Intelligence Package
Forward-looking financial planning and scenario analysis for:
- Executive KPI dashboard with trends
- Cash flow forecasting and runway analysis
- Capital planning and CAPEX tracking
- Working capital optimization
- Financial ratio trends and benchmarks
- Scenario analysis (sensitivity + Monte Carlo)
- Period-over-period comparison
- Budget management (placeholder for future)
"""

import frappe
from datetime import datetime
from typing import Dict, Any

from insights.ml.base import BaseMLModel

# Import submodule functions
from .data import (
    sanitize_for_json,
    get_current_fiscal_year,
    get_cash_balance,
    get_expense_breakdown,
    analyze_budget,
)
from .summary import (
    calculate_executive_summary,
)
from .forecast import (
    forecast_cash_flow,
    generate_thirteen_week_forecast,
)
from .analysis import (
    analyze_capital_planning,
    analyze_working_capital,
    calculate_ratio_trends,
)
from .scenarios import (
    generate_scenario_analysis,
    compare_periods,
)


class StrategicFinanceIntelligence(BaseMLModel):
    """
    Strategic Finance Intelligence Model

    Differentiates from Financial Intelligence by focusing on:
    - FORWARD-LOOKING analytics (forecasts, projections, scenarios)
    - STRATEGIC planning (capital allocation, runway, what-if)
    - DECISION SUPPORT (scenario modeling, sensitivity analysis)

    While Financial Intelligence focuses on:
    - HISTORICAL reporting (P&L, cash flow, ratios)
    - COMPLIANCE (tax, receivables, payables)
    - OPERATIONAL metrics (DSO, DPO, aging)
    """

    CORPORATE_TAX_RATE = 30.0  # Kenya corporate tax rate

    def __init__(self):
        super().__init__()
        self.model_name = "StrategicFinanceIntelligence"
        self.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
        self.base_currency = frappe.db.get_value("Company", self.company, "default_currency") or "KES"
        self.fiscal_year = get_current_fiscal_year(self)

    def train(self) -> Dict[str, Any]:
        """Generate comprehensive strategic finance intelligence"""
        try:
            executive_summary = calculate_executive_summary(self)
            cash_forecast = forecast_cash_flow(self)
            thirteen_week_forecast = generate_thirteen_week_forecast(self)
            capital_planning = analyze_capital_planning(self)
            working_capital = analyze_working_capital(self)
            ratio_trends = calculate_ratio_trends(self)
            scenario_analysis = generate_scenario_analysis(self)
            period_comparison = compare_periods(self)
            budget_analysis = analyze_budget(self)
            expense_breakdown = get_expense_breakdown(self)

            result = {
                "status": "success",
                "generated_at": datetime.now().isoformat(),
                "company": self.company,
                "base_currency": self.base_currency,
                "fiscal_year": self.fiscal_year,
                "executive_summary": executive_summary,
                "cash_forecast": cash_forecast,
                "thirteen_week_forecast": thirteen_week_forecast,
                "capital_planning": capital_planning,
                "working_capital": working_capital,
                "ratio_trends": ratio_trends,
                "scenario_analysis": scenario_analysis,
                "period_comparison": period_comparison,
                "budget_analysis": budget_analysis,
                "expense_breakdown": expense_breakdown
            }

            self.cache_results("strategic_finance_intelligence", result)
            return result

        except Exception as e:
            frappe.log_error(f"Strategic Finance Intelligence failed: {str(e)}", "ML Strategic Finance")
            return {"status": "error", "message": str(e)}

    def predict(self) -> Dict[str, Any]:
        """Return cached results or generate new ones with daily auto-refresh"""
        cached = self.get_cached_results("strategic_finance_intelligence")

        if cached:
            # Check if cache is from today (daily auto-refresh)
            generated_at = cached.get("generated_at", "")
            if generated_at:
                try:
                    cache_date = datetime.fromisoformat(generated_at).date()
                    today = datetime.now().date()

                    # If cache is from a previous day, regenerate
                    if cache_date < today:
                        return self.train()
                except (ValueError, TypeError):
                    pass

            return cached

        return self.train()


def run_strategic_finance_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """Helper function to run strategic finance intelligence"""
    model = StrategicFinanceIntelligence()
    if refresh:
        result = model.train()
    else:
        result = model.predict()
    # Sanitize numpy types for JSON serialization
    return sanitize_for_json(result)
