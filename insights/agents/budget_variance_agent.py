"""
Budget Variance AI Agent

This agent specializes in handling budget variance analysis queries and provides:
- Intelligent budget variance insights
- Automated variance interpretation
- Natural language query processing for budget-related questions
- Contextual recommendations for budget improvement
- Interactive analysis and explanations

Author: AI Assistant
Version: 1.0.0
"""

import frappe
from typing import Dict, List, Any, Optional
import json
import re
import logging
from insights.ml.budget_variance_intelligence import BudgetVarianceIntelligence

logger = logging.getLogger(__name__)

class BudgetVarianceAgent:
    """
    AI Agent specialized in budget variance analysis and insights
    
    Capabilities:
    - Natural language query processing for budget variance questions
    - Contextual insights and recommendations
    - Interactive variance analysis
    - Automated variance interpretation and alerts
    """
    
    def __init__(self):
        """Initialize Budget Variance Agent"""
        self.agent_name = "Budget Variance Agent"
        self.description = "Specialized agent for budget variance analysis and financial planning insights"
        
        # Keywords for budget variance queries
        self.budget_keywords = [
            "budget", "variance", "actual", "forecast", "planning",
            "spend", "spending", "allocation", "deviation", "overspend",
            "underspend", "budget control", "financial planning",
            "cost control", "expense management", "budget monitoring"
        ]
        
        # Query intent patterns
        self.intent_patterns = {
            "variance_overview": [
                r"budget\s+variance", r"variance\s+analysis", r"budget\s+performance",
                r"actual\s+vs\s+budget", r"budget\s+summary", r"variance\s+report"
            ],
            "department_variance": [
                r"department.*variance", r"departmental.*budget", r"cost\s+center.*budget",
                r"division.*variance", r"team.*budget", r"unit.*spending"
            ],
            "forecast_accuracy": [
                r"forecast.*accuracy", r"prediction.*accuracy", r"forecasting.*performance",
                r"forecast.*quality", r"prediction.*quality"
            ],
            "alerts": [
                r"budget.*alert", r"variance.*alert", r"budget.*problem",
                r"spending.*issue", r"budget.*concern", r"overspent"
            ],
            "recommendations": [
                r"improve.*budget", r"budget.*recommendation", r"optimize.*budget",
                r"budget.*suggestion", r"better.*planning", r"enhance.*forecasting"
            ]
        }
    
    def can_handle_query(self, query: str) -> bool:
        """
        Determine if this agent can handle the given query
        
        Args:
            query: User query string
            
        Returns:
            True if agent can handle the query
        """
        try:
            query_lower = query.lower()
            
            # Check for budget variance keywords
            return any(keyword in query_lower for keyword in self.budget_keywords)
            
        except Exception as e:
            logger.error(f"Error checking query compatibility: {e}")
            return False
    
    def get_insights(self, query: str, company: str = None, fiscal_year: str = None) -> Dict[str, Any]:
        """
        Get budget variance insights based on the query
        
        Args:
            query: Natural language query
            company: Company filter
            fiscal_year: Fiscal year filter
            
        Returns:
            Dict with insights and analysis
        """
        try:
            logger.info(f"Processing budget variance query: {query}")
            
            # Initialize intelligence module
            intelligence = BudgetVarianceIntelligence(
                company=company,
                fiscal_year=fiscal_year
            )
            
            # Analyze query intent
            intent = self._analyze_query_intent(query)
            
            # Get base data
            overview = intelligence.get_budget_variance_overview()
            
            # Generate response based on intent
            if intent == "variance_overview":
                insights = self._get_variance_overview_insights(overview, query)
            elif intent == "department_variance":
                insights = self._get_department_variance_insights(overview, query)
            elif intent == "forecast_accuracy":
                insights = self._get_forecast_accuracy_insights(overview, query)
            elif intent == "alerts":
                insights = self._get_alert_insights(overview, query)
            elif intent == "recommendations":
                insights = self._get_recommendation_insights(overview, query)
            else:
                insights = self._get_general_insights(overview, query)
            
            # Add contextual information
            insights.update({
                "agent": self.agent_name,
                "query_intent": intent,
                "data_source": "Budget Variance Intelligence",
                "timestamp": frappe.utils.now()
            })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error processing budget variance query: {e}")
            return {
                "error": "Unable to process budget variance query",
                "message": str(e),
                "agent": self.agent_name
            }
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze query to determine intent"""
        try:
            query_lower = query.lower()
            
            for intent, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, query_lower):
                        return intent
            
            # Check for specific keywords
            if any(word in query_lower for word in ["overview", "summary", "performance"]):
                return "variance_overview"
            elif any(word in query_lower for word in ["department", "cost center", "division"]):
                return "department_variance"
            elif any(word in query_lower for word in ["alert", "problem", "issue", "concern"]):
                return "alerts"
            elif any(word in query_lower for word in ["improve", "optimize", "recommend", "suggest"]):
                return "recommendations"
            
            return "general"
            
        except Exception as e:
            logger.error(f"Error analyzing query intent: {e}")
            return "general"
    
    def _get_variance_overview_insights(self, overview: Dict, query: str) -> Dict[str, Any]:
        """Get insights for variance overview queries"""
        try:
            summary = overview.get('summary', {})
            
            variance_pct = summary.get('variance_percentage', 0)
            budget_status = summary.get('status', 'unknown')
            
            # Generate narrative
            if abs(variance_pct) <= 5:
                narrative = f"Your budget performance is excellent with only {variance_pct:.1f}% variance from planned amounts."
            elif abs(variance_pct) <= 15:
                narrative = f"Budget performance is {budget_status} with {variance_pct:.1f}% variance, which is within acceptable limits."
            else:
                narrative = f"Budget variance of {variance_pct:.1f}% indicates significant deviations that require attention."
            
            # Key metrics
            key_metrics = {
                "Total Budget": f"${summary.get('total_budget', 0):,.2f}",
                "Total Actual": f"${summary.get('total_actual', 0):,.2f}",
                "Variance": f"${summary.get('total_variance', 0):,.2f} ({variance_pct:.1f}%)",
                "Budget Utilization": f"{summary.get('budget_utilization', 0):.1f}%",
                "Trend": summary.get('variance_trend', 'unknown').title()
            }
            
            # Performance indicators
            ytd_performance = summary.get('ytd_performance', {})
            
            return {
                "summary": narrative,
                "key_metrics": key_metrics,
                "variance_status": budget_status,
                "ytd_performance": ytd_performance,
                "detailed_data": summary,
                "visualization_data": self._prepare_variance_chart_data(summary)
            }
            
        except Exception as e:
            logger.error(f"Error generating variance overview insights: {e}")
            return {"error": "Unable to generate variance overview insights"}
    
    def _get_department_variance_insights(self, overview: Dict, query: str) -> Dict[str, Any]:
        """Get insights for department variance queries"""
        try:
            dept_analysis = overview.get('departmental_analysis', [])
            
            if not dept_analysis:
                return {"message": "No departmental variance data available"}
            
            # Find departments with highest variances
            top_variances = sorted(
                dept_analysis, 
                key=lambda x: abs(x.get('variance_percentage', 0)), 
                reverse=True
            )[:5]
            
            # Generate narrative
            worst_dept = top_variances[0] if top_variances else None
            if worst_dept:
                worst_variance = worst_dept.get('variance_percentage', 0)
                narrative = f"Department variance analysis shows {worst_dept['department']} has the highest variance at {worst_variance:.1f}%."
            else:
                narrative = "All departments are performing within expected variance ranges."
            
            # Department insights
            dept_insights = []
            for dept in top_variances:
                variance_pct = dept.get('variance_percentage', 0)
                status = dept.get('status', 'unknown')
                trend = dept.get('trend', 'unknown')
                
                insight = {
                    "department": dept['department'],
                    "variance_percentage": variance_pct,
                    "status": status,
                    "trend": trend,
                    "budget": f"${dept.get('budget', 0):,.2f}",
                    "actual": f"${dept.get('actual', 0):,.2f}",
                    "variance": f"${dept.get('variance', 0):,.2f}",
                    "interpretation": self._interpret_department_variance(variance_pct, status, trend)
                }
                dept_insights.append(insight)
            
            return {
                "summary": narrative,
                "department_insights": dept_insights,
                "total_departments": len(dept_analysis),
                "departments_over_budget": len([d for d in dept_analysis if d.get('variance', 0) > 0]),
                "departments_under_budget": len([d for d in dept_analysis if d.get('variance', 0) < 0]),
                "visualization_data": self._prepare_department_chart_data(dept_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error generating department variance insights: {e}")
            return {"error": "Unable to generate department variance insights"}
    
    def _get_forecast_accuracy_insights(self, overview: Dict, query: str) -> Dict[str, Any]:
        """Get insights for forecast accuracy queries"""
        try:
            forecast_data = overview.get('forecast_accuracy', {})
            
            if not forecast_data:
                return {"message": "No forecast accuracy data available"}
            
            accuracy = forecast_data.get('overall_accuracy', 0)
            grade = forecast_data.get('accuracy_grade', 'N/A')
            trend = forecast_data.get('accuracy_trend', 'unknown')
            
            # Generate narrative based on accuracy
            if accuracy >= 90:
                narrative = f"Excellent forecasting performance with {accuracy:.1f}% accuracy (Grade: {grade})"
            elif accuracy >= 80:
                narrative = f"Good forecasting accuracy at {accuracy:.1f}% (Grade: {grade}), with room for improvement"
            elif accuracy >= 70:
                narrative = f"Moderate forecasting accuracy of {accuracy:.1f}% (Grade: {grade}) suggests need for process enhancement"
            else:
                narrative = f"Forecasting accuracy of {accuracy:.1f}% (Grade: {grade}) is below acceptable levels and requires immediate attention"
            
            # Improvement recommendations
            improvements = forecast_data.get('improvement_recommendations', [])
            
            return {
                "summary": narrative,
                "accuracy_percentage": accuracy,
                "accuracy_grade": grade,
                "accuracy_trend": trend,
                "forecast_bias": forecast_data.get('forecast_bias', {}),
                "improvement_recommendations": improvements,
                "monthly_accuracy": forecast_data.get('monthly_accuracy', [])
            }
            
        except Exception as e:
            logger.error(f"Error generating forecast accuracy insights: {e}")
            return {"error": "Unable to generate forecast accuracy insights"}
    
    def _get_alert_insights(self, overview: Dict, query: str) -> Dict[str, Any]:
        """Get insights for budget alert queries"""
        try:
            alerts = overview.get('alerts', [])
            
            if not alerts:
                return {
                    "summary": "No budget alerts detected. All variance levels are within acceptable ranges.",
                    "alert_count": 0,
                    "status": "healthy"
                }
            
            # Categorize alerts by severity
            high_alerts = [a for a in alerts if a.get('severity') == 'high']
            medium_alerts = [a for a in alerts if a.get('severity') == 'medium']
            low_alerts = [a for a in alerts if a.get('severity') == 'low']
            
            # Generate narrative
            total_alerts = len(alerts)
            if high_alerts:
                narrative = f"Critical attention required: {len(high_alerts)} high-severity budget alerts detected"
            elif medium_alerts:
                narrative = f"Moderate attention needed: {len(medium_alerts)} medium-priority budget alerts"
            else:
                narrative = f"{total_alerts} low-priority budget alerts requiring monitoring"
            
            return {
                "summary": narrative,
                "alert_count": total_alerts,
                "high_priority_alerts": high_alerts,
                "medium_priority_alerts": medium_alerts,
                "low_priority_alerts": low_alerts,
                "recommended_actions": self._get_alert_actions(alerts),
                "status": "critical" if high_alerts else "warning" if medium_alerts else "caution"
            }
            
        except Exception as e:
            logger.error(f"Error generating alert insights: {e}")
            return {"error": "Unable to generate alert insights"}
    
    def _get_recommendation_insights(self, overview: Dict, query: str) -> Dict[str, Any]:
        """Get insights for recommendation queries"""
        try:
            recommendations = overview.get('recommendations', [])
            
            if not recommendations:
                return {
                    "summary": "Budget performance is optimal. No specific recommendations at this time.",
                    "recommendation_count": 0
                }
            
            # Categorize by priority
            high_priority = [r for r in recommendations if r.get('priority') == 'high']
            medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
            low_priority = [r for r in recommendations if r.get('priority') == 'low']
            
            # Generate narrative
            if high_priority:
                narrative = f"Immediate action recommended: {len(high_priority)} high-priority improvements identified"
            elif medium_priority:
                narrative = f"Strategic improvements available: {len(medium_priority)} medium-priority recommendations"
            else:
                narrative = f"Optimization opportunities: {len(low_priority)} enhancement suggestions"
            
            return {
                "summary": narrative,
                "total_recommendations": len(recommendations),
                "high_priority_recommendations": high_priority,
                "medium_priority_recommendations": medium_priority,
                "low_priority_recommendations": low_priority,
                "implementation_roadmap": self._create_implementation_roadmap(recommendations),
                "expected_impact": self._assess_recommendation_impact(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation insights: {e}")
            return {"error": "Unable to generate recommendation insights"}
    
    def _get_general_insights(self, overview: Dict, query: str) -> Dict[str, Any]:
        """Get general budget variance insights"""
        try:
            summary = overview.get('summary', {})
            alerts = overview.get('alerts', [])
            recommendations = overview.get('recommendations', [])
            
            # Generate comprehensive narrative
            variance_pct = summary.get('variance_percentage', 0)
            status = summary.get('status', 'unknown')
            
            narrative = f"""
            Budget variance analysis shows {status} performance with {variance_pct:.1f}% overall variance. 
            {len(alerts)} alerts detected requiring attention, with {len(recommendations)} improvement recommendations available.
            """
            
            # Key highlights
            highlights = []
            if abs(variance_pct) > 15:
                highlights.append(f"High variance of {variance_pct:.1f}% requires immediate attention")
            
            if alerts:
                high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
                if high_alerts:
                    highlights.append(f"{high_alerts} critical alerts need immediate action")
            
            ytd_performance = summary.get('ytd_performance', {})
            if ytd_performance:
                utilization = ytd_performance.get('budget_utilization', 0)
                highlights.append(f"YTD budget utilization: {utilization:.1f}%")
            
            return {
                "summary": narrative.strip(),
                "key_highlights": highlights,
                "variance_status": status,
                "alert_summary": f"{len(alerts)} alerts detected",
                "recommendation_summary": f"{len(recommendations)} recommendations available",
                "performance_metrics": overview.get('performance_metrics', {}),
                "next_steps": self._suggest_next_steps(overview)
            }
            
        except Exception as e:
            logger.error(f"Error generating general insights: {e}")
            return {"error": "Unable to generate general insights"}
    
    # Helper methods for contextual insights
    
    def _interpret_department_variance(self, variance_pct: float, status: str, trend: str) -> str:
        """Interpret department variance for user understanding"""
        interpretation = []
        
        if abs(variance_pct) <= 5:
            interpretation.append("Excellent budget control")
        elif abs(variance_pct) <= 15:
            interpretation.append("Good budget management with minor variances")
        else:
            interpretation.append("Significant variance requires attention")
        
        if trend == "improving":
            interpretation.append("showing positive trend")
        elif trend == "deteriorating":
            interpretation.append("with concerning trend requiring intervention")
        
        return ". ".join(interpretation)
    
    def _prepare_variance_chart_data(self, summary: Dict) -> Dict[str, Any]:
        """Prepare data for variance visualization"""
        return {
            "chart_type": "variance_comparison",
            "data": [
                {"category": "Budget", "value": summary.get('total_budget', 0)},
                {"category": "Actual", "value": summary.get('total_actual', 0)},
                {"category": "Variance", "value": abs(summary.get('total_variance', 0))}
            ],
            "variance_percentage": summary.get('variance_percentage', 0)
        }
    
    def _prepare_department_chart_data(self, dept_analysis: List) -> Dict[str, Any]:
        """Prepare data for department variance visualization"""
        chart_data = []
        for dept in dept_analysis[:10]:  # Top 10 departments
            chart_data.append({
                "department": dept['department'],
                "variance_percentage": dept.get('variance_percentage', 0),
                "variance_amount": dept.get('variance', 0)
            })
        
        return {
            "chart_type": "department_variance",
            "data": chart_data
        }
    
    def _get_alert_actions(self, alerts: List) -> List[str]:
        """Extract actionable items from alerts"""
        actions = []
        for alert in alerts:
            action = alert.get('action')
            if action:
                actions.append(action)
        return list(set(actions))  # Remove duplicates
    
    def _create_implementation_roadmap(self, recommendations: List) -> List[Dict[str, Any]]:
        """Create implementation roadmap for recommendations"""
        roadmap = []
        
        # Sort by priority
        sorted_recs = sorted(recommendations, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x.get('priority', 'low')], reverse=True)
        
        for i, rec in enumerate(sorted_recs[:5], 1):  # Top 5 recommendations
            roadmap.append({
                "phase": i,
                "title": rec.get('title', ''),
                "priority": rec.get('priority', 'medium'),
                "impact": rec.get('impact', 'unknown'),
                "effort": rec.get('effort', 'unknown'),
                "timeline": self._estimate_timeline(rec.get('effort', 'unknown'))
            })
        
        return roadmap
    
    def _estimate_timeline(self, effort: str) -> str:
        """Estimate implementation timeline based on effort"""
        timelines = {
            "Low": "1-2 weeks",
            "Medium": "1-2 months",
            "High": "3-6 months"
        }
        return timelines.get(effort, "2-4 weeks")
    
    def _assess_recommendation_impact(self, recommendations: List) -> Dict[str, Any]:
        """Assess overall impact of implementing recommendations"""
        high_impact = len([r for r in recommendations if r.get('impact') == 'High'])
        medium_impact = len([r for r in recommendations if r.get('impact') == 'Medium'])
        
        return {
            "high_impact_items": high_impact,
            "medium_impact_items": medium_impact,
            "total_recommendations": len(recommendations),
            "estimated_improvement": "15-25%" if high_impact > 0 else "5-15%"
        }
    
    def _suggest_next_steps(self, overview: Dict) -> List[str]:
        """Suggest immediate next steps based on analysis"""
        steps = []
        
        alerts = overview.get('alerts', [])
        recommendations = overview.get('recommendations', [])
        summary = overview.get('summary', {})
        
        # Based on alerts
        high_alerts = [a for a in alerts if a.get('severity') == 'high']
        if high_alerts:
            steps.append("Address high-priority budget alerts immediately")
        
        # Based on variance
        variance_pct = abs(summary.get('variance_percentage', 0))
        if variance_pct > 20:
            steps.append("Conduct detailed variance investigation")
        
        # Based on recommendations
        high_priority_recs = [r for r in recommendations if r.get('priority') == 'high']
        if high_priority_recs:
            steps.append(f"Implement {len(high_priority_recs)} high-priority recommendations")
        
        # Default steps
        if not steps:
            steps.extend([
                "Continue monitoring budget performance",
                "Review monthly variance trends",
                "Update forecasting models as needed"
            ])
        
        return steps