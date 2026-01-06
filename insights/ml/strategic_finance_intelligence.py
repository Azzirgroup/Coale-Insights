# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Strategic Finance Intelligence Model
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
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from insights.ml.base import BaseMLModel


def sanitize_for_json(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    else:
        return obj


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
        self.fiscal_year = self._get_current_fiscal_year()
    
    def _get_current_fiscal_year(self) -> Dict[str, Any]:
        """Get current fiscal year for the company"""
        today = datetime.now().date()
        fy = frappe.db.sql("""
            SELECT name, year_start_date, year_end_date
            FROM `tabFiscal Year`
            WHERE %s BETWEEN year_start_date AND year_end_date
            ORDER BY year_start_date DESC
            LIMIT 1
        """, (today,), as_dict=True)
        
        if fy:
            return {
                "name": fy[0].name,
                "start_date": str(fy[0].year_start_date),
                "end_date": str(fy[0].year_end_date)
            }
        
        # Default to calendar year if no fiscal year found
        return {
            "name": str(today.year),
            "start_date": f"{today.year}-01-01",
            "end_date": f"{today.year}-12-31"
        }
    
    def train(self) -> Dict[str, Any]:
        """Generate comprehensive strategic finance intelligence"""
        try:
            executive_summary = self._calculate_executive_summary()
            cash_forecast = self._forecast_cash_flow()
            thirteen_week_forecast = self._generate_thirteen_week_forecast()
            capital_planning = self._analyze_capital_planning()
            working_capital = self._analyze_working_capital()
            ratio_trends = self._calculate_ratio_trends()
            scenario_analysis = self._generate_scenario_analysis()
            period_comparison = self._compare_periods()
            budget_analysis = self._analyze_budget()  # Placeholder
            expense_breakdown = self._get_expense_breakdown()
            
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
    
    # =========================================================================
    # EXECUTIVE SUMMARY - C-Level KPIs
    # =========================================================================
    
    def _calculate_executive_summary(self) -> Dict[str, Any]:
        """Calculate executive-level KPIs and trends"""
        fy_start = self.fiscal_year["start_date"]
        today = datetime.now().strftime('%Y-%m-%d')
        
        # YTD Revenue
        ytd_revenue = frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(credit - debit)), 0) as amount
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.root_type = 'Income'
                AND gle.posting_date BETWEEN %s AND %s
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (fy_start, today, self.company), as_dict=True)[0].amount or 0
        
        # YTD Expenses
        ytd_expenses = frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(debit - credit)), 0) as amount
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.root_type = 'Expense'
                AND gle.posting_date BETWEEN %s AND %s
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (fy_start, today, self.company), as_dict=True)[0].amount or 0
        
        # YTD Net Income
        ytd_net_income = ytd_revenue - ytd_expenses
        net_margin = (ytd_net_income / ytd_revenue * 100) if ytd_revenue > 0 else 0
        
        # YTD Cost of Goods Sold (COGS) for Gross Margin calculation
        ytd_cogs = frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(debit - credit)), 0) as amount
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE (acc.account_type = 'Cost of Goods Sold'
                   OR acc.name LIKE '%%Cost of Goods%%'
                   OR acc.name LIKE '%%COGS%%')
                AND acc.root_type = 'Expense'
                AND gle.posting_date BETWEEN %s AND %s
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (fy_start, today, self.company), as_dict=True)[0].amount or 0
        
        # Gross Margin = (Revenue - COGS) / Revenue * 100
        # If no COGS accounts found, fall back to a reasonable estimate (70% of revenue)
        gross_profit = ytd_revenue - ytd_cogs if ytd_cogs > 0 else ytd_revenue * 0.7
        gross_margin = (gross_profit / ytd_revenue * 100) if ytd_revenue > 0 else 0
        
        # Prior Year Same Period for Growth
        prior_fy_start = (datetime.strptime(fy_start, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        prior_today = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        prior_revenue = frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(credit - debit)), 0) as amount
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.root_type = 'Income'
                AND gle.posting_date BETWEEN %s AND %s
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (prior_fy_start, prior_today, self.company), as_dict=True)[0].amount or 0
        
        revenue_growth = ((ytd_revenue - prior_revenue) / prior_revenue * 100) if prior_revenue > 0 else 0
        
        # Cash Position
        cash_balance = self._get_cash_balance()
        
        # Monthly Burn Rate (average of last 3 months expenses)
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        monthly_expenses = frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(debit - credit)), 0) / 3 as avg_monthly
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.root_type = 'Expense'
                AND gle.posting_date >= %s
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (three_months_ago, self.company), as_dict=True)[0].avg_monthly or 0
        
        # Cash Runway
        cash_runway_months = (cash_balance / monthly_expenses) if monthly_expenses > 0 else 999
        
        # Total Assets (from Asset doctype)
        total_assets = frappe.db.sql("""
            SELECT COALESCE(SUM(gross_purchase_amount), 0) as total
            FROM `tabAsset`
            WHERE company = %s
                AND docstatus = 1
                AND status NOT IN ('Sold', 'Scrapped')
        """, (self.company,), as_dict=True)[0].total or 0
        
        # Total Debt (Liabilities)
        total_liabilities = frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(credit - debit)), 0) as amount
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.root_type = 'Liability'
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (self.company,), as_dict=True)[0].amount or 0
        
        # Equity
        total_equity = frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(credit - debit)), 0) as amount
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.root_type = 'Equity'
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (self.company,), as_dict=True)[0].amount or 0
        
        # ROE and ROA
        roe = (ytd_net_income / total_equity * 100) if total_equity > 0 else 0
        roa = (ytd_net_income / total_assets * 100) if total_assets > 0 else 0
        
        # Debt to Equity
        debt_to_equity = (total_liabilities / total_equity) if total_equity > 0 else 0
        
        # Monthly trends (last 12 months)
        monthly_trends = self._get_monthly_financial_trends()
        
        # Calculate Health Scores
        health_scores = self._calculate_health_scores(
            net_margin=net_margin,
            roe=roe,
            roa=roa,
            debt_to_equity=debt_to_equity,
            cash_runway_months=cash_runway_months,
            revenue_growth=revenue_growth
        )
        
        # Generate Key Executive Insights
        key_insights = self._generate_key_insights(
            ytd_revenue=ytd_revenue,
            ytd_net_income=ytd_net_income,
            net_margin=net_margin,
            revenue_growth=revenue_growth,
            cash_runway_months=cash_runway_months,
            debt_to_equity=debt_to_equity,
            roe=roe,
            health_scores=health_scores
        )
        
        return {
            "ytd_revenue": ytd_revenue,
            "ytd_expenses": ytd_expenses,
            "ytd_cogs": ytd_cogs,
            "gross_profit": gross_profit,
            "gross_margin": round(gross_margin, 2),
            "ytd_net_income": ytd_net_income,
            "net_margin": round(net_margin, 2),
            "revenue_growth_yoy": round(revenue_growth, 2),
            "cash_balance": cash_balance,
            "cash_runway_months": round(cash_runway_months, 1),
            "monthly_burn_rate": monthly_expenses,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "roe": round(roe, 2),
            "roa": round(roa, 2),
            "debt_to_equity": round(debt_to_equity, 2),
            "monthly_trends": monthly_trends,
            "health_scores": health_scores,
            "key_insights": key_insights,
            "kpis": [
                {"label": "Total Revenue", "value": ytd_revenue, "format": "currency", "subtitle": "Year to Date", "trend": round(revenue_growth, 1)},
                {"label": "Net Profit", "value": ytd_net_income, "format": "currency", "subtitle": f"{net_margin:.1f}% margin"},
                {"label": "Gross Margin", "value": gross_margin, "format": "percent", "subtitle": "Revenue - COGS"},
                {"label": "Revenue Growth", "value": revenue_growth, "format": "percent", "subtitle": "YoY"},
                {"label": "Cash Position", "value": cash_balance, "format": "currency", "subtitle": f"{cash_runway_months:.0f} months runway"},
                {"label": "ROE", "value": roe, "format": "percent", "subtitle": "Return on Equity"}
            ]
        }
    
    def _get_cash_balance(self) -> float:
        """Get current cash and bank balance"""
        cash = frappe.db.sql("""
            SELECT COALESCE(SUM(debit - credit), 0) as balance
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.account_type IN ('Cash', 'Bank')
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (self.company,), as_dict=True)[0].balance or 0
        return cash
    
    def _calculate_health_scores(self, net_margin: float, roe: float, roa: float, 
                                  debt_to_equity: float, cash_runway_months: float,
                                  revenue_growth: float) -> Dict[str, Any]:
        """Calculate financial health scores (0-100) for liquidity, profitability, and efficiency"""
        
        # Liquidity Score (based on cash runway and debt ratio)
        liquidity_score = 0
        if cash_runway_months >= 12:
            liquidity_score = 90
        elif cash_runway_months >= 6:
            liquidity_score = 70
        elif cash_runway_months >= 3:
            liquidity_score = 50
        else:
            liquidity_score = 30
        
        # Adjust for debt level
        if debt_to_equity < 0.5:
            liquidity_score = min(100, liquidity_score + 10)
        elif debt_to_equity > 2:
            liquidity_score = max(0, liquidity_score - 20)
        
        liquidity_status = "Excellent" if liquidity_score >= 80 else "Good" if liquidity_score >= 60 else "Fair" if liquidity_score >= 40 else "Poor"
        
        # Profitability Score (based on net margin and ROE)
        profitability_score = 0
        if net_margin >= 20:
            profitability_score = 90
        elif net_margin >= 10:
            profitability_score = 70
        elif net_margin >= 5:
            profitability_score = 55
        elif net_margin > 0:
            profitability_score = 40
        else:
            profitability_score = 20
        
        # Boost for strong ROE
        if roe >= 15:
            profitability_score = min(100, profitability_score + 10)
        elif roe < 5:
            profitability_score = max(0, profitability_score - 10)
        
        profitability_status = "Excellent" if profitability_score >= 80 else "Good" if profitability_score >= 60 else "Fair" if profitability_score >= 40 else "Poor"
        
        # Efficiency Score (based on ROA and revenue growth)
        efficiency_score = 0
        if roa >= 10:
            efficiency_score = 85
        elif roa >= 5:
            efficiency_score = 65
        elif roa >= 2:
            efficiency_score = 50
        else:
            efficiency_score = 35
        
        # Boost for revenue growth
        if revenue_growth >= 20:
            efficiency_score = min(100, efficiency_score + 15)
        elif revenue_growth >= 10:
            efficiency_score = min(100, efficiency_score + 10)
        elif revenue_growth < 0:
            efficiency_score = max(0, efficiency_score - 10)
        
        efficiency_status = "Excellent" if efficiency_score >= 80 else "Good" if efficiency_score >= 60 else "Fair" if efficiency_score >= 40 else "Poor"
        
        return {
            "liquidity": round(liquidity_score),
            "liquidity_status": liquidity_status,
            "profitability": round(profitability_score),
            "profitability_status": profitability_status,
            "efficiency": round(efficiency_score),
            "efficiency_status": efficiency_status,
            "overall": round((liquidity_score + profitability_score + efficiency_score) / 3),
            "overall_status": "Excellent" if (liquidity_score + profitability_score + efficiency_score) / 3 >= 80 else "Good" if (liquidity_score + profitability_score + efficiency_score) / 3 >= 60 else "Fair"
        }
    
    def _generate_key_insights(self, ytd_revenue: float, ytd_net_income: float, 
                                net_margin: float, revenue_growth: float,
                                cash_runway_months: float, debt_to_equity: float,
                                roe: float, health_scores: Dict) -> List[Dict]:
        """Generate actionable executive insights based on financial metrics"""
        insights = []
        
        # Revenue performance insight
        if revenue_growth > 15:
            insights.append({
                "type": "success",
                "title": "Strong Revenue Growth",
                "description": f"Revenue is growing at {revenue_growth:.1f}% YoY, outpacing industry averages. Consider reinvesting in growth initiatives."
            })
        elif revenue_growth > 0:
            insights.append({
                "type": "info",
                "title": "Moderate Revenue Growth",
                "description": f"Revenue growth of {revenue_growth:.1f}% YoY is positive but below optimal targets. Review sales strategies for acceleration."
            })
        else:
            insights.append({
                "type": "danger",
                "title": "Revenue Declining",
                "description": f"Revenue has declined {abs(revenue_growth):.1f}% YoY. Immediate attention needed on sales pipeline and market positioning."
            })
        
        # Profitability insight
        if net_margin >= 15:
            insights.append({
                "type": "success",
                "title": "Excellent Profit Margins",
                "description": f"Net margin of {net_margin:.1f}% demonstrates strong operational efficiency and pricing power."
            })
        elif net_margin >= 5:
            insights.append({
                "type": "info",
                "title": "Healthy Profit Margins",
                "description": f"Net margin of {net_margin:.1f}% is acceptable. Look for cost optimization opportunities to improve profitability."
            })
        elif net_margin > 0:
            insights.append({
                "type": "warning",
                "title": "Thin Profit Margins",
                "description": f"Net margin of {net_margin:.1f}% is below target. Review expense structure and pricing strategy."
            })
        else:
            insights.append({
                "type": "danger",
                "title": "Operating at Loss",
                "description": f"Negative net margin of {net_margin:.1f}%. Urgent cost reduction and revenue improvement measures needed."
            })
        
        # Cash runway insight
        if cash_runway_months < 3:
            insights.append({
                "type": "danger",
                "title": "Critical Cash Position",
                "description": f"Only {cash_runway_months:.1f} months of cash runway remaining. Immediate action required on cash conservation or funding."
            })
        elif cash_runway_months < 6:
            insights.append({
                "type": "warning",
                "title": "Limited Cash Runway",
                "description": f"{cash_runway_months:.1f} months of cash runway. Begin planning for additional funding or cost reductions."
            })
        elif cash_runway_months >= 12:
            insights.append({
                "type": "success",
                "title": "Strong Cash Position",
                "description": f"{cash_runway_months:.1f}+ months of runway provides flexibility for strategic investments."
            })
        
        # Leverage insight
        if debt_to_equity > 2:
            insights.append({
                "type": "warning",
                "title": "High Leverage",
                "description": f"Debt-to-equity ratio of {debt_to_equity:.2f} indicates high leverage. Consider debt reduction strategies."
            })
        elif debt_to_equity < 0.3:
            insights.append({
                "type": "info",
                "title": "Conservative Capital Structure",
                "description": f"Low debt-to-equity of {debt_to_equity:.2f} may indicate opportunity for strategic debt financing."
            })
        
        # Overall health insight
        overall_score = health_scores.get('overall', 0)
        if overall_score >= 75:
            insights.append({
                "type": "success",
                "title": "Excellent Financial Health",
                "description": f"Overall financial health score of {overall_score}/100 indicates a strong position for growth."
            })
        elif overall_score < 50:
            insights.append({
                "type": "warning",
                "title": "Financial Health Needs Attention",
                "description": f"Overall score of {overall_score}/100 suggests focus needed on improving key financial metrics."
            })
        
        return insights[:5]  # Limit to top 5 insights
    
    def _get_monthly_financial_trends(self) -> List[Dict]:
        """Get monthly revenue/expense trends for last 12 months"""
        trends = frappe.db.sql("""
            SELECT 
                DATE_FORMAT(gle.posting_date, '%%Y-%%m') as period,
                SUM(CASE WHEN acc.root_type = 'Income' THEN ABS(credit - debit) ELSE 0 END) as revenue,
                SUM(CASE WHEN acc.root_type = 'Expense' THEN ABS(debit - credit) ELSE 0 END) as expenses
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.posting_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                AND gle.company = %s
                AND gle.is_cancelled = 0
                AND acc.root_type IN ('Income', 'Expense')
            GROUP BY DATE_FORMAT(gle.posting_date, '%%Y-%%m')
            ORDER BY period
        """, (self.company,), as_dict=True)
        
        result = []
        for t in trends:
            revenue = float(t.revenue or 0)
            expenses = float(t.expenses or 0)
            result.append({
                "period": t.period,
                "revenue": revenue,
                "expenses": expenses,
                "net_income": revenue - expenses,
                "margin": round((revenue - expenses) / revenue * 100, 1) if revenue > 0 else 0
            })
        return result
    
    def _get_expense_breakdown(self) -> List[Dict[str, Any]]:
        """Get expense breakdown by category for current fiscal year"""
        fy_start = self.fiscal_year["start_date"]
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get expense accounts with their totals
        expenses = frappe.db.sql("""
            SELECT 
                acc.account_name as category,
                acc.parent_account,
                COALESCE(SUM(ABS(gle.debit - gle.credit)), 0) as amount
            FROM `tabAccount` acc
            LEFT JOIN `tabGL Entry` gle ON gle.account = acc.name 
                AND gle.is_cancelled = 0
                AND gle.posting_date BETWEEN %s AND %s
            WHERE acc.root_type = 'Expense'
                AND acc.is_group = 0
                AND acc.company = %s
            GROUP BY acc.name
            HAVING amount > 0
            ORDER BY amount DESC
            LIMIT 10
        """, (fy_start, today, self.company), as_dict=True)
        
        # Calculate total and percentages
        total = sum(e.get('amount', 0) for e in expenses)
        
        result = []
        for exp in expenses:
            amount = float(exp.get('amount', 0))
            pct = round((amount / total * 100), 1) if total > 0 else 0
            result.append({
                "category": exp.get('category', 'Unknown'),
                "amount": amount,
                "percentage": pct
            })
        
        return result
    
    # =========================================================================
    # CASH FLOW FORECASTING - 90-Day Projections
    # =========================================================================
    
    def _forecast_cash_flow(self) -> Dict[str, Any]:
        """Generate 90-day cash flow forecast with scenarios"""
        current_cash = self._get_cash_balance()
        
        # Get historical daily cash flows (last 90 days)
        historical = frappe.db.sql("""
            SELECT 
                gle.posting_date as date,
                SUM(CASE WHEN acc.account_type IN ('Cash', 'Bank') THEN (debit - credit) ELSE 0 END) as net_flow
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.posting_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
                AND gle.company = %s
                AND gle.is_cancelled = 0
            GROUP BY gle.posting_date
            ORDER BY gle.posting_date
        """, (self.company,), as_dict=True)
        
        # Calculate average daily flow
        if historical:
            daily_flows = [float(h.net_flow or 0) for h in historical]
            avg_daily_flow = float(np.mean(daily_flows)) if daily_flows else 0
            std_daily_flow = float(np.std(daily_flows)) if len(daily_flows) > 1 else abs(avg_daily_flow) * 0.3
        else:
            avg_daily_flow = 0
            std_daily_flow = 0
        
        # Expected receivables (outstanding invoices)
        expected_inflows = frappe.db.sql("""
            SELECT 
                COALESCE(SUM(outstanding_amount), 0) as total,
                COUNT(*) as count
            FROM `tabSales Invoice`
            WHERE company = %s
                AND docstatus = 1
                AND outstanding_amount > 0
        """, (self.company,), as_dict=True)[0]
        
        # Expected payables (outstanding bills)
        expected_outflows = frappe.db.sql("""
            SELECT 
                COALESCE(SUM(outstanding_amount), 0) as total,
                COUNT(*) as count
            FROM `tabPurchase Invoice`
            WHERE company = %s
                AND docstatus = 1
                AND outstanding_amount > 0
        """, (self.company,), as_dict=True)[0]
        
        # Generate 90-day forecast
        forecast_days = 90
        base_forecast = []
        optimistic_forecast = []
        pessimistic_forecast = []
        
        running_balance = current_cash
        optimistic_balance = current_cash
        pessimistic_balance = current_cash
        
        # Distribute expected receivables over 45 days (average collection)
        daily_ar_inflow = float(expected_inflows.total or 0) / 45
        # Distribute payables over 30 days
        daily_ap_outflow = float(expected_outflows.total or 0) / 30
        
        for day in range(1, forecast_days + 1):
            date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
            
            # Base case: average historical + AR/AP adjustments
            ar_adjustment = daily_ar_inflow if day <= 45 else 0
            ap_adjustment = daily_ap_outflow if day <= 30 else 0
            
            base_flow = avg_daily_flow + ar_adjustment - ap_adjustment
            running_balance += base_flow
            
            # Optimistic: +20% inflows
            opt_flow = base_flow * 1.2 if base_flow > 0 else base_flow * 0.8
            optimistic_balance += opt_flow
            
            # Pessimistic: -20% inflows, +20% outflows
            pess_flow = base_flow * 0.8 if base_flow > 0 else base_flow * 1.2
            pessimistic_balance += pess_flow
            
            base_forecast.append({
                "date": date,
                "day": day,
                "balance": round(running_balance, 2)
            })
            optimistic_forecast.append({
                "date": date,
                "day": day,
                "balance": round(optimistic_balance, 2)
            })
            pessimistic_forecast.append({
                "date": date,
                "day": day,
                "balance": round(pessimistic_balance, 2)
            })
        
        # Calculate runway for each scenario
        def calculate_runway(forecast):
            for i, f in enumerate(forecast):
                if f["balance"] <= 0:
                    return i
            return 999  # More than forecast period
        
        base_runway = calculate_runway(base_forecast)
        opt_runway = calculate_runway(optimistic_forecast)
        pess_runway = calculate_runway(pessimistic_forecast)
        
        # Weekly summary
        weekly_summary = []
        for week in range(1, 14):  # 13 weeks
            week_start = (week - 1) * 7
            week_end = min(week * 7, 90)
            if week_start < len(base_forecast):
                weekly_summary.append({
                    "week": week,
                    "base_balance": base_forecast[min(week_end - 1, len(base_forecast) - 1)]["balance"],
                    "optimistic_balance": optimistic_forecast[min(week_end - 1, len(optimistic_forecast) - 1)]["balance"],
                    "pessimistic_balance": pessimistic_forecast[min(week_end - 1, len(pessimistic_forecast) - 1)]["balance"]
                })
        
        return {
            "current_cash": current_cash,
            "avg_daily_flow": round(avg_daily_flow, 2),
            "expected_ar_inflows": float(expected_inflows.total or 0),
            "expected_ap_outflows": float(expected_outflows.total or 0),
            "net_expected": float(expected_inflows.total or 0) - float(expected_outflows.total or 0),
            "base_forecast": base_forecast,
            "optimistic_forecast": optimistic_forecast,
            "pessimistic_forecast": pessimistic_forecast,
            "base_runway_days": base_runway,
            "optimistic_runway_days": opt_runway,
            "pessimistic_runway_days": pess_runway,
            "weekly_summary": weekly_summary,
            "end_of_period": {
                "base": base_forecast[-1]["balance"] if base_forecast else current_cash,
                "optimistic": optimistic_forecast[-1]["balance"] if optimistic_forecast else current_cash,
                "pessimistic": pessimistic_forecast[-1]["balance"] if pessimistic_forecast else current_cash
            }
        }
    
    # =========================================================================
    # 13-WEEK CASH FLOW FORECAST
    # =========================================================================
    
    def _generate_thirteen_week_forecast(self, min_cash_threshold: float = 0) -> Dict[str, Any]:
        """
        Generate detailed 13-week rolling cash flow forecast with:
        - Categorized inflows/outflows (AR, AP, Payroll, Operating, Taxes)
        - Historical actuals for past weeks with variance tracking
        - Forecast for future weeks based on due dates
        - Threshold alerts for weeks below minimum cash
        - Auto-detected payroll patterns
        """
        today = datetime.now().date()
        
        # Calculate the start of the 13-week period (start of current week - 1 week for historical comparison)
        # Week starts on Monday
        days_since_monday = today.weekday()
        current_week_start = today - timedelta(days=days_since_monday)
        
        # Include 1 week of history for variance comparison
        period_start = current_week_start - timedelta(weeks=1)
        period_end = current_week_start + timedelta(weeks=13) - timedelta(days=1)
        
        # Get current cash balance
        current_cash = self._get_cash_balance()
        
        # Auto-detect payroll pattern
        payroll_pattern = self._detect_payroll_pattern()
        
        # Get threshold from Company settings or use provided value
        if min_cash_threshold <= 0:
            try:
                min_cash_threshold = frappe.db.get_value(
                    "Company", self.company, "custom_min_cash_threshold"
                ) or 0
            except Exception:
                # Field doesn't exist
                min_cash_threshold = 0
        
        # Get historical cash transactions for actuals (last 2 weeks)
        historical_transactions = self._get_historical_cash_transactions(
            period_start, today
        )
        
        # Get expected AR inflows by due date
        ar_by_week = self._get_ar_collections_by_week(current_week_start, period_end)
        
        # Get expected AP outflows by due date
        ap_by_week = self._get_ap_payments_by_week(current_week_start, period_end)
        
        # Build week-by-week forecast
        weeks = []
        running_balance = current_cash
        
        # Calculate opening balance for the period
        # For historical weeks, we need to back-calculate from current balance
        historical_net_flow = sum(
            t.get('net_flow', 0) for t in historical_transactions.values()
        )
        opening_balance = current_cash - historical_net_flow
        
        for week_num in range(14):  # -1 (historical) to 12 (forecast) = 14 weeks total
            week_start = current_week_start + timedelta(weeks=week_num - 1)
            week_end = week_start + timedelta(days=6)
            week_key = week_start.strftime('%Y-%m-%d')
            
            is_historical = week_end < today
            is_current = week_start <= today <= week_end
            is_forecast = week_start > today
            
            # Determine if this week has actuals
            is_actual = is_historical or (is_current and today.weekday() >= 3)  # After Thursday, use actuals
            
            # Convert to native Python bools for JSON serialization
            is_historical = bool(is_historical)
            is_current = bool(is_current)
            is_forecast = bool(is_forecast)
            is_actual = bool(is_actual)
            
            if is_actual and week_key in historical_transactions:
                # Use actual transactions
                week_data = historical_transactions[week_key]
                inflows = week_data.get('inflows', {})
                outflows = week_data.get('outflows', {})
            else:
                # Use forecast based on due dates and patterns
                inflows = {
                    'ar_collections': ar_by_week.get(week_key, {}).get('amount', 0),
                    'other_receipts': self._estimate_other_receipts(week_start),
                    'total': 0
                }
                inflows['total'] = inflows['ar_collections'] + inflows['other_receipts']
                
                outflows = {
                    'ap_payments': ap_by_week.get(week_key, {}).get('amount', 0),
                    'payroll': self._get_payroll_for_week(week_start, payroll_pattern),
                    'operating_expenses': self._estimate_operating_expenses(week_start),
                    'taxes': self._get_scheduled_taxes(week_start, week_end),
                    'total': 0
                }
                outflows['total'] = (
                    outflows['ap_payments'] + 
                    outflows['payroll'] + 
                    outflows['operating_expenses'] + 
                    outflows['taxes']
                )
            
            net_flow = inflows.get('total', 0) - outflows.get('total', 0)
            
            # Calculate opening balance for this week
            if week_num == 0:
                week_opening = opening_balance
            else:
                week_opening = weeks[-1]['closing_balance'] if weeks else opening_balance
            
            closing_balance = week_opening + net_flow
            
            # Check variance for historical weeks that also had forecasts
            variance = None
            if is_actual and not is_forecast:
                original_forecast = self._get_original_forecast_for_week(week_key)
                if original_forecast:
                    variance = {
                        'inflows': inflows.get('total', 0) - original_forecast.get('inflows', 0),
                        'outflows': outflows.get('total', 0) - original_forecast.get('outflows', 0),
                        'net': net_flow - original_forecast.get('net_flow', 0)
                    }
            
            week_record = {
                'week_number': week_num,  # -1 = last week, 0 = current, 1-12 = future
                'week_start': str(week_start),
                'week_end': str(week_end),
                'week_label': self._get_week_label(week_start, week_num),
                'is_actual': is_actual,
                'is_forecast': not is_actual,
                'is_current': is_current,
                'opening_balance': round(week_opening, 2),
                'inflows': {
                    'ar_collections': round(inflows.get('ar_collections', 0), 2),
                    'other_receipts': round(inflows.get('other_receipts', 0), 2),
                    'total': round(inflows.get('total', 0), 2)
                },
                'outflows': {
                    'ap_payments': round(outflows.get('ap_payments', 0), 2),
                    'payroll': round(outflows.get('payroll', 0), 2),
                    'operating_expenses': round(outflows.get('operating_expenses', 0), 2),
                    'taxes': round(outflows.get('taxes', 0), 2),
                    'total': round(outflows.get('total', 0), 2)
                },
                'net_flow': round(net_flow, 2),
                'closing_balance': round(closing_balance, 2),
                'below_threshold': bool(closing_balance < min_cash_threshold),
                'variance': variance
            }
            
            weeks.append(week_record)
            running_balance = closing_balance
        
        # Calculate summary statistics
        future_weeks = [w for w in weeks if w['is_forecast']]
        all_weeks = weeks[1:]  # Exclude historical week from summary
        
        total_inflows = sum(w['inflows']['total'] for w in future_weeks)
        total_outflows = sum(w['outflows']['total'] for w in future_weeks)
        ending_cash = weeks[-1]['closing_balance'] if weeks else current_cash
        
        min_balance_week = min(all_weeks, key=lambda w: w['closing_balance']) if all_weeks else None
        weeks_below_threshold = sum(1 for w in all_weeks if w['below_threshold'])
        
        # Generate scenario analysis for the 13-week forecast
        scenarios = self._generate_cashflow_scenarios(weeks, current_cash, min_cash_threshold)
        
        # Generate variance analysis for historical weeks
        variance_analysis = self._generate_variance_analysis(weeks)
        
        return {
            'opening_balance': round(opening_balance, 2),
            'current_cash': round(current_cash, 2),
            'min_cash_threshold': round(min_cash_threshold, 2),
            'currency': self.base_currency,
            'generated_at': datetime.now().isoformat(),
            'cache_expires': (datetime.now() + timedelta(days=1)).isoformat(),
            'payroll_detection': payroll_pattern,
            'weeks': weeks,
            'scenarios': scenarios,
            'variance_analysis': variance_analysis,
            'summary': {
                'total_inflows': round(total_inflows, 2),
                'total_outflows': round(total_outflows, 2),
                'net_cash_flow': round(total_inflows - total_outflows, 2),
                'ending_cash': round(ending_cash, 2),
                'minimum_balance': round(min_balance_week['closing_balance'], 2) if min_balance_week else current_cash,
                'minimum_balance_week': min_balance_week['week_number'] if min_balance_week else 0,
                'minimum_balance_date': min_balance_week['week_start'] if min_balance_week else str(today),
                'weeks_below_threshold': weeks_below_threshold,
                'avg_weekly_inflow': round(total_inflows / len(future_weeks), 2) if future_weeks else 0,
                'avg_weekly_outflow': round(total_outflows / len(future_weeks), 2) if future_weeks else 0
            }
        }
    
    def _generate_cashflow_scenarios(self, base_weeks: List[Dict], current_cash: float, threshold: float) -> Dict[str, Any]:
        """
        Generate what-if scenarios for 13-week cash flow forecast
        Scenarios: AR delay, AP acceleration, revenue drop, expense increase, etc.
        """
        forecast_weeks = [w for w in base_weeks if w.get('is_forecast')]
        if not forecast_weeks:
            return {'scenarios': [], 'quick_actions': []}
        
        base_ending = forecast_weeks[-1]['closing_balance'] if forecast_weeks else current_cash
        base_min = min(w['closing_balance'] for w in forecast_weeks) if forecast_weeks else current_cash
        
        # Calculate scenario impacts
        scenarios = []
        
        # Scenario 1: AR Collections Delayed 2 weeks
        ar_delayed = self._apply_scenario(forecast_weeks, ar_delay_weeks=2)
        scenarios.append({
            'id': 'ar_delay_2w',
            'name': 'AR Collections Delayed 2 Weeks',
            'description': 'What if customer payments are delayed by 2 weeks?',
            'type': 'risk',
            'icon': 'clock',
            'ending_balance': ar_delayed['ending_balance'],
            'min_balance': ar_delayed['min_balance'],
            'impact': ar_delayed['ending_balance'] - base_ending,
            'weeks_below_threshold': ar_delayed['weeks_below_threshold'],
            'risk_level': 'high' if ar_delayed['min_balance'] < threshold else 'medium'
        })
        
        # Scenario 2: AR Collections Improved 20%
        ar_improved = self._apply_scenario(forecast_weeks, ar_change_pct=20)
        scenarios.append({
            'id': 'ar_improve_20',
            'name': 'AR Collections +20%',
            'description': 'What if we improve collections by 20%?',
            'type': 'opportunity',
            'icon': 'trending-up',
            'ending_balance': ar_improved['ending_balance'],
            'min_balance': ar_improved['min_balance'],
            'impact': ar_improved['ending_balance'] - base_ending,
            'weeks_below_threshold': ar_improved['weeks_below_threshold'],
            'risk_level': 'low'
        })
        
        # Scenario 3: AP Payments Accelerated (paid early)
        ap_accelerated = self._apply_scenario(forecast_weeks, ap_delay_weeks=-1)
        scenarios.append({
            'id': 'ap_accelerate',
            'name': 'AP Payments Accelerated',
            'description': 'What if we pay suppliers 1 week early for discounts?',
            'type': 'decision',
            'icon': 'fast-forward',
            'ending_balance': ap_accelerated['ending_balance'],
            'min_balance': ap_accelerated['min_balance'],
            'impact': ap_accelerated['ending_balance'] - base_ending,
            'weeks_below_threshold': ap_accelerated['weeks_below_threshold'],
            'risk_level': 'medium' if ap_accelerated['min_balance'] < threshold else 'low'
        })
        
        # Scenario 4: AP Payments Delayed 2 weeks
        ap_delayed = self._apply_scenario(forecast_weeks, ap_delay_weeks=2)
        scenarios.append({
            'id': 'ap_delay_2w',
            'name': 'AP Payments Delayed 2 Weeks',
            'description': 'What if we negotiate extended payment terms?',
            'type': 'opportunity',
            'icon': 'pause',
            'ending_balance': ap_delayed['ending_balance'],
            'min_balance': ap_delayed['min_balance'],
            'impact': ap_delayed['ending_balance'] - base_ending,
            'weeks_below_threshold': ap_delayed['weeks_below_threshold'],
            'risk_level': 'low'
        })
        
        # Scenario 5: Revenue/Inflows Drop 30%
        revenue_drop = self._apply_scenario(forecast_weeks, ar_change_pct=-30)
        scenarios.append({
            'id': 'revenue_drop_30',
            'name': 'Revenue Drop 30%',
            'description': 'Stress test: What if revenue drops 30%?',
            'type': 'risk',
            'icon': 'alert-triangle',
            'ending_balance': revenue_drop['ending_balance'],
            'min_balance': revenue_drop['min_balance'],
            'impact': revenue_drop['ending_balance'] - base_ending,
            'weeks_below_threshold': revenue_drop['weeks_below_threshold'],
            'risk_level': 'critical' if revenue_drop['min_balance'] < 0 else 'high'
        })
        
        # Scenario 6: Operating Expenses Increase 20%
        opex_increase = self._apply_scenario(forecast_weeks, opex_change_pct=20)
        scenarios.append({
            'id': 'opex_increase_20',
            'name': 'Operating Expenses +20%',
            'description': 'What if operating costs increase 20%?',
            'type': 'risk',
            'icon': 'trending-up',
            'ending_balance': opex_increase['ending_balance'],
            'min_balance': opex_increase['min_balance'],
            'impact': opex_increase['ending_balance'] - base_ending,
            'weeks_below_threshold': opex_increase['weeks_below_threshold'],
            'risk_level': 'high' if opex_increase['min_balance'] < threshold else 'medium'
        })
        
        # Scenario 7: Best Case (AR +20%, AP delayed, OpEx -10%)
        best_case = self._apply_scenario(forecast_weeks, ar_change_pct=20, ap_delay_weeks=1, opex_change_pct=-10)
        scenarios.append({
            'id': 'best_case',
            'name': 'Best Case Scenario',
            'description': 'Optimistic: Better collections, delayed AP, lower costs',
            'type': 'opportunity',
            'icon': 'sun',
            'ending_balance': best_case['ending_balance'],
            'min_balance': best_case['min_balance'],
            'impact': best_case['ending_balance'] - base_ending,
            'weeks_below_threshold': best_case['weeks_below_threshold'],
            'risk_level': 'low'
        })
        
        # Scenario 8: Worst Case (AR -30%, AR delayed, OpEx +20%)
        worst_case = self._apply_scenario(forecast_weeks, ar_change_pct=-30, ar_delay_weeks=2, opex_change_pct=20)
        scenarios.append({
            'id': 'worst_case',
            'name': 'Worst Case Scenario',
            'description': 'Pessimistic: Poor collections, delayed payments, higher costs',
            'type': 'risk',
            'icon': 'cloud-rain',
            'ending_balance': worst_case['ending_balance'],
            'min_balance': worst_case['min_balance'],
            'impact': worst_case['ending_balance'] - base_ending,
            'weeks_below_threshold': worst_case['weeks_below_threshold'],
            'risk_level': 'critical' if worst_case['min_balance'] < 0 else 'high'
        })
        
        # Quick action recommendations based on scenarios
        quick_actions = []
        
        # Calculate impacts for recommendations
        ar_delayed_impact = ar_delayed['ending_balance'] - base_ending
        ap_delayed_impact = ap_delayed['ending_balance'] - base_ending
        
        if ar_delayed['min_balance'] < threshold:
            quick_actions.append({
                'action': 'Accelerate AR Collections',
                'priority': 'high',
                'potential_impact': abs(ar_delayed['min_balance'] - base_min),
                'description': 'Focus on collecting overdue invoices to avoid cash shortfall'
            })
        
        if ap_delayed_impact > 0 and base_min < threshold * 1.5:
            quick_actions.append({
                'action': 'Negotiate Extended Payment Terms',
                'priority': 'medium',
                'potential_impact': ap_delayed_impact,
                'description': 'Extend AP terms to improve cash position'
            })
        
        if worst_case['min_balance'] < 0:
            quick_actions.append({
                'action': 'Secure Credit Line',
                'priority': 'high',
                'potential_impact': abs(worst_case['min_balance']),
                'description': 'Consider establishing or increasing credit facility as backup'
            })
        
        return {
            'base_ending_balance': round(base_ending, 2),
            'base_min_balance': round(base_min, 2),
            'threshold': round(threshold, 2),
            'scenarios': scenarios,
            'quick_actions': quick_actions
        }
    
    def _apply_scenario(
        self, 
        base_weeks: List[Dict], 
        ar_change_pct: float = 0,
        ar_delay_weeks: int = 0,
        ap_change_pct: float = 0,
        ap_delay_weeks: int = 0,
        opex_change_pct: float = 0,
        payroll_change_pct: float = 0
    ) -> Dict[str, Any]:
        """Apply scenario adjustments to forecast weeks and calculate results"""
        if not base_weeks:
            return {'ending_balance': 0, 'min_balance': 0, 'weeks_below_threshold': 0}
        
        adjusted_weeks = []
        running_balance = base_weeks[0]['opening_balance']
        
        for i, week in enumerate(base_weeks):
            # Get base values
            ar = week['inflows'].get('ar_collections', 0)
            other_receipts = week['inflows'].get('other_receipts', 0)
            ap = week['outflows'].get('ap_payments', 0)
            payroll = week['outflows'].get('payroll', 0)
            opex = week['outflows'].get('operating_expenses', 0)
            taxes = week['outflows'].get('taxes', 0)
            
            # Apply AR changes
            if ar_change_pct != 0:
                ar = ar * (1 + ar_change_pct / 100)
            
            # Apply AR delay (shift collections forward)
            if ar_delay_weeks > 0 and i < ar_delay_weeks:
                # Early weeks lose some AR
                ar = ar * 0.3
            elif ar_delay_weeks < 0 and i < len(base_weeks) + ar_delay_weeks:
                # Early weeks gain AR from future
                ar = ar * 1.3
            
            # Apply AP changes
            if ap_change_pct != 0:
                ap = ap * (1 + ap_change_pct / 100)
            
            # Apply AP delay (shift payments forward)
            if ap_delay_weeks > 0 and i < ap_delay_weeks:
                ap = ap * 0.3  # Early weeks pay less
            elif ap_delay_weeks < 0 and i < len(base_weeks) + ap_delay_weeks:
                ap = ap * 1.5  # Early weeks pay more
            
            # Apply OpEx changes
            if opex_change_pct != 0:
                opex = opex * (1 + opex_change_pct / 100)
            
            # Apply payroll changes
            if payroll_change_pct != 0:
                payroll = payroll * (1 + payroll_change_pct / 100)
            
            total_inflows = ar + other_receipts
            total_outflows = ap + payroll + opex + taxes
            net_flow = total_inflows - total_outflows
            closing = running_balance + net_flow
            
            adjusted_weeks.append({
                'closing_balance': closing,
                'net_flow': net_flow
            })
            running_balance = closing
        
        min_balance = min(w['closing_balance'] for w in adjusted_weeks) if adjusted_weeks else 0
        ending_balance = adjusted_weeks[-1]['closing_balance'] if adjusted_weeks else 0
        threshold = base_weeks[0].get('threshold', 0) if base_weeks else 0
        
        return {
            'ending_balance': round(ending_balance, 2),
            'min_balance': round(min_balance, 2),
            'weeks_below_threshold': sum(1 for w in adjusted_weeks if w['closing_balance'] < threshold)
        }
    
    def _generate_variance_analysis(self, weeks: List[Dict]) -> Dict[str, Any]:
        """
        Generate variance analysis comparing actual vs forecast for historical weeks
        """
        actual_weeks = [w for w in weeks if w.get('is_actual') and w.get('variance')]
        
        if not actual_weeks:
            return {
                'has_variance_data': False,
                'weeks_analyzed': 0,
                'summary': {},
                'insights': [],
                'weekly_details': []
            }
        
        # Calculate aggregate variances
        total_inflow_variance = sum(w['variance'].get('inflows', 0) for w in actual_weeks)
        total_outflow_variance = sum(w['variance'].get('outflows', 0) for w in actual_weeks)
        total_net_variance = sum(w['variance'].get('net', 0) for w in actual_weeks)
        
        avg_inflow_variance = total_inflow_variance / len(actual_weeks)
        avg_outflow_variance = total_outflow_variance / len(actual_weeks)
        avg_net_variance = total_net_variance / len(actual_weeks)
        
        # Calculate forecast accuracy
        total_forecast_inflows = sum(
            w['inflows']['total'] - w['variance'].get('inflows', 0) 
            for w in actual_weeks
        )
        total_actual_inflows = sum(w['inflows']['total'] for w in actual_weeks)
        
        inflow_accuracy = (1 - abs(total_inflow_variance) / total_forecast_inflows * 100) if total_forecast_inflows > 0 else 100
        
        total_forecast_outflows = sum(
            w['outflows']['total'] - w['variance'].get('outflows', 0)
            for w in actual_weeks
        )
        total_actual_outflows = sum(w['outflows']['total'] for w in actual_weeks)
        
        outflow_accuracy = (1 - abs(total_outflow_variance) / total_forecast_outflows * 100) if total_forecast_outflows > 0 else 100
        
        # Generate insights
        insights = []
        
        if avg_inflow_variance > 0:
            insights.append({
                'type': 'positive',
                'category': 'inflows',
                'title': 'Collections Better Than Expected',
                'description': f'Actual inflows exceeded forecast by avg {self._format_currency(avg_inflow_variance)}/week',
                'recommendation': 'Consider revising forecast model upward'
            })
        elif avg_inflow_variance < 0:
            insights.append({
                'type': 'negative',
                'category': 'inflows',
                'title': 'Collections Below Forecast',
                'description': f'Actual inflows fell short of forecast by avg {self._format_currency(abs(avg_inflow_variance))}/week',
                'recommendation': 'Review AR collection processes and customer payment terms'
            })
        
        if avg_outflow_variance > 0:
            insights.append({
                'type': 'negative',
                'category': 'outflows',
                'title': 'Spending Higher Than Forecast',
                'description': f'Actual outflows exceeded forecast by avg {self._format_currency(avg_outflow_variance)}/week',
                'recommendation': 'Review expense controls and budget adherence'
            })
        elif avg_outflow_variance < 0:
            insights.append({
                'type': 'positive',
                'category': 'outflows',
                'title': 'Spending Below Forecast',
                'description': f'Actual outflows were below forecast by avg {self._format_currency(abs(avg_outflow_variance))}/week',
                'recommendation': 'Verify if delayed payments or deferred expenses'
            })
        
        # Net position insight
        if total_net_variance > 0:
            insights.append({
                'type': 'positive',
                'category': 'net',
                'title': 'Net Cash Position Better',
                'description': f'Cumulative net cash {self._format_currency(total_net_variance)} better than forecast',
                'recommendation': 'Good performance - consider investment opportunities'
            })
        elif total_net_variance < 0:
            insights.append({
                'type': 'negative',
                'category': 'net',
                'title': 'Net Cash Position Worse',
                'description': f'Cumulative net cash {self._format_currency(abs(total_net_variance))} below forecast',
                'recommendation': 'Monitor closely and review upcoming large payments'
            })
        
        # Weekly details with trend
        weekly_details = []
        for w in actual_weeks:
            weekly_details.append({
                'week_number': w['week_number'],
                'week_label': w['week_label'],
                'inflow_variance': round(w['variance'].get('inflows', 0), 2),
                'outflow_variance': round(w['variance'].get('outflows', 0), 2),
                'net_variance': round(w['variance'].get('net', 0), 2),
                'inflow_variance_pct': round(
                    w['variance'].get('inflows', 0) / (w['inflows']['total'] - w['variance'].get('inflows', 0)) * 100, 1
                ) if (w['inflows']['total'] - w['variance'].get('inflows', 0)) > 0 else 0,
                'outflow_variance_pct': round(
                    w['variance'].get('outflows', 0) / (w['outflows']['total'] - w['variance'].get('outflows', 0)) * 100, 1
                ) if (w['outflows']['total'] - w['variance'].get('outflows', 0)) > 0 else 0
            })
        
        return {
            'has_variance_data': True,
            'weeks_analyzed': len(actual_weeks),
            'summary': {
                'total_inflow_variance': round(total_inflow_variance, 2),
                'total_outflow_variance': round(total_outflow_variance, 2),
                'total_net_variance': round(total_net_variance, 2),
                'avg_inflow_variance': round(avg_inflow_variance, 2),
                'avg_outflow_variance': round(avg_outflow_variance, 2),
                'avg_net_variance': round(avg_net_variance, 2),
                'inflow_forecast_accuracy': round(max(0, min(100, inflow_accuracy)), 1),
                'outflow_forecast_accuracy': round(max(0, min(100, outflow_accuracy)), 1)
            },
            'insights': insights,
            'weekly_details': weekly_details
        }
    
    def _format_currency(self, value: float) -> str:
        """Helper to format currency for insights"""
        if abs(value) >= 1000000:
            return f"KES {value/1000000:.1f}M"
        elif abs(value) >= 1000:
            return f"KES {value/1000:.0f}K"
        return f"KES {value:.0f}"
    
    def _detect_payroll_pattern(self) -> Dict[str, Any]:
        """
        Auto-detect payroll schedule from historical Journal Entry and Payment Entry
        containing salary/payroll/wages keywords
        """
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        # Search for payroll-related payments
        payroll_entries = frappe.db.sql("""
            SELECT 
                pe.posting_date,
                pe.paid_amount,
                pe.reference_no,
                'Payment Entry' as doctype
            FROM `tabPayment Entry` pe
            WHERE pe.company = %s
                AND pe.docstatus = 1
                AND pe.posting_date >= %s
                AND pe.payment_type = 'Pay'
                AND (
                    pe.reference_no LIKE '%%salary%%'
                    OR pe.reference_no LIKE '%%payroll%%'
                    OR pe.reference_no LIKE '%%wages%%'
                    OR pe.remarks LIKE '%%salary%%'
                    OR pe.remarks LIKE '%%payroll%%'
                )
            UNION ALL
            SELECT 
                je.posting_date,
                (SELECT ABS(SUM(jea.debit_in_account_currency)) 
                 FROM `tabJournal Entry Account` jea 
                 WHERE jea.parent = je.name AND jea.debit_in_account_currency > 0) as paid_amount,
                je.cheque_no as reference_no,
                'Journal Entry' as doctype
            FROM `tabJournal Entry` je
            WHERE je.company = %s
                AND je.docstatus = 1
                AND je.posting_date >= %s
                AND (
                    je.user_remark LIKE '%%salary%%'
                    OR je.user_remark LIKE '%%payroll%%'
                    OR je.user_remark LIKE '%%wages%%'
                    OR je.cheque_no LIKE '%%salary%%'
                )
            ORDER BY posting_date DESC
        """, (self.company, six_months_ago, self.company, six_months_ago), as_dict=True)
        
        if not payroll_entries or len(payroll_entries) < 2:
            # Not enough data, check salary account directly
            payroll_entries = frappe.db.sql("""
                SELECT 
                    gle.posting_date,
                    ABS(gle.debit - gle.credit) as paid_amount
                FROM `tabGL Entry` gle
                JOIN `tabAccount` acc ON gle.account = acc.name
                WHERE gle.company = %s
                    AND gle.posting_date >= %s
                    AND gle.is_cancelled = 0
                    AND (
                        acc.name LIKE '%%Salary%%'
                        OR acc.name LIKE '%%Payroll%%'
                        OR acc.name LIKE '%%Wages%%'
                    )
                    AND ABS(gle.debit - gle.credit) > 10000
                ORDER BY gle.posting_date DESC
            """, (self.company, six_months_ago), as_dict=True)
        
        if not payroll_entries or len(payroll_entries) < 2:
            return {
                'detected': False,
                'frequency': 'unknown',
                'typical_amount': 0,
                'next_date': None,
                'confidence': 0,
                'day_of_month': None
            }
        
        # Analyze patterns
        dates = [datetime.strptime(str(e.posting_date), '%Y-%m-%d') if isinstance(e.posting_date, str) 
                 else e.posting_date for e in payroll_entries]
        amounts = [float(e.paid_amount or 0) for e in payroll_entries]
        
        # Calculate intervals between payments
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i-1] - dates[i]).days
            if 5 <= interval <= 35:  # Reasonable payroll interval
                intervals.append(interval)
        
        if not intervals:
            return {
                'detected': False,
                'frequency': 'unknown',
                'typical_amount': float(np.mean(amounts)) if amounts else 0,
                'next_date': None,
                'confidence': 0,
                'day_of_month': None
            }
        
        avg_interval = float(np.mean(intervals))
        std_interval = float(np.std(intervals)) if len(intervals) > 1 else 10
        
        # Determine frequency
        if avg_interval <= 9:
            frequency = 'weekly'
            expected_interval = 7
        elif avg_interval <= 17:
            frequency = 'bi-weekly'
            expected_interval = 14
        elif avg_interval <= 20:
            frequency = 'semi-monthly'
            expected_interval = 15
        else:
            frequency = 'monthly'
            expected_interval = 30
        
        # Calculate confidence based on consistency
        consistency = 1 - (std_interval / avg_interval) if avg_interval > 0 else 0
        confidence = min(0.95, max(0.3, consistency))
        
        # Typical amount (median to reduce outlier effect)
        typical_amount = float(np.median(amounts)) if amounts else 0
        
        # Detect day of month for monthly payroll
        day_of_month = None
        if frequency == 'monthly':
            days = [d.day for d in dates]
            day_counts = {}
            for d in days:
                day_counts[d] = day_counts.get(d, 0) + 1
            if day_counts:
                day_of_month = max(day_counts, key=day_counts.get)
        
        # Calculate next expected payroll date
        last_payroll = dates[0] if dates else datetime.now()
        next_date = last_payroll + timedelta(days=expected_interval)
        
        # Get the date part for comparison
        def get_date(d):
            if hasattr(d, 'date') and callable(d.date):
                return d.date()
            return d
        
        # If next_date is in the past, keep adding intervals
        while get_date(next_date) < datetime.now().date():
            next_date += timedelta(days=expected_interval)
        
        return {
            'detected': True,
            'frequency': frequency,
            'typical_amount': round(typical_amount, 2),
            'next_date': str(get_date(next_date)),
            'confidence': round(confidence, 2),
            'day_of_month': day_of_month,
            'avg_interval_days': round(avg_interval, 1),
            'entries_analyzed': len(payroll_entries)
        }
    
    def _get_historical_cash_transactions(self, start_date: datetime, end_date: datetime) -> Dict[str, Dict]:
        """Get categorized historical cash transactions by week"""
        transactions = frappe.db.sql("""
            SELECT 
                gle.posting_date,
                gle.account,
                acc.account_type,
                acc.root_type,
                acc.parent_account,
                (gle.debit - gle.credit) as amount,
                gle.voucher_type,
                gle.voucher_no,
                gle.against
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
                AND gle.posting_date BETWEEN %s AND %s
                AND acc.account_type IN ('Cash', 'Bank')
                AND gle.is_cancelled = 0
            ORDER BY gle.posting_date
        """, (self.company, start_date, end_date), as_dict=True)
        
        weeks_data = {}
        
        for txn in transactions:
            posting_date = txn.posting_date
            if isinstance(posting_date, str):
                posting_date = datetime.strptime(posting_date, '%Y-%m-%d').date()
            
            # Find week start (Monday)
            days_since_monday = posting_date.weekday()
            week_start = posting_date - timedelta(days=days_since_monday)
            week_key = str(week_start)
            
            if week_key not in weeks_data:
                weeks_data[week_key] = {
                    'inflows': {'ar_collections': 0, 'other_receipts': 0, 'total': 0},
                    'outflows': {'ap_payments': 0, 'payroll': 0, 'operating_expenses': 0, 'taxes': 0, 'total': 0},
                    'net_flow': 0
                }
            
            amount = float(txn.amount or 0)
            voucher_type = txn.voucher_type or ''
            against = txn.against or ''
            
            if amount > 0:  # Inflow (debit to cash)
                if voucher_type == 'Sales Invoice' or 'receivable' in against.lower():
                    weeks_data[week_key]['inflows']['ar_collections'] += amount
                else:
                    weeks_data[week_key]['inflows']['other_receipts'] += amount
                weeks_data[week_key]['inflows']['total'] += amount
            else:  # Outflow (credit from cash)
                abs_amount = abs(amount)
                if voucher_type == 'Purchase Invoice' or 'payable' in against.lower():
                    weeks_data[week_key]['outflows']['ap_payments'] += abs_amount
                elif 'salary' in against.lower() or 'payroll' in against.lower() or 'wages' in against.lower():
                    weeks_data[week_key]['outflows']['payroll'] += abs_amount
                elif 'tax' in against.lower() or 'vat' in against.lower() or 'paye' in against.lower():
                    weeks_data[week_key]['outflows']['taxes'] += abs_amount
                else:
                    weeks_data[week_key]['outflows']['operating_expenses'] += abs_amount
                weeks_data[week_key]['outflows']['total'] += abs_amount
            
            weeks_data[week_key]['net_flow'] = (
                weeks_data[week_key]['inflows']['total'] - 
                weeks_data[week_key]['outflows']['total']
            )
        
        return weeks_data
    
    def _get_ar_collections_by_week(self, start_date: datetime, end_date: datetime) -> Dict[str, Dict]:
        """Get expected AR collections by week based on due dates"""
        receivables = frappe.db.sql("""
            SELECT 
                si.name,
                si.due_date,
                si.outstanding_amount,
                si.customer
            FROM `tabSales Invoice` si
            WHERE si.company = %s
                AND si.docstatus = 1
                AND si.outstanding_amount > 0
                AND si.due_date BETWEEN %s AND %s
            ORDER BY si.due_date
        """, (self.company, start_date, end_date), as_dict=True)
        
        weeks = {}
        
        for inv in receivables:
            due_date = inv.due_date
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            # Find week start
            days_since_monday = due_date.weekday()
            week_start = due_date - timedelta(days=days_since_monday)
            week_key = str(week_start)
            
            if week_key not in weeks:
                weeks[week_key] = {'amount': 0, 'count': 0, 'invoices': []}
            
            weeks[week_key]['amount'] += float(inv.outstanding_amount or 0)
            weeks[week_key]['count'] += 1
            weeks[week_key]['invoices'].append(inv.name)
        
        # Also add overdue receivables to week 0 (current week)
        overdue = frappe.db.sql("""
            SELECT COALESCE(SUM(outstanding_amount), 0) as total
            FROM `tabSales Invoice`
            WHERE company = %s
                AND docstatus = 1
                AND outstanding_amount > 0
                AND due_date < %s
        """, (self.company, start_date), as_dict=True)[0].total or 0
        
        # Distribute overdue across first 4 weeks (assume gradual collection)
        if overdue > 0:
            weekly_overdue = overdue / 4
            for week_offset in range(4):
                week_date = start_date + timedelta(weeks=week_offset)
                if hasattr(week_date, 'date') and callable(week_date.date):
                    week_date = week_date.date()
                # If it's already a date object, use as-is
                days_since_monday = week_date.weekday()
                week_start = week_date - timedelta(days=days_since_monday)
                week_key = str(week_start)
                
                if week_key not in weeks:
                    weeks[week_key] = {'amount': 0, 'count': 0, 'invoices': []}
                weeks[week_key]['amount'] += weekly_overdue
        
        return weeks
    
    def _get_ap_payments_by_week(self, start_date: datetime, end_date: datetime) -> Dict[str, Dict]:
        """Get expected AP payments by week based on due dates"""
        payables = frappe.db.sql("""
            SELECT 
                pi.name,
                pi.due_date,
                pi.outstanding_amount,
                pi.supplier
            FROM `tabPurchase Invoice` pi
            WHERE pi.company = %s
                AND pi.docstatus = 1
                AND pi.outstanding_amount > 0
                AND pi.due_date BETWEEN %s AND %s
            ORDER BY pi.due_date
        """, (self.company, start_date, end_date), as_dict=True)
        
        weeks = {}
        
        for inv in payables:
            due_date = inv.due_date
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            # Find week start
            days_since_monday = due_date.weekday()
            week_start = due_date - timedelta(days=days_since_monday)
            week_key = str(week_start)
            
            if week_key not in weeks:
                weeks[week_key] = {'amount': 0, 'count': 0, 'invoices': []}
            
            weeks[week_key]['amount'] += float(inv.outstanding_amount or 0)
            weeks[week_key]['count'] += 1
            weeks[week_key]['invoices'].append(inv.name)
        
        return weeks
    
    def _get_payroll_for_week(self, week_start, payroll_pattern: Dict) -> float:
        """Get expected payroll amount for a specific week"""
        if not payroll_pattern.get('detected'):
            return 0
        
        if isinstance(week_start, str):
            week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
        elif hasattr(week_start, 'date') and callable(week_start.date):
            week_start = week_start.date()
        # If it's already a date object, use as-is
        
        week_end = week_start + timedelta(days=6)
        next_payroll = payroll_pattern.get('next_date')
        
        if not next_payroll:
            return 0
        
        next_payroll_date = datetime.strptime(next_payroll, '%Y-%m-%d').date()
        frequency = payroll_pattern.get('frequency', 'monthly')
        typical_amount = payroll_pattern.get('typical_amount', 0)
        
        # Check if payroll falls in this week
        payroll_in_week = week_start <= next_payroll_date <= week_end
        
        if payroll_in_week:
            return typical_amount
        
        # For weekly/bi-weekly, check recurring dates
        if frequency == 'weekly':
            interval = 7
        elif frequency == 'bi-weekly':
            interval = 14
        elif frequency == 'semi-monthly':
            interval = 15
        else:  # monthly
            interval = 30
        
        # Check if any subsequent payroll dates fall in this week
        check_date = next_payroll_date
        max_iterations = 20  # Safety limit
        iteration = 0
        
        while check_date <= week_end and iteration < max_iterations:
            if week_start <= check_date <= week_end:
                return typical_amount
            check_date += timedelta(days=interval)
            iteration += 1
        
        return 0
    
    def _estimate_other_receipts(self, week_start: datetime) -> float:
        """Estimate other receipts (non-AR) based on historical average"""
        # Get average weekly other receipts from last 12 weeks
        twelve_weeks_ago = (datetime.now() - timedelta(weeks=12)).strftime('%Y-%m-%d')
        
        other_receipts = frappe.db.sql("""
            SELECT COALESCE(SUM(gle.debit - gle.credit), 0) / 12 as weekly_avg
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
                AND gle.posting_date >= %s
                AND acc.account_type IN ('Cash', 'Bank')
                AND gle.is_cancelled = 0
                AND (gle.debit - gle.credit) > 0
                AND gle.voucher_type NOT IN ('Sales Invoice', 'Payment Entry')
        """, (self.company, twelve_weeks_ago), as_dict=True)[0].weekly_avg or 0
        
        return float(other_receipts)
    
    def _estimate_operating_expenses(self, week_start: datetime) -> float:
        """Estimate operating expenses based on historical average"""
        twelve_weeks_ago = (datetime.now() - timedelta(weeks=12)).strftime('%Y-%m-%d')
        
        operating_exp = frappe.db.sql("""
            SELECT COALESCE(ABS(SUM(gle.debit - gle.credit)), 0) / 12 as weekly_avg
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
                AND gle.posting_date >= %s
                AND acc.account_type IN ('Cash', 'Bank')
                AND gle.is_cancelled = 0
                AND (gle.debit - gle.credit) < 0
                AND gle.voucher_type NOT IN ('Purchase Invoice', 'Payment Entry')
                AND gle.against NOT LIKE '%%Salary%%'
                AND gle.against NOT LIKE '%%Payroll%%'
                AND gle.against NOT LIKE '%%Tax%%'
                AND gle.against NOT LIKE '%%VAT%%'
        """, (self.company, twelve_weeks_ago), as_dict=True)[0].weekly_avg or 0
        
        return abs(float(operating_exp))
    
    def _get_scheduled_taxes(self, week_start, week_end) -> float:
        """Get scheduled tax payments for a specific week"""
        # In Kenya, typical tax dates:
        # - VAT: 20th of following month
        # - PAYE: 9th of following month
        # - Corporate Tax: Quarterly installments
        
        if isinstance(week_start, str):
            week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
        elif hasattr(week_start, 'date') and callable(week_start.date):
            week_start = week_start.date()
        if isinstance(week_end, str):
            week_end = datetime.strptime(week_end, '%Y-%m-%d').date()
        elif hasattr(week_end, 'date') and callable(week_end.date):
            week_end = week_end.date()
        
        tax_amount = 0
        
        # Check for VAT due (20th of month)
        for day in range((week_end - week_start).days + 1):
            check_date = week_start + timedelta(days=day)
            
            # VAT due on 20th
            if check_date.day == 20:
                # Estimate VAT from previous month's sales
                prev_month_start = (check_date.replace(day=1) - timedelta(days=1)).replace(day=1)
                prev_month_end = check_date.replace(day=1) - timedelta(days=1)
                
                vat_collected = frappe.db.sql("""
                    SELECT COALESCE(SUM(total_taxes_and_charges), 0) as vat
                    FROM `tabSales Invoice`
                    WHERE company = %s
                        AND docstatus = 1
                        AND posting_date BETWEEN %s AND %s
                """, (self.company, prev_month_start, prev_month_end), as_dict=True)[0].vat or 0
                
                tax_amount += float(vat_collected) * 0.8  # Assume 80% is payable after input VAT offset
            
            # PAYE due on 9th
            if check_date.day == 9:
                # Use payroll pattern to estimate PAYE (roughly 30% of gross payroll)
                payroll_pattern = self._detect_payroll_pattern()
                if payroll_pattern.get('detected'):
                    tax_amount += payroll_pattern.get('typical_amount', 0) * 0.30
        
        return round(tax_amount, 2)
    
    def _get_original_forecast_for_week(self, week_key: str) -> Optional[Dict]:
        """Get the original forecast for a week (for variance calculation)"""
        # This would typically come from a stored forecast
        # For now, return None as we don't have historical forecasts stored
        cache_key = f"thirteen_week_forecast_{self.company}_{week_key}"
        cached = frappe.cache().get_value(cache_key)
        return cached
    
    def _get_week_label(self, week_start: datetime, week_num: int) -> str:
        """Generate a readable label for the week"""
        if isinstance(week_start, str):
            week_start = datetime.strptime(week_start, '%Y-%m-%d')
        elif isinstance(week_start, datetime):
            pass
        else:
            week_start = datetime.combine(week_start, datetime.min.time())
        
        if week_num == -1:
            return "Last Week"
        elif week_num == 0:
            return "This Week"
        elif week_num == 1:
            return "Next Week"
        else:
            return week_start.strftime('%b %d')
    
    # =========================================================================
    # CAPITAL PLANNING - Assets & CAPEX
    # =========================================================================
    
    def _analyze_capital_planning(self) -> Dict[str, Any]:
        """Analyze capital assets and CAPEX planning"""
        # Get all assets
        assets = frappe.db.sql("""
            SELECT 
                a.name,
                a.asset_name,
                a.asset_category,
                a.gross_purchase_amount,
                a.purchase_date,
                a.available_for_use_date,
                a.status,
                a.value_after_depreciation,
                a.total_number_of_depreciations,
                a.frequency_of_depreciation,
                COALESCE(ads.accumulated_depreciation, 0) as accumulated_depreciation
            FROM `tabAsset` a
            LEFT JOIN (
                SELECT parent, SUM(depreciation_amount) as accumulated_depreciation
                FROM `tabDepreciation Schedule`
                WHERE schedule_date <= CURDATE()
                GROUP BY parent
            ) ads ON ads.parent = a.name
            WHERE a.company = %s
                AND a.docstatus = 1
                AND a.status NOT IN ('Sold', 'Scrapped')
            ORDER BY a.gross_purchase_amount DESC
        """, (self.company,), as_dict=True)
        
        # Summarize by category
        category_summary = {}
        total_gross = 0
        total_net = 0
        total_depreciation = 0
        
        for asset in assets:
            cat = asset.asset_category or "Uncategorized"
            if cat not in category_summary:
                category_summary[cat] = {
                    "category": cat,
                    "asset_count": 0,
                    "gross_value": 0,
                    "net_value": 0,
                    "accumulated_depreciation": 0
                }
            
            gross = float(asset.gross_purchase_amount or 0)
            net = float(asset.value_after_depreciation or gross)
            dep = float(asset.accumulated_depreciation or 0)
            
            category_summary[cat]["asset_count"] += 1
            category_summary[cat]["gross_value"] += gross
            category_summary[cat]["net_value"] += net
            category_summary[cat]["accumulated_depreciation"] += dep
            
            total_gross += gross
            total_net += net
            total_depreciation += dep
        
        # CAPEX this year
        fy_start = self.fiscal_year["start_date"]
        ytd_capex = frappe.db.sql("""
            SELECT COALESCE(SUM(gross_purchase_amount), 0) as amount
            FROM `tabAsset`
            WHERE company = %s
                AND docstatus = 1
                AND purchase_date >= %s
        """, (self.company, fy_start), as_dict=True)[0].amount or 0
        
        # Prior year CAPEX for comparison
        prior_fy_start = (datetime.strptime(fy_start, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        prior_capex = frappe.db.sql("""
            SELECT COALESCE(SUM(gross_purchase_amount), 0) as amount
            FROM `tabAsset`
            WHERE company = %s
                AND docstatus = 1
                AND purchase_date >= %s
                AND purchase_date < %s
        """, (self.company, prior_fy_start, fy_start), as_dict=True)[0].amount or 0
        
        # Upcoming depreciation (next 12 months)
        upcoming_depreciation = frappe.db.sql("""
            SELECT 
                DATE_FORMAT(schedule_date, '%%Y-%%m') as period,
                SUM(depreciation_amount) as amount
            FROM `tabDepreciation Schedule` ads
            JOIN `tabAsset` a ON ads.parent = a.name
            WHERE a.company = %s
                AND a.docstatus = 1
                AND a.status NOT IN ('Sold', 'Scrapped')
                AND ads.schedule_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(schedule_date, '%%Y-%%m')
            ORDER BY period
        """, (self.company,), as_dict=True)
        
        return {
            "total_gross_assets": total_gross,
            "total_net_assets": total_net,
            "total_accumulated_depreciation": total_depreciation,
            "asset_count": len(assets),
            "ytd_capex": float(ytd_capex),
            "prior_year_capex": float(prior_capex),
            "capex_change_pct": round(((float(ytd_capex) - float(prior_capex)) / float(prior_capex) * 100), 1) if prior_capex > 0 else 0,
            "category_summary": list(category_summary.values()),
            "upcoming_depreciation": [{"period": d.period, "amount": float(d.amount)} for d in upcoming_depreciation],
            "top_assets": [
                {
                    "name": a.name,
                    "asset_name": a.asset_name,
                    "category": a.asset_category,
                    "gross_value": float(a.gross_purchase_amount or 0),
                    "net_value": float(a.value_after_depreciation or a.gross_purchase_amount or 0),
                    "status": a.status
                }
                for a in assets[:10]
            ]
        }
    
    # =========================================================================
    # WORKING CAPITAL ANALYSIS
    # =========================================================================
    
    def _analyze_working_capital(self) -> Dict[str, Any]:
        """Analyze working capital metrics and trends"""
        # Current Assets (Cash, Receivables, Inventory)
        current_assets = frappe.db.sql("""
            SELECT 
                COALESCE(SUM(CASE WHEN acc.account_type IN ('Cash', 'Bank') THEN (debit - credit) ELSE 0 END), 0) as cash,
                COALESCE(SUM(CASE WHEN acc.account_type = 'Receivable' THEN (debit - credit) ELSE 0 END), 0) as receivables,
                COALESCE(SUM(CASE WHEN acc.account_type = 'Stock' THEN (debit - credit) ELSE 0 END), 0) as inventory
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.company = %s
                AND gle.is_cancelled = 0
        """, (self.company,), as_dict=True)[0]
        
        cash = float(current_assets.cash or 0)
        receivables = float(current_assets.receivables or 0)
        inventory = float(current_assets.inventory or 0)
        total_current_assets = cash + receivables + inventory
        
        # Current Liabilities (Payables, Short-term debt)
        current_liabilities = frappe.db.sql("""
            SELECT COALESCE(SUM(credit - debit), 0) as payables
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.account_type = 'Payable'
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (self.company,), as_dict=True)[0].payables or 0
        
        total_current_liabilities = abs(float(current_liabilities))
        
        # Working Capital
        working_capital = total_current_assets - total_current_liabilities
        # Use absolute values for ratios, with reasonable caps
        current_ratio = round(total_current_assets / total_current_liabilities, 2) if total_current_liabilities > 1000 else 0
        quick_ratio = round((cash + receivables) / total_current_liabilities, 2) if total_current_liabilities > 1000 else 0
        
        # Cap ratios to reasonable values
        current_ratio = min(current_ratio, 10.0) if current_ratio > 0 else 0
        quick_ratio = min(quick_ratio, 10.0) if quick_ratio > 0 else 0
        
        # DSO, DPO, DIO calculations
        # Average daily revenue (last 90 days)
        avg_daily_revenue = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total), 0) / 90 as daily_avg
            FROM `tabSales Invoice`
            WHERE company = %s
                AND docstatus = 1
                AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        """, (self.company,), as_dict=True)[0].daily_avg or 1
        
        # Average daily COGS
        avg_daily_cogs = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total), 0) / 90 as daily_avg
            FROM `tabPurchase Invoice`
            WHERE company = %s
                AND docstatus = 1
                AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        """, (self.company,), as_dict=True)[0].daily_avg or 1
        
        # Calculate with caps for reasonable values
        dso = min(receivables / float(avg_daily_revenue), 365) if avg_daily_revenue > 0 else 0
        dpo = min(abs(float(current_liabilities)) / float(avg_daily_cogs), 365) if avg_daily_cogs > 0 else 0
        dio = min(inventory / float(avg_daily_cogs), 365) if avg_daily_cogs > 0 else 0
        ccc = dso + dio - dpo  # Cash Conversion Cycle
        ccc = max(min(ccc, 365), -365)  # Cap CCC to reasonable range
        
        # Monthly working capital trends
        wc_trends = frappe.db.sql("""
            SELECT 
                DATE_FORMAT(gle.posting_date, '%%Y-%%m') as period,
                SUM(CASE WHEN acc.account_type IN ('Cash', 'Bank', 'Receivable', 'Stock') 
                    THEN (debit - credit) ELSE 0 END) as current_assets,
                SUM(CASE WHEN acc.account_type = 'Payable' 
                    THEN (credit - debit) ELSE 0 END) as current_liabilities
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.posting_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                AND gle.company = %s
                AND gle.is_cancelled = 0
            GROUP BY DATE_FORMAT(gle.posting_date, '%%Y-%%m')
            ORDER BY period
        """, (self.company,), as_dict=True)
        
        trends = []
        for t in wc_trends:
            ca = float(t.current_assets or 0)
            cl = float(t.current_liabilities or 0)
            trends.append({
                "period": t.period,
                "current_assets": ca,
                "current_liabilities": cl,
                "working_capital": ca - cl,
                "current_ratio": round(ca / cl, 2) if cl > 0 else 999
            })
        
        return {
            "cash": cash,
            "receivables": receivables,
            "inventory": inventory,
            "total_current_assets": total_current_assets,
            "total_current_liabilities": total_current_liabilities,
            "working_capital": working_capital,
            "current_ratio": round(current_ratio, 2),
            "quick_ratio": round(quick_ratio, 2),
            "dso": round(dso, 1),
            "dpo": round(dpo, 1),
            "dio": round(dio, 1),
            "cash_conversion_cycle": round(ccc, 1),
            "trends": trends
        }
    
    # =========================================================================
    # FINANCIAL RATIO TRENDS
    # =========================================================================
    
    def _calculate_ratio_trends(self) -> Dict[str, Any]:
        """Calculate financial ratio trends over time"""
        # Get quarterly data for last 8 quarters
        quarters = []
        for q in range(8):
            end_date = datetime.now() - timedelta(days=q * 90)
            start_date = end_date - timedelta(days=90)
            quarters.append({
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d'),
                "label": f"Q{((end_date.month - 1) // 3) + 1} {end_date.year}"
            })
        
        ratio_trends = []
        for q in reversed(quarters):
            # Revenue and expenses for the quarter
            financials = frappe.db.sql("""
                SELECT 
                    SUM(CASE WHEN acc.root_type = 'Income' THEN ABS(credit - debit) ELSE 0 END) as revenue,
                    SUM(CASE WHEN acc.root_type = 'Expense' THEN ABS(debit - credit) ELSE 0 END) as expenses
                FROM `tabGL Entry` gle
                JOIN `tabAccount` acc ON gle.account = acc.name
                WHERE gle.posting_date BETWEEN %s AND %s
                    AND gle.company = %s
                    AND gle.is_cancelled = 0
            """, (q["start"], q["end"], self.company), as_dict=True)[0]
            
            # Get cumulative balance sheet items as of quarter end
            balance_sheet = frappe.db.sql("""
                SELECT 
                    SUM(CASE WHEN acc.root_type = 'Asset' THEN (debit - credit) ELSE 0 END) as assets,
                    SUM(CASE WHEN acc.root_type = 'Liability' THEN (credit - debit) ELSE 0 END) as liabilities,
                    SUM(CASE WHEN acc.root_type = 'Equity' THEN (credit - debit) ELSE 0 END) as equity
                FROM `tabGL Entry` gle
                JOIN `tabAccount` acc ON gle.account = acc.name
                WHERE gle.posting_date <= %s
                    AND gle.company = %s
                    AND gle.is_cancelled = 0
            """, (q["end"], self.company), as_dict=True)[0]
            
            revenue = float(financials.revenue or 0)
            expenses = float(financials.expenses or 0)
            assets = abs(float(balance_sheet.assets or 0))
            liabilities = abs(float(balance_sheet.liabilities or 0))
            equity = abs(float(balance_sheet.equity or 0))
            net_income = revenue - expenses
            
            # Avoid division issues - use reasonable defaults
            assets = assets if assets > 1000 else 1
            equity = equity if equity > 1000 else 1
            
            ratio_trends.append({
                "period": q["label"],
                "gross_margin": round((revenue - expenses) / revenue * 100, 1) if revenue > 0 else 0,
                "net_margin": round(net_income / revenue * 100, 1) if revenue > 0 else 0,
                "roe": round(net_income / equity * 100, 1) if equity > 1000 else 0,
                "roa": round(net_income / assets * 100, 1) if assets > 1000 else 0,
                "debt_to_equity": round(liabilities / equity, 2) if equity > 1000 else 0,
                "asset_turnover": round(revenue / assets, 2) if assets > 1000 else 0
            })
        
        # Current period ratios
        current = ratio_trends[-1] if ratio_trends else {}
        
        # Industry benchmarks (Kenya SME averages - indicative)
        benchmarks = {
            "gross_margin": 35.0,
            "net_margin": 10.0,
            "roe": 15.0,
            "roa": 8.0,
            "debt_to_equity": 1.5,
            "asset_turnover": 1.2
        }
        
        return {
            "current_ratios": current,
            "trends": ratio_trends,
            "benchmarks": benchmarks,
            "ratio_cards": [
                {
                    "name": "Gross Margin",
                    "value": current.get("gross_margin", 0),
                    "benchmark": benchmarks["gross_margin"],
                    "status": "good" if current.get("gross_margin", 0) >= benchmarks["gross_margin"] else "warning"
                },
                {
                    "name": "Net Margin",
                    "value": current.get("net_margin", 0),
                    "benchmark": benchmarks["net_margin"],
                    "status": "good" if current.get("net_margin", 0) >= benchmarks["net_margin"] else "warning"
                },
                {
                    "name": "ROE",
                    "value": current.get("roe", 0),
                    "benchmark": benchmarks["roe"],
                    "status": "good" if current.get("roe", 0) >= benchmarks["roe"] else "warning"
                },
                {
                    "name": "ROA",
                    "value": current.get("roa", 0),
                    "benchmark": benchmarks["roa"],
                    "status": "good" if current.get("roa", 0) >= benchmarks["roa"] else "warning"
                },
                {
                    "name": "Debt/Equity",
                    "value": current.get("debt_to_equity", 0),
                    "benchmark": benchmarks["debt_to_equity"],
                    "status": "good" if current.get("debt_to_equity", 0) <= benchmarks["debt_to_equity"] else "warning"
                },
                {
                    "name": "Asset Turnover",
                    "value": current.get("asset_turnover", 0),
                    "benchmark": benchmarks["asset_turnover"],
                    "status": "good" if current.get("asset_turnover", 0) >= benchmarks["asset_turnover"] else "warning"
                }
            ]
        }
    
    # =========================================================================
    # SCENARIO ANALYSIS - Sensitivity + Monte Carlo
    # =========================================================================
    
    def _generate_scenario_analysis(self) -> Dict[str, Any]:
        """Generate scenario analysis with sensitivity and Monte Carlo"""
        # Get baseline metrics
        fy_start = self.fiscal_year["start_date"]
        today = datetime.now().strftime('%Y-%m-%d')
        
        baseline = frappe.db.sql("""
            SELECT 
                SUM(CASE WHEN acc.root_type = 'Income' THEN ABS(credit - debit) ELSE 0 END) as revenue,
                SUM(CASE WHEN acc.root_type = 'Expense' THEN ABS(debit - credit) ELSE 0 END) as expenses
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.posting_date BETWEEN %s AND %s
                AND gle.company = %s
                AND gle.is_cancelled = 0
        """, (fy_start, today, self.company), as_dict=True)[0]
        
        base_revenue = float(baseline.revenue or 0)
        base_expenses = float(baseline.expenses or 0)
        base_net_income = base_revenue - base_expenses
        base_tax = base_net_income * (self.CORPORATE_TAX_RATE / 100) if base_net_income > 0 else 0
        base_net_after_tax = base_net_income - base_tax
        
        # =====================
        # SENSITIVITY ANALYSIS
        # =====================
        sensitivity_scenarios = []
        revenue_changes = [-30, -20, -10, 0, 10, 20, 30]
        expense_changes = [-20, -10, 0, 10, 20]
        
        for rev_change in revenue_changes:
            for exp_change in expense_changes:
                adj_revenue = base_revenue * (1 + rev_change / 100)
                adj_expenses = base_expenses * (1 + exp_change / 100)
                adj_net = adj_revenue - adj_expenses
                adj_tax = adj_net * (self.CORPORATE_TAX_RATE / 100) if adj_net > 0 else 0
                adj_net_after_tax = adj_net - adj_tax
                
                sensitivity_scenarios.append({
                    "revenue_change": rev_change,
                    "expense_change": exp_change,
                    "revenue": adj_revenue,
                    "expenses": adj_expenses,
                    "net_income": adj_net,
                    "net_after_tax": adj_net_after_tax,
                    "margin": round(adj_net / adj_revenue * 100, 1) if adj_revenue > 0 else 0
                })
        
        # Break-even analysis
        fixed_costs_ratio = 0.4  # Assume 40% of expenses are fixed
        fixed_costs = base_expenses * fixed_costs_ratio
        variable_cost_ratio = (base_expenses * (1 - fixed_costs_ratio)) / base_revenue if base_revenue > 0 else 0.5
        contribution_margin = 1 - variable_cost_ratio
        break_even_revenue = fixed_costs / contribution_margin if contribution_margin > 0 else 0
        
        # =====================
        # MONTE CARLO SIMULATION
        # =====================
        num_simulations = 1000
        
        # Historical volatility (simplified - using last 12 months std dev)
        monthly_revenues = frappe.db.sql("""
            SELECT 
                DATE_FORMAT(gle.posting_date, '%%Y-%%m') as period,
                SUM(ABS(credit - debit)) as revenue
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE acc.root_type = 'Income'
                AND gle.posting_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                AND gle.company = %s
                AND gle.is_cancelled = 0
            GROUP BY DATE_FORMAT(gle.posting_date, '%%Y-%%m')
        """, (self.company,), as_dict=True)
        
        if monthly_revenues and len(monthly_revenues) > 1:
            rev_values = [float(r.revenue or 0) for r in monthly_revenues]
            rev_mean = np.mean(rev_values)
            rev_std = np.std(rev_values)
            rev_volatility = rev_std / rev_mean if rev_mean > 0 else 0.15
        else:
            rev_volatility = 0.15  # Default 15% volatility
        
        exp_volatility = rev_volatility * 0.7  # Expenses less volatile
        
        # Run simulations
        np.random.seed(42)  # For reproducibility
        simulated_revenues = np.random.normal(base_revenue, base_revenue * rev_volatility, num_simulations)
        simulated_expenses = np.random.normal(base_expenses, base_expenses * exp_volatility, num_simulations)
        simulated_net_income = simulated_revenues - simulated_expenses
        simulated_net_after_tax = np.where(
            simulated_net_income > 0,
            simulated_net_income * (1 - self.CORPORATE_TAX_RATE / 100),
            simulated_net_income
        )
        
        # Calculate percentiles
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        net_income_percentiles = {
            f"p{p}": float(np.percentile(simulated_net_after_tax, p))
            for p in percentiles
        }
        
        # Probability of outcomes
        prob_loss = float(np.sum(simulated_net_income < 0) / num_simulations * 100)
        prob_exceed_base = float(np.sum(simulated_net_after_tax > base_net_after_tax) / num_simulations * 100)
        
        # Distribution histogram data
        hist_bins = 20
        hist_counts, hist_edges = np.histogram(simulated_net_after_tax, bins=hist_bins)
        histogram_data = [
            {
                "bin_start": float(hist_edges[i]),
                "bin_end": float(hist_edges[i + 1]),
                "count": int(hist_counts[i]),
                "probability": float(hist_counts[i] / num_simulations * 100)
            }
            for i in range(len(hist_counts))
        ]
        
        # Named scenarios
        named_scenarios = [
            {
                "name": "Best Case (P95)",
                "description": "95th percentile outcome",
                "net_income": net_income_percentiles["p95"],
                "probability": 5
            },
            {
                "name": "Optimistic (P75)",
                "description": "75th percentile outcome",
                "net_income": net_income_percentiles["p75"],
                "probability": 25
            },
            {
                "name": "Base Case (P50)",
                "description": "Median expected outcome",
                "net_income": net_income_percentiles["p50"],
                "probability": 50
            },
            {
                "name": "Pessimistic (P25)",
                "description": "25th percentile outcome",
                "net_income": net_income_percentiles["p25"],
                "probability": 25
            },
            {
                "name": "Worst Case (P5)",
                "description": "5th percentile outcome",
                "net_income": net_income_percentiles["p5"],
                "probability": 5
            }
        ]
        
        return {
            "baseline": {
                "revenue": base_revenue,
                "expenses": base_expenses,
                "net_income": base_net_income,
                "tax": base_tax,
                "net_after_tax": base_net_after_tax,
                "margin": round(base_net_income / base_revenue * 100, 1) if base_revenue > 0 else 0
            },
            "sensitivity": {
                "scenarios": sensitivity_scenarios,
                "revenue_changes": revenue_changes,
                "expense_changes": expense_changes
            },
            "break_even": {
                "revenue": break_even_revenue,
                "current_revenue": base_revenue,
                "margin_of_safety": round((base_revenue - break_even_revenue) / base_revenue * 100, 1) if base_revenue > 0 else 0,
                "fixed_costs": fixed_costs,
                "contribution_margin": round(contribution_margin * 100, 1)
            },
            "monte_carlo": {
                "simulations": num_simulations,
                "revenue_volatility": round(rev_volatility * 100, 1),
                "expense_volatility": round(exp_volatility * 100, 1),
                "percentiles": net_income_percentiles,
                "mean": float(np.mean(simulated_net_after_tax)),
                "std": float(np.std(simulated_net_after_tax)),
                "probability_of_loss": round(prob_loss, 1),
                "probability_exceed_base": round(prob_exceed_base, 1),
                "histogram": histogram_data,
                "named_scenarios": named_scenarios
            }
        }
    
    # =========================================================================
    # PERIOD COMPARISON - YoY, QoQ, MoM
    # =========================================================================
    
    def _compare_periods(self) -> Dict[str, Any]:
        """Compare financial performance across periods"""
        today = datetime.now()
        
        # Define periods
        periods = {
            "current_month": {
                "start": today.replace(day=1).strftime('%Y-%m-%d'),
                "end": today.strftime('%Y-%m-%d'),
                "label": today.strftime('%b %Y')
            },
            "prior_month": {
                "start": (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d'),
                "end": (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d'),
                "label": (today.replace(day=1) - timedelta(days=1)).strftime('%b %Y')
            },
            "current_quarter": {
                "start": datetime(today.year, ((today.month - 1) // 3) * 3 + 1, 1).strftime('%Y-%m-%d'),
                "end": today.strftime('%Y-%m-%d'),
                "label": f"Q{((today.month - 1) // 3) + 1} {today.year}"
            },
            "prior_quarter": {
                "start": (datetime(today.year, ((today.month - 1) // 3) * 3 + 1, 1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d'),
                "end": (datetime(today.year, ((today.month - 1) // 3) * 3 + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d'),
                "label": f"Q{(((today.month - 1) // 3) or 4)} {today.year if (today.month - 1) // 3 > 0 else today.year - 1}"
            },
            "current_ytd": {
                "start": self.fiscal_year["start_date"],
                "end": today.strftime('%Y-%m-%d'),
                "label": f"YTD {today.year}"
            },
            "prior_ytd": {
                "start": (datetime.strptime(self.fiscal_year["start_date"], '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d'),
                "end": (today - timedelta(days=365)).strftime('%Y-%m-%d'),
                "label": f"YTD {today.year - 1}"
            }
        }
        
        def get_period_financials(start, end):
            result = frappe.db.sql("""
                SELECT 
                    SUM(CASE WHEN acc.root_type = 'Income' THEN ABS(credit - debit) ELSE 0 END) as revenue,
                    SUM(CASE WHEN acc.root_type = 'Expense' THEN ABS(debit - credit) ELSE 0 END) as expenses
                FROM `tabGL Entry` gle
                JOIN `tabAccount` acc ON gle.account = acc.name
                WHERE gle.posting_date BETWEEN %s AND %s
                    AND gle.company = %s
                    AND gle.is_cancelled = 0
            """, (start, end, self.company), as_dict=True)[0]
            
            revenue = float(result.revenue or 0)
            expenses = float(result.expenses or 0)
            return {
                "revenue": revenue,
                "expenses": expenses,
                "net_income": revenue - expenses,
                "margin": round((revenue - expenses) / revenue * 100, 1) if revenue > 0 else 0
            }
        
        # Calculate for each period
        period_data = {}
        for key, period in periods.items():
            period_data[key] = {
                **get_period_financials(period["start"], period["end"]),
                "label": period["label"]
            }
        
        # Calculate comparisons
        def calc_change(current, prior):
            if prior == 0:
                return 100 if current > 0 else 0
            return round((current - prior) / abs(prior) * 100, 1)
        
        mom_comparison = {
            "current": period_data["current_month"],
            "prior": period_data["prior_month"],
            "revenue_change": calc_change(period_data["current_month"]["revenue"], period_data["prior_month"]["revenue"]),
            "expense_change": calc_change(period_data["current_month"]["expenses"], period_data["prior_month"]["expenses"]),
            "net_income_change": calc_change(period_data["current_month"]["net_income"], period_data["prior_month"]["net_income"])
        }
        
        qoq_comparison = {
            "current": period_data["current_quarter"],
            "prior": period_data["prior_quarter"],
            "revenue_change": calc_change(period_data["current_quarter"]["revenue"], period_data["prior_quarter"]["revenue"]),
            "expense_change": calc_change(period_data["current_quarter"]["expenses"], period_data["prior_quarter"]["expenses"]),
            "net_income_change": calc_change(period_data["current_quarter"]["net_income"], period_data["prior_quarter"]["net_income"])
        }
        
        yoy_comparison = {
            "current": period_data["current_ytd"],
            "prior": period_data["prior_ytd"],
            "revenue_change": calc_change(period_data["current_ytd"]["revenue"], period_data["prior_ytd"]["revenue"]),
            "expense_change": calc_change(period_data["current_ytd"]["expenses"], period_data["prior_ytd"]["expenses"]),
            "net_income_change": calc_change(period_data["current_ytd"]["net_income"], period_data["prior_ytd"]["net_income"])
        }
        
        return {
            "period_data": period_data,
            "mom": mom_comparison,
            "qoq": qoq_comparison,
            "yoy": yoy_comparison,
            "summary": [
                {
                    "comparison": "Month over Month",
                    "revenue_change": mom_comparison["revenue_change"],
                    "expense_change": mom_comparison["expense_change"],
                    "net_income_change": mom_comparison["net_income_change"]
                },
                {
                    "comparison": "Quarter over Quarter",
                    "revenue_change": qoq_comparison["revenue_change"],
                    "expense_change": qoq_comparison["expense_change"],
                    "net_income_change": qoq_comparison["net_income_change"]
                },
                {
                    "comparison": "Year over Year",
                    "revenue_change": yoy_comparison["revenue_change"],
                    "expense_change": yoy_comparison["expense_change"],
                    "net_income_change": yoy_comparison["net_income_change"]
                }
            ]
        }
    
    # =========================================================================
    # BUDGET ANALYSIS - Placeholder
    # =========================================================================
    
    def _analyze_budget(self) -> Dict[str, Any]:
        """Budget analysis - placeholder for when budgets are configured"""
        # Check if budgets exist
        budget_count = frappe.db.count("Budget", {"company": self.company, "docstatus": 1})
        
        if budget_count == 0:
            return {
                "status": "not_configured",
                "message": "No budgets have been configured for this company. Create budgets in ERPNext to enable budget variance analysis.",
                "help_link": "/app/budget/new-budget-1",
                "has_data": False,
                "variance_by_account": [],
                "variance_by_cost_center": [],
                "total_budget": 0,
                "total_actual": 0,
                "total_variance": 0,
                "variance_pct": 0
            }
        
        # If budgets exist, analyze them
        fy_start = self.fiscal_year["start_date"]
        fy_end = self.fiscal_year["end_date"]
        
        # Get budget vs actual by account
        variance_data = frappe.db.sql("""
            SELECT 
                ba.account,
                SUM(ba.budget_amount) as budget_amount,
                COALESCE((
                    SELECT SUM(ABS(debit - credit))
                    FROM `tabGL Entry` gle
                    WHERE gle.account = ba.account
                        AND gle.posting_date BETWEEN %s AND %s
                        AND gle.company = %s
                        AND gle.is_cancelled = 0
                ), 0) as actual_amount
            FROM `tabBudget` b
            JOIN `tabBudget Account` ba ON ba.parent = b.name
            WHERE b.company = %s
                AND b.docstatus = 1
                AND b.fiscal_year = %s
            GROUP BY ba.account
        """, (fy_start, fy_end, self.company, self.company, self.fiscal_year["name"]), as_dict=True)
        
        variance_by_account = []
        total_budget = 0
        total_actual = 0
        
        for v in variance_data:
            budget = float(v.budget_amount or 0)
            actual = float(v.actual_amount or 0)
            variance = budget - actual
            variance_pct = (variance / budget * 100) if budget > 0 else 0
            
            variance_by_account.append({
                "account": v.account,
                "budget": budget,
                "actual": actual,
                "variance": variance,
                "variance_pct": round(variance_pct, 1),
                "status": "under" if variance > 0 else "over"
            })
            
            total_budget += budget
            total_actual += actual
        
        total_variance = total_budget - total_actual
        total_variance_pct = (total_variance / total_budget * 100) if total_budget > 0 else 0
        
        return {
            "status": "configured",
            "has_data": True,
            "variance_by_account": variance_by_account,
            "total_budget": total_budget,
            "total_actual": total_actual,
            "total_variance": total_variance,
            "variance_pct": round(total_variance_pct, 1),
            "budget_count": budget_count
        }


def run_strategic_finance_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """Helper function to run strategic finance intelligence"""
    model = StrategicFinanceIntelligence()
    if refresh:
        result = model.train()
    else:
        result = model.predict()
    # Sanitize numpy types for JSON serialization
    return sanitize_for_json(result)
