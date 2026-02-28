# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Customer Intelligence Agent
Specialized AI agent for Customer dashboard insights
"""

from typing import Dict, List, Optional

from insights.agents.base import BaseIntelligenceAgent
from insights.agents.registry import AgentRegistry


@AgentRegistry.register("Customer")
class CustomerIntelligenceAgent(BaseIntelligenceAgent):
    """AI agent specialized for Customer Intelligence dashboard"""
    
    dashboard_type = "Customer"
    agent_name = "Customer Intelligence Agent"
    description = "AI assistant for customer analytics, CLV analysis, and retention strategies"
    
    def compress_context(self, full_context: Dict) -> Dict:
        """Compress customer-specific context"""
        compressed = {
            "summary": self._extract_summary(full_context),
            "customer_overview": self._extract_customer_overview(full_context),
            "clv_analysis": self._extract_clv(full_context),
            "churn_risk": self._extract_churn_risk(full_context),
            "segmentation": self._extract_segmentation(full_context),
            "top_customers": self._extract_top_customers(full_context),
            "geographic_data": self._extract_geographic(full_context),
            "alerts": self._extract_alerts(full_context),
            "period": full_context.get("period", "Current Period")
        }
        return compressed
    
    def _extract_customer_overview(self, context: Dict) -> Dict:
        """Extract customer overview metrics"""
        overview = {}
        overview_keys = [
            "total_customers", "active_customers", "new_customers",
            "customer_growth_rate", "average_customer_value", "retention_rate"
        ]
        
        for key in overview_keys:
            if key in context:
                overview[key] = context[key]
        
        return overview
    
    def _extract_clv(self, context: Dict) -> Dict:
        """Extract CLV analysis data"""
        clv = {}
        
        if "average_clv" in context:
            clv["average"] = context["average_clv"]
        if "clv_distribution" in context:
            clv["distribution"] = context["clv_distribution"]
        if "clv_by_segment" in context:
            clv["by_segment"] = context["clv_by_segment"]
        if "high_value_customers" in context:
            clv["high_value"] = context["high_value_customers"][:5]
        
        return clv
    
    def _extract_churn_risk(self, context: Dict) -> Dict:
        """Extract churn risk analysis"""
        churn = {}
        
        if "churn_rate" in context:
            churn["rate"] = context["churn_rate"]
        if "at_risk_customers" in context:
            churn["at_risk"] = context["at_risk_customers"][:5]
        if "churn_prediction" in context:
            churn["predicted"] = context["churn_prediction"]
        if "inactive_customers" in context:
            churn["inactive"] = context["inactive_customers"][:5]
        
        return churn
    
    def _extract_segmentation(self, context: Dict) -> Dict:
        """Extract customer segmentation data"""
        segments = {}
        
        if "customer_segments" in context:
            segments["breakdown"] = context["customer_segments"]
        if "rfm_analysis" in context:
            segments["rfm"] = context["rfm_analysis"]
        if "segment_performance" in context:
            segments["performance"] = context["segment_performance"]
        
        return segments
    
    def _extract_top_customers(self, context: Dict) -> List[Dict]:
        """Extract top customers"""
        top = []
        
        if "top_customers" in context:
            top = context["top_customers"][:5]
        elif "best_customers" in context:
            top = context["best_customers"][:5]
        
        return top
    
    def _extract_geographic(self, context: Dict) -> Dict:
        """Extract geographic distribution"""
        geo = {}
        
        if "customers_by_territory" in context:
            geo["territory"] = context["customers_by_territory"]
        if "customers_by_region" in context:
            geo["region"] = context["customers_by_region"]
        if "geographic_distribution" in context:
            geo["distribution"] = context["geographic_distribution"]
        
        return geo
    
    def _get_default_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Get default system prompt for customer agent"""
        ctx_str = ""
        if context:
            import json
            ctx_str = json.dumps(context, indent=2, default=str)
        
        return f"""You are a specialized Customer Intelligence AI assistant for ERPNext.

## Your Expertise:
- Customer Lifetime Value (CLV) analysis and optimization
- Churn prediction and prevention strategies
- Customer segmentation (RFM analysis, behavioral segments)
- Cohort analysis and retention metrics
- Geographic and demographic analysis
- Customer health scoring and engagement tracking
- Customer acquisition cost (CAC) analysis

## Current Dashboard Data:
{ctx_str if ctx_str else "No data available"}

## Guidelines:
- Provide actionable customer retention strategies
- Reference specific CLV values, churn rates, and segment data
- Identify at-risk customers requiring immediate attention
- Suggest personalized engagement approaches by segment
- Explain customer metrics and their business implications
- Recommend strategies to increase customer lifetime value
- Consider geographic and demographic factors
- Use markdown formatting with bullet points for clarity

## Response Format:
- Start with customer health overview
- Highlight at-risk customers or segments
- Provide specific retention recommendations
- Suggest 2-3 actions to improve customer metrics"""
    
    def _get_default_quick_actions(self) -> List[Dict]:
        """Get default quick actions for customer dashboard"""
        return [
            {
                "label": "⚠️ At-Risk Customers",
                "prompt_template": "Which customers are at risk of churning? What specific actions should we take to retain them?",
                "icon": "alert-triangle"
            },
            {
                "label": "💎 Top Customers",
                "prompt_template": "Who are our most valuable customers by CLV? How do we retain and grow these relationships?",
                "icon": "gem"
            },
            {
                "label": "📊 Segment Analysis",
                "prompt_template": "Analyze our customer segments. Which segments are growing and which need attention?",
                "icon": "users"
            },
            {
                "label": "📈 Growth Opportunities",
                "prompt_template": "Which customer segments or territories offer the best growth opportunities?",
                "icon": "trending-up"
            },
            {
                "label": "🔄 Retention Strategy",
                "prompt_template": "What strategies should we implement to improve customer retention and reduce churn?",
                "icon": "refresh-cw"
            }
        ]
    
    def _get_default_routing_keywords(self) -> List[str]:
        """Get default routing keywords for customer queries"""
        return [
            "customer", "client", "clv", "lifetime value", "churn",
            "retention", "segment", "cohort", "loyalty", "nps",
            "satisfaction", "engagement", "acquisition", "rfm"
        ]
