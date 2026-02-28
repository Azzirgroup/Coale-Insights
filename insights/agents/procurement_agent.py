# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Procurement Intelligence Agent
Specialized AI agent for Procurement dashboard insights
"""

from typing import Dict, List, Optional

from insights.agents.base import BaseIntelligenceAgent
from insights.agents.registry import AgentRegistry


@AgentRegistry.register("Procurement")
class ProcurementIntelligenceAgent(BaseIntelligenceAgent):
    """AI agent specialized for Procurement Intelligence dashboard"""
    
    dashboard_type = "Procurement"
    agent_name = "Procurement Intelligence Agent"
    description = "AI assistant for supplier analysis, spend management, and procurement optimization"
    
    def compress_context(self, full_context: Dict) -> Dict:
        """Compress procurement-specific context"""
        compressed = {
            "summary": self._extract_summary(full_context),
            "spend_overview": self._extract_spend_overview(full_context),
            "supplier_performance": self._extract_supplier_performance(full_context),
            "price_analysis": self._extract_price_analysis(full_context),
            "pending_orders": self._extract_pending_orders(full_context),
            "savings_opportunities": self._extract_savings(full_context),
            "alerts": self._extract_alerts(full_context),
            "period": full_context.get("period", "Current Period")
        }
        return compressed
    
    def _extract_spend_overview(self, context: Dict) -> Dict:
        """Extract spend overview metrics"""
        spend = {}
        spend_keys = [
            "total_spend", "total_purchases", "average_po_value",
            "spend_by_category", "spend_by_supplier", "mom_spend_change"
        ]
        
        for key in spend_keys:
            if key in context:
                spend[key] = context[key]
        
        if "spend_analysis" in context and isinstance(context["spend_analysis"], dict):
            spend.update(context["spend_analysis"])
        
        return spend
    
    def _extract_supplier_performance(self, context: Dict) -> Dict:
        """Extract supplier performance data"""
        performance = {
            "top_suppliers": [],
            "underperforming": [],
            "metrics": {}
        }
        
        if "top_suppliers" in context:
            performance["top_suppliers"] = context["top_suppliers"][:5]
        if "supplier_performance" in context:
            performance["metrics"] = context["supplier_performance"]
        if "underperforming_suppliers" in context:
            performance["underperforming"] = context["underperforming_suppliers"][:5]
        if "supplier_scores" in context:
            performance["scores"] = context["supplier_scores"]
        
        return performance
    
    def _extract_price_analysis(self, context: Dict) -> Dict:
        """Extract price variance and trends"""
        prices = {}
        
        if "price_variance" in context:
            prices["variance"] = context["price_variance"]
        if "price_trends" in context:
            prices["trends"] = context["price_trends"]
        if "price_benchmarks" in context:
            prices["benchmarks"] = context["price_benchmarks"]
        
        return prices
    
    def _extract_pending_orders(self, context: Dict) -> Dict:
        """Extract pending order information"""
        pending = {}
        
        if "pending_orders" in context:
            pending["orders"] = context["pending_orders"][:5]
        if "overdue_deliveries" in context:
            pending["overdue"] = context["overdue_deliveries"][:5]
        if "pending_value" in context:
            pending["total_value"] = context["pending_value"]
        
        return pending
    
    def _extract_savings(self, context: Dict) -> List[Dict]:
        """Extract savings opportunities"""
        savings = []
        
        if "savings_opportunities" in context:
            savings = context["savings_opportunities"][:5]
        if "consolidation_opportunities" in context:
            savings.extend(context["consolidation_opportunities"][:3])
        
        return savings
    
    def _get_default_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Get default system prompt for procurement agent"""
        ctx_str = ""
        if context:
            import json
            ctx_str = json.dumps(context, indent=2, default=str)
        
        return f"""You are a specialized Procurement Intelligence AI assistant for ERPNext.

## Your Expertise:
- Supplier performance evaluation and scoring
- Spend analysis and cost optimization
- Purchase price variance and benchmarking
- Vendor consolidation opportunities
- Lead time analysis and reliability tracking
- Contract compliance and savings identification
- Category management strategies

## Current Dashboard Data:
{ctx_str if ctx_str else "No data available"}

## Guidelines:
- Provide actionable supplier recommendations
- Reference specific spend amounts, price variances, and supplier metrics
- Identify cost reduction opportunities with estimated savings
- Suggest supplier diversification or consolidation strategies
- Highlight delivery performance issues and their business impact
- Compare supplier performance against benchmarks
- Use markdown formatting with bullet points for clarity

## Response Format:
- Start with spend summary and key insights
- Highlight supplier issues requiring attention
- Quantify savings opportunities where possible
- Recommend 2-3 specific procurement optimizations"""
    
    def _get_default_quick_actions(self) -> List[Dict]:
        """Get default quick actions for procurement dashboard"""
        return [
            {
                "label": "⭐ Supplier Performance",
                "prompt_template": "How are our key suppliers performing? Who are the top performers and who needs attention?",
                "icon": "star"
            },
            {
                "label": "💰 Cost Savings",
                "prompt_template": "Where are the opportunities for cost savings in procurement? Quantify potential savings.",
                "icon": "dollar-sign"
            },
            {
                "label": "📊 Spend Analysis",
                "prompt_template": "Analyze our spending patterns by category and supplier. Where are we overspending?",
                "icon": "pie-chart"
            },
            {
                "label": "⏱️ Lead Time Issues",
                "prompt_template": "Are there any supplier lead time issues affecting our operations? Which suppliers are consistently late?",
                "icon": "clock"
            },
            {
                "label": "🔄 Consolidation",
                "prompt_template": "Are there opportunities to consolidate suppliers or negotiate better terms?",
                "icon": "minimize"
            }
        ]
    
    def _get_default_routing_keywords(self) -> List[str]:
        """Get default routing keywords for procurement queries"""
        return [
            "supplier", "vendor", "procurement", "purchase", "buying",
            "sourcing", "spend", "contract", "lead time", "delivery",
            "price variance", "po", "purchase order"
        ]
