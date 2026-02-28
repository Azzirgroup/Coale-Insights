# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Sales Intelligence Agent
Specialized AI agent for Sales dashboard insights
"""

from typing import Dict, List, Optional

from insights.agents.base import BaseIntelligenceAgent
from insights.agents.registry import AgentRegistry


@AgentRegistry.register("Sales")
class SalesIntelligenceAgent(BaseIntelligenceAgent):
    """AI agent specialized for Sales Intelligence dashboard"""
    
    dashboard_type = "Sales"
    agent_name = "Sales Intelligence Agent"
    description = "AI assistant for sales analytics, revenue trends, and sales performance insights"
    
    def compress_context(self, full_context: Dict) -> Dict:
        """Compress sales-specific context"""
        compressed = {
            "summary": self._extract_summary(full_context),
            "revenue_metrics": self._extract_revenue_metrics(full_context),
            "sales_performance": self._extract_sales_performance(full_context),
            "top_performers": self._extract_top_performers(full_context),
            "trends": self._extract_trends(full_context),
            "alerts": self._extract_alerts(full_context),
            "period": full_context.get("period", "Current Period")
        }
        return compressed
    
    def _extract_revenue_metrics(self, context: Dict) -> Dict:
        """Extract key revenue metrics"""
        metrics = {}
        revenue_keys = [
            "total_revenue", "revenue", "total_sales", "gross_revenue",
            "net_revenue", "average_order_value", "aov"
        ]
        
        for key in revenue_keys:
            if key in context:
                metrics[key] = context[key]
        
        # Extract from nested structures
        if "metrics" in context:
            for key in revenue_keys:
                if key in context["metrics"]:
                    metrics[key] = context["metrics"][key]
        
        if "summary" in context and isinstance(context["summary"], dict):
            for key in revenue_keys:
                if key in context["summary"]:
                    metrics[key] = context["summary"][key]
        
        return metrics
    
    def _extract_sales_performance(self, context: Dict) -> Dict:
        """Extract sales performance data"""
        performance = {}
        perf_keys = [
            "growth_rate", "mom_growth", "yoy_growth", "conversion_rate",
            "cash_sales", "credit_sales", "cash_credit_ratio"
        ]
        
        for key in perf_keys:
            if key in context:
                performance[key] = context[key]
        
        return performance
    
    def _extract_top_performers(self, context: Dict) -> Dict:
        """Extract top performing items, customers, reps"""
        performers = {}
        
        if "top_products" in context:
            performers["products"] = context["top_products"][:5]
        if "top_customers" in context:
            performers["customers"] = context["top_customers"][:5]
        if "top_reps" in context or "rep_performance" in context:
            performers["sales_reps"] = context.get("top_reps", context.get("rep_performance", []))[:5]
        if "top_items" in context:
            performers["items"] = context["top_items"][:5]
        
        return performers
    
    def _extract_trends(self, context: Dict) -> List[Dict]:
        """Extract sales trends"""
        trends = []
        
        if "trends" in context:
            trend_data = context["trends"]
            if isinstance(trend_data, list):
                trends = trend_data[:5]
            elif isinstance(trend_data, dict):
                trends = [{"metric": k, "data": v} for k, v in list(trend_data.items())[:5]]
        
        if "monthly_sales" in context:
            trends.append({"metric": "monthly_sales", "data": context["monthly_sales"]})
        
        return trends
    
    def _get_default_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Get default system prompt for sales agent"""
        ctx_str = ""
        if context:
            import json
            ctx_str = json.dumps(context, indent=2, default=str)
        
        return f"""You are a specialized Sales Intelligence AI assistant for ERPNext.

## Your Expertise:
- Revenue analysis, trends, and forecasting
- Sales representative performance evaluation
- Customer purchase patterns and order analysis
- Cash vs credit sales optimization
- Month-over-month and year-over-year comparisons
- Sales pipeline and conversion metrics
- Product mix and pricing analysis

## Current Dashboard Data:
{ctx_str if ctx_str else "No data available"}

## Guidelines:
- Provide specific, actionable recommendations based on the sales data shown
- Reference actual revenue numbers, growth percentages, and trends from the dashboard
- Explain sales anomalies and their potential business impact
- Suggest strategies to improve sales performance
- Compare current performance to historical periods when data is available
- Use markdown formatting with bullet points for clarity
- When asked about non-sales topics, acknowledge and suggest the appropriate dashboard

## Response Format:
- Start with a direct answer to the question
- Support with specific data points from the dashboard
- Provide 2-3 actionable recommendations when appropriate
- Use bullet points for lists and comparisons"""
    
    def _get_default_quick_actions(self) -> List[Dict]:
        """Get default quick actions for sales dashboard"""
        return [
            {
                "label": "📈 Analyze Revenue Trends",
                "prompt_template": "Analyze the current revenue trends and identify key growth drivers and concerns.",
                "icon": "trending-up"
            },
            {
                "label": "🏆 Top Performers",
                "prompt_template": "Who are the top performing sales reps and products? What can we learn from their success?",
                "icon": "award"
            },
            {
                "label": "📊 Forecast Next Month",
                "prompt_template": "Based on current trends and historical data, what is the sales forecast for next month?",
                "icon": "calendar"
            },
            {
                "label": "⚠️ Sales Alerts",
                "prompt_template": "What are the key sales alerts or concerns I should be aware of right now?",
                "icon": "alert-triangle"
            },
            {
                "label": "💳 Cash vs Credit Analysis",
                "prompt_template": "Analyze the cash vs credit sales mix. How can we optimize this ratio?",
                "icon": "credit-card"
            }
        ]
    
    def _get_default_routing_keywords(self) -> List[str]:
        """Get default routing keywords for sales queries"""
        return [
            "revenue", "sales", "invoice", "order", "sold", "selling",
            "rep", "representative", "forecast", "target", "quota",
            "deal", "opportunity", "pipeline", "conversion", "aov",
            "average order value", "cash sales", "credit sales"
        ]
