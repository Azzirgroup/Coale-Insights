"""
Executive Intelligence Agent

AI agent specialized in C-suite level insights, cross-departmental analysis,
and strategic recommendations.

Extends BaseIntelligenceAgent for consistent behavior with all other
dashboard agents (model fallback, quota, config, etc.).
"""

from typing import Dict, List, Optional

from insights.agents.base import BaseIntelligenceAgent
from insights.agents.registry import AgentRegistry


@AgentRegistry.register("Executive")
class ExecutiveIntelligenceAgent(BaseIntelligenceAgent):
    """AI agent specialized for Executive Intelligence dashboard"""

    dashboard_type = "Executive"
    agent_name = "Executive Intelligence Agent"
    description = "AI assistant for C-suite level business intelligence and strategic insights"

    def __init__(self):
        super().__init__()
        try:
            from insights.ml.executive_intelligence import ExecutiveIntelligence
            self.executive_intel = ExecutiveIntelligence()
        except Exception:
            self.executive_intel = None

    def execute(self, query, session_id, context=None, conversation_history=None):
        """Gather fresh executive data if no context provided, then delegate to base."""
        if not context and self.executive_intel:
            try:
                executive_data = self.executive_intel.get_executive_summary("YTD")
                context = self.compress_context(executive_data)
            except Exception:
                context = {}
        return super().execute(query, session_id, context, conversation_history)

    def compress_context(self, full_context: Dict) -> Dict:
        """Compress executive-specific context for token optimization."""
        kpis = full_context.get("kpis", {})
        alerts = full_context.get("alerts", [])
        health_score = full_context.get("business_health_score", {})

        # Extract key metrics across departments
        key_metrics = {}
        for dept_key in ["financial", "sales", "customer", "operations", "risk"]:
            dept = kpis.get(dept_key, {})
            for metric_name, metric_data in dept.items():
                if isinstance(metric_data, dict) and "value" in metric_data:
                    key_metrics[f"{dept_key}_{metric_name}"] = {
                        "value": metric_data.get("value", 0),
                        "rag_status": metric_data.get("rag_status", "amber"),
                    }
                    if len(key_metrics) >= 12:
                        break

        total_kpis = len(key_metrics)
        green_kpis = sum(1 for m in key_metrics.values() if m.get("rag_status") == "green")
        red_kpis = sum(1 for m in key_metrics.values() if m.get("rag_status") == "red")

        critical_alerts = [a for a in alerts if a.get("priority") == "critical"]
        high_alerts = [a for a in alerts if a.get("priority") == "high"]

        return {
            "summary": f"Business health: {health_score.get('overall_score', 0)}/100 "
                       f"({health_score.get('overall_rag', 'amber')}), "
                       f"{green_kpis}/{total_kpis} KPIs green, "
                       f"{len(critical_alerts)} critical alerts",
            "overall_health_score": health_score.get("overall_score", 0),
            "overall_rag": health_score.get("overall_rag", "amber"),
            "key_metrics": key_metrics,
            "department_scores": health_score.get("department_scores", {}),
            "priority_alerts": (critical_alerts + high_alerts)[:5],
            "period": full_context.get("period", "YTD"),
        }

    def _get_default_system_prompt(self, context: Optional[Dict] = None) -> str:
        ctx_str = ""
        if context:
            import json
            ctx_str = json.dumps(context, indent=2, default=str)

        return f"""You are an Executive AI Assistant specializing in C-suite level business intelligence and strategic insights. Your role is to:

1. **Executive Communication**: Communicate at a CEO/board level - concise, strategic, action-oriented
2. **Cross-Departmental Analysis**: Identify patterns and relationships across Finance, Sales, Operations, Customer, and Risk domains
3. **Strategic Focus**: Emphasize strategic implications over tactical details
4. **Data-Driven Insights**: Base all recommendations on quantitative KPIs and trends
5. **Risk Awareness**: Highlight business risks and mitigation strategies
6. **Forward-Looking**: Provide predictive insights and strategic recommendations

## Current Dashboard Data:
{ctx_str if ctx_str else "No data available"}

## Guidelines:
- Use executive language and business terminology
- Lead with key insights and bottom-line impact
- Structure responses with clear sections: Summary, Key Issues, Recommendations
- Include specific metrics and targets when available
- Flag critical alerts that need immediate attention
- Use markdown formatting for clarity

## Response Format:
- Start with overall business health assessment
- Highlight key metrics and their implications
- Identify risks and opportunities
- Recommend 2-3 specific strategic actions"""

    def _get_default_quick_actions(self) -> List[Dict]:
        return [
            {
                "label": "Business Overview",
                "prompt_template": "Give me a high-level overview of business health and performance.",
                "icon": "activity",
            },
            {
                "label": "Strategic KPIs",
                "prompt_template": "What are our key strategic KPIs and how are they trending?",
                "icon": "target",
            },
            {
                "label": "Executive Alerts",
                "prompt_template": "What critical business alerts need my attention?",
                "icon": "alert-triangle",
            },
            {
                "label": "Department Performance",
                "prompt_template": "Compare department performances and highlight areas needing focus.",
                "icon": "bar-chart-2",
            },
        ]

    def _get_default_routing_keywords(self) -> List[str]:
        return [
            "CEO", "executive", "board", "strategy", "KPI", "performance",
            "summary", "overview", "dashboard", "health", "score",
            "business performance", "company performance", "overall",
            "cross-departmental", "enterprise", "organization",
            "revenue", "profitability", "growth", "margin", "cash flow",
            "risk", "compliance", "governance", "operations", "efficiency",
            "strategic", "planning", "forecast",
        ]
