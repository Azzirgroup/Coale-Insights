# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Inventory Intelligence Agent
Specialized AI agent for Inventory dashboard insights
"""

from typing import Dict, List, Optional

from insights.agents import BaseIntelligenceAgent, AgentRegistry


@AgentRegistry.register("Inventory")
class InventoryIntelligenceAgent(BaseIntelligenceAgent):
    """AI agent specialized for Inventory Intelligence dashboard"""
    
    dashboard_type = "Inventory"
    agent_name = "Inventory Intelligence Agent"
    description = "AI assistant for stock analysis, warehouse optimization, and inventory management"
    
    def compress_context(self, full_context: Dict) -> Dict:
        """Compress inventory-specific context"""
        compressed = {
            "summary": self._extract_summary(full_context),
            "stock_overview": self._extract_stock_overview(full_context),
            "critical_items": self._extract_critical_items(full_context),
            "classification": self._extract_classification(full_context),
            "turnover_metrics": self._extract_turnover(full_context),
            "warehouse_status": self._extract_warehouse_status(full_context),
            "alerts": self._extract_alerts(full_context),
            "period": full_context.get("period", "Current Period")
        }
        return compressed
    
    def _extract_stock_overview(self, context: Dict) -> Dict:
        """Extract stock overview metrics"""
        overview = {}
        stock_keys = [
            "total_stock_value", "total_items", "total_sku",
            "low_stock_count", "out_of_stock_count", "excess_stock_count",
            "average_stock_days"
        ]
        
        for key in stock_keys:
            if key in context:
                overview[key] = context[key]
        
        if "stock_overview" in context and isinstance(context["stock_overview"], dict):
            overview.update(context["stock_overview"])
        
        return overview
    
    def _extract_critical_items(self, context: Dict) -> Dict:
        """Extract items needing attention"""
        critical = {
            "low_stock": [],
            "out_of_stock": [],
            "excess_stock": [],
            "slow_moving": []
        }
        
        if "low_stock_items" in context:
            critical["low_stock"] = context["low_stock_items"][:5]
        if "out_of_stock" in context:
            critical["out_of_stock"] = context["out_of_stock"][:5]
        if "excess_stock" in context:
            critical["excess_stock"] = context["excess_stock"][:5]
        if "slow_moving" in context or "dead_stock" in context:
            critical["slow_moving"] = context.get("slow_moving", context.get("dead_stock", []))[:5]
        
        return critical
    
    def _extract_classification(self, context: Dict) -> Dict:
        """Extract ABC/XYZ classification"""
        classification = {}
        
        if "abc_analysis" in context:
            classification["abc"] = context["abc_analysis"]
        if "xyz_analysis" in context:
            classification["xyz"] = context["xyz_analysis"]
        if "abc_xyz_matrix" in context:
            classification["matrix"] = context["abc_xyz_matrix"]
        
        return classification
    
    def _extract_turnover(self, context: Dict) -> Dict:
        """Extract turnover metrics"""
        turnover = {}
        turnover_keys = [
            "inventory_turnover", "turnover_ratio", "days_of_inventory",
            "average_age", "fifo_aging"
        ]
        
        for key in turnover_keys:
            if key in context:
                turnover[key] = context[key]
        
        return turnover
    
    def _extract_warehouse_status(self, context: Dict) -> Dict:
        """Extract warehouse utilization data"""
        warehouse = {}
        
        if "warehouse_utilization" in context:
            warehouse["utilization"] = context["warehouse_utilization"]
        if "stock_by_warehouse" in context:
            warehouse["distribution"] = context["stock_by_warehouse"]
        if "transfer_recommendations" in context:
            warehouse["transfers"] = context["transfer_recommendations"][:3]
        
        return warehouse
    
    def _get_default_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Get default system prompt for inventory agent"""
        ctx_str = ""
        if context:
            import json
            ctx_str = json.dumps(context, indent=2, default=str)
        
        return f"""You are a specialized Inventory Intelligence AI assistant for ERPNext.

## Your Expertise:
- Stock level optimization and reorder point analysis
- ABC/XYZ classification and inventory segmentation
- Inventory turnover and days of inventory analysis
- Warehouse utilization and transfer recommendations
- FIFO aging and obsolescence risk assessment
- Dead stock identification and clearance strategies
- Demand forecasting and safety stock calculations

## Current Dashboard Data:
{ctx_str if ctx_str else "No data available"}

## Guidelines:
- Provide specific recommendations for stock optimization
- Reference actual stock levels, turnover rates, and aging data
- Identify items requiring immediate attention (stockouts, excess, aging)
- Suggest reorder quantities based on demand patterns
- Recommend warehouse transfers to optimize distribution
- Calculate financial impact of inventory issues
- Use markdown formatting with bullet points for clarity

## Response Format:
- Start with current stock health assessment
- Highlight critical items needing immediate action
- Provide specific quantities and values
- Recommend 2-3 actionable optimizations"""
    
    def _get_default_quick_actions(self) -> List[Dict]:
        """Get default quick actions for inventory dashboard"""
        return [
            {
                "label": "📦 Stock Alerts",
                "prompt_template": "Which items need immediate attention due to low stock, stockouts, or excess inventory?",
                "icon": "package"
            },
            {
                "label": "🔄 Reorder Recommendations",
                "prompt_template": "What items should be reordered now? Provide recommended quantities based on demand patterns.",
                "icon": "refresh-cw"
            },
            {
                "label": "📉 Slow Moving Items",
                "prompt_template": "Identify slow-moving or dead stock items. What clearance strategies do you recommend?",
                "icon": "trending-down"
            },
            {
                "label": "🏭 Warehouse Optimization",
                "prompt_template": "How can we optimize warehouse utilization and stock distribution across locations?",
                "icon": "home"
            },
            {
                "label": "📊 Turnover Analysis",
                "prompt_template": "Analyze inventory turnover rates. Which items or categories need attention?",
                "icon": "activity"
            }
        ]
    
    def _get_default_routing_keywords(self) -> List[str]:
        """Get default routing keywords for inventory queries"""
        return [
            "stock", "inventory", "warehouse", "reorder", "turnover",
            "abc", "xyz", "aging", "fifo", "dead stock", "stockout",
            "excess", "bin", "quantity", "storage", "sku"
        ]
