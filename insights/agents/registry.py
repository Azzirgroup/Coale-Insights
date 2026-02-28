# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Agent Registry
Central registry for all dashboard intelligence agents.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from insights.agents.base import BaseIntelligenceAgent


class AgentRegistry:
    """Registry for dashboard intelligence agents"""

    _agents: Dict[str, type] = {}

    @classmethod
    def register(cls, dashboard_type: str):
        """Decorator to register an agent class"""

        def decorator(agent_class: type):
            cls._agents[dashboard_type] = agent_class
            return agent_class

        return decorator

    @classmethod
    def get_agent(cls, dashboard_type: str) -> Optional["BaseIntelligenceAgent"]:
        """Get an agent instance for a dashboard type"""
        agent_class = cls._agents.get(dashboard_type)
        if agent_class:
            return agent_class()
        return None

    @classmethod
    def get_all_dashboard_types(cls) -> List[str]:
        """Get all registered dashboard types"""
        return list(cls._agents.keys())

    @classmethod
    def get_all_routing_keywords(cls) -> Dict[str, List[str]]:
        """Get routing keywords for all registered agents"""
        keywords = {}
        for dtype, agent_class in cls._agents.items():
            agent = agent_class()
            keywords[dtype] = agent.get_routing_keywords()
        return keywords
