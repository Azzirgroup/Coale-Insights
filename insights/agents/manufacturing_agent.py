"""
Manufacturing Intelligence Agent

AI agent specialized in manufacturing operations, production efficiency,
and operational intelligence insights.

Extends BaseIntelligenceAgent for consistent behavior with all other
dashboard agents (model fallback, quota, config, etc.).
"""

from typing import Dict, List, Optional

from insights.agents.base import BaseIntelligenceAgent
from insights.agents.registry import AgentRegistry


@AgentRegistry.register("Manufacturing")
class ManufacturingIntelligenceAgent(BaseIntelligenceAgent):
    """AI agent specialized for Manufacturing Intelligence dashboard"""

    dashboard_type = "Manufacturing"
    agent_name = "Manufacturing Intelligence Agent"
    description = "AI assistant for manufacturing operations, production efficiency, and quality analysis"

    def __init__(self):
        super().__init__()
        try:
            from insights.ml.manufacturing_intelligence import ManufacturingIntelligence
            self.manufacturing_intel = ManufacturingIntelligence()
        except Exception:
            self.manufacturing_intel = None

    def execute(self, query, session_id, context=None, conversation_history=None):
        """Gather fresh manufacturing data if no context provided, then delegate to base."""
        if not context and self.manufacturing_intel:
            try:
                manufacturing_data = self.manufacturing_intel.get_manufacturing_overview("YTD")
                context = self.compress_context(manufacturing_data)
            except Exception:
                context = {}
        return super().execute(query, session_id, context, conversation_history)

    def compress_context(self, full_context: Dict) -> Dict:
        """Compress manufacturing-specific context for token optimization."""
        oee = full_context.get("oee_analysis", {})
        production = full_context.get("production_metrics", {})
        quality = full_context.get("quality_metrics", {})
        capacity = full_context.get("capacity_analysis", {})
        cost = full_context.get("cost_analysis", {})

        key_metrics = {
            "oee_score_pct": oee.get("oee_score_pct", 0),
            "oee_rating": oee.get("oee_rating", "unknown"),
            "availability_pct": oee.get("availability_pct", 0),
            "performance_pct": oee.get("performance_pct", 0),
            "quality_pct": oee.get("quality_pct", 0),
            "total_work_orders": production.get("total_work_orders", 0),
            "completed_work_orders": production.get("completed_work_orders", 0),
            "defect_rate_pct": quality.get("defect_rate_pct", 0),
            "first_pass_yield_pct": quality.get("first_pass_yield_pct", 0),
            "capacity_utilization_pct": capacity.get("utilization_pct", 0),
            "production_cost_per_unit": cost.get("cost_per_unit", 0),
        }

        return {
            "summary": f"Manufacturing: OEE {key_metrics['oee_score_pct']}% ({key_metrics['oee_rating']}), "
                       f"capacity {key_metrics['capacity_utilization_pct']}%, "
                       f"defect rate {key_metrics['defect_rate_pct']}%",
            "key_metrics": key_metrics,
            "downtime_analysis": oee.get("downtime_analysis", {}),
            "workstation_performance": capacity.get("workstation_performance", {}),
            "quality_trends": quality.get("trends", []),
            "period": full_context.get("period", "YTD"),
        }

    def _get_default_system_prompt(self, context: Optional[Dict] = None) -> str:
        ctx_str = ""
        if context:
            import json
            ctx_str = json.dumps(context, indent=2, default=str)

        return f"""You are a Manufacturing Intelligence AI assistant for ERPNext. Your expertise includes:

## Your Expertise:
- Overall Equipment Effectiveness (OEE) analysis
- Production efficiency and throughput optimization
- Quality control and defect analysis
- Capacity planning and utilization
- Work order management and scheduling
- Manufacturing cost analysis
- Equipment maintenance and downtime tracking
- Lean manufacturing and waste reduction

## Current Dashboard Data:
{ctx_str if ctx_str else "No data available"}

## Guidelines:
- Provide specific production insights with metrics
- Reference OEE scores, capacity utilization, and quality rates
- Identify bottlenecks and efficiency opportunities
- Suggest strategies for improving manufacturing performance
- Include actionable recommendations with expected impact
- Use markdown formatting with bullet points for clarity

## Response Format:
- Start with overall manufacturing performance assessment
- Highlight key metrics (OEE, quality, capacity)
- Identify bottlenecks and areas of concern
- Recommend 2-3 specific actions for improvement"""

    def _get_default_quick_actions(self) -> List[Dict]:
        return [
            {
                "label": "Production Overview",
                "prompt_template": "Give me an overview of production performance and OEE.",
                "icon": "home",
            },
            {
                "label": "Equipment Status",
                "prompt_template": "What is the status of our equipment and any maintenance concerns?",
                "icon": "settings",
            },
            {
                "label": "Quality Metrics",
                "prompt_template": "Analyze our quality control metrics and defect rates.",
                "icon": "check-circle",
            },
            {
                "label": "Efficiency Analysis",
                "prompt_template": "How can we improve manufacturing efficiency?",
                "icon": "trending-up",
            },
        ]

    def _get_default_routing_keywords(self) -> List[str]:
        return [
            "oee", "overall equipment effectiveness", "production efficiency",
            "manufacturing", "production", "work orders", "shop floor",
            "capacity", "utilization", "throughput", "output",
            "quality", "defects", "first pass yield", "rework", "scrap",
            "quality control", "inspection", "workstation", "machines",
            "equipment", "bottleneck", "downtime", "maintenance",
            "breakdown", "lean", "waste", "optimization",
            "production planning", "scheduling", "capacity planning",
            "manufacturing cost", "production cost", "cost per unit",
        ]
