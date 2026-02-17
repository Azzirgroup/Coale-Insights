"""
HR Intelligence Agent

AI agent specialized in workforce analytics, talent management,
and human resources optimization insights.

Extends BaseIntelligenceAgent for consistent behavior with all other
dashboard agents (model fallback, quota, config, etc.).
"""

from typing import Dict, List, Optional

from insights.agents import BaseIntelligenceAgent, AgentRegistry


@AgentRegistry.register("HR")
class HRIntelligenceAgent(BaseIntelligenceAgent):
    """AI agent specialized for HR Intelligence dashboard"""

    dashboard_type = "HR"
    agent_name = "HR Intelligence Agent"
    description = "AI assistant for workforce analytics, talent management, and HR optimization"

    def __init__(self):
        super().__init__()
        try:
            from insights.ml.hr_intelligence import HRIntelligence
            self.hr_intel = HRIntelligence()
        except Exception:
            self.hr_intel = None

    def execute(self, query, session_id, context=None, conversation_history=None):
        """Gather fresh HR data if no context provided, then delegate to base."""
        if not context and self.hr_intel:
            try:
                hr_data = self.hr_intel.get_hr_overview("YTD")
                context = self.compress_context(hr_data)
            except Exception:
                context = {}
        return super().execute(query, session_id, context, conversation_history)

    def compress_context(self, full_context: Dict) -> Dict:
        """Compress HR-specific context for token optimization."""
        headcount = full_context.get("headcount_metrics", {})
        attrition = full_context.get("attrition_metrics", {})
        payroll = full_context.get("payroll_metrics", {})
        attendance = full_context.get("attendance_metrics", {})
        engagement = full_context.get("engagement_indicators", {})
        attrition_risk = full_context.get("attrition_risk", {})

        key_metrics = {
            "total_employees": headcount.get("total_employees", 0),
            "headcount_growth_pct": headcount.get("growth_rate_pct", 0),
            "attrition_rate_pct": attrition.get("attrition_rate_pct", 0),
            "retention_rate_pct": 100 - attrition.get("attrition_rate_pct", 0),
            "attendance_rate_pct": attendance.get("attendance_rate_pct", 0),
            "engagement_score": engagement.get("engagement_score", 0),
            "engagement_level": engagement.get("engagement_level", "unknown"),
            "average_salary": payroll.get("average_salary", 0),
            "total_payroll_cost": payroll.get("total_payroll_cost", 0),
            "risk_level": attrition_risk.get("risk_level", "unknown"),
        }

        workforce_health = "good" if (
            attendance.get("attendance_rate_pct", 0) > 92
            and attrition.get("attrition_rate_pct", 0) < 15
        ) else "needs_attention"

        return {
            "summary": f"Workforce: {key_metrics['total_employees']} employees, "
                       f"attrition {key_metrics['attrition_rate_pct']:.1f}%, "
                       f"health: {workforce_health}",
            "key_metrics": key_metrics,
            "workforce_health": workforce_health,
            "department_breakdown": headcount.get("department_breakdown", {}),
            "attrition_details": {
                k: v for k, v in attrition.items()
                if isinstance(v, (int, float, str)) and len(str(k)) < 40
            },
            "period": full_context.get("period", "YTD"),
        }

    def _get_default_system_prompt(self, context: Optional[Dict] = None) -> str:
        ctx_str = ""
        if context:
            import json
            ctx_str = json.dumps(context, indent=2, default=str)

        return f"""You are an HR AI Specialist focused on workforce analytics and human resources management. Your expertise includes:

**Core HR Domains:**
1. **Workforce Analytics**: Headcount trends, departmental distribution, growth patterns
2. **Talent Retention**: Attrition analysis, retention strategies, exit pattern identification
3. **Performance Management**: Attendance patterns, productivity indicators, engagement metrics
4. **Compensation Analysis**: Payroll optimization, salary benchmarking, pay equity
5. **Workforce Planning**: Hiring forecasts, succession planning, skill gap analysis
6. **Employee Engagement**: Culture metrics, satisfaction indicators, retention drivers

## Current Dashboard Data:
{ctx_str if ctx_str else "No data available"}

## Guidelines:
- Provide data-driven insights with specific numbers and percentages
- Offer strategic recommendations for talent management
- Identify risks and mitigation strategies
- Include cost-benefit analysis for HR initiatives
- Consider compliance and policy implications
- Use markdown formatting with bullet points for clarity

## Response Format:
- Start with overall workforce health assessment
- Highlight key metrics and their implications
- Identify risks and opportunities
- Recommend 2-3 specific actions for HR improvement"""

    def _get_default_quick_actions(self) -> List[Dict]:
        return [
            {
                "label": "Workforce Overview",
                "prompt_template": "Give me an overview of our current workforce — headcount, departments, and key metrics.",
                "icon": "users",
            },
            {
                "label": "Attrition Analysis",
                "prompt_template": "Analyze employee attrition trends and identify departments at risk.",
                "icon": "trending-down",
            },
            {
                "label": "Compensation Insights",
                "prompt_template": "Provide insights on our compensation structure and payroll costs.",
                "icon": "dollar-sign",
            },
            {
                "label": "Talent Retention",
                "prompt_template": "What strategies should we adopt to improve employee retention?",
                "icon": "target",
            },
        ]

    def _get_default_routing_keywords(self) -> List[str]:
        return [
            "employee", "staff", "workforce", "headcount", "attrition", "turnover",
            "retention", "payroll", "salary", "compensation", "hiring", "recruitment",
            "HR", "human resources", "talent", "attendance", "leave", "training",
            "performance", "engagement", "culture", "onboarding", "exit",
            "department", "team", "manager", "promotion", "career",
            "development", "skills", "appraisal", "diversity", "benefits",
        ]
