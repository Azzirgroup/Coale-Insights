import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock


class TestAgentRegistry(FrappeTestCase):
    """Test suite for the Agent Registry and agent initialization"""

    def test_registry_has_registered_agents(self):
        """Test that agents are registered in the registry"""
        # Import agents to trigger registration
        import insights.agents.sales_agent
        import insights.agents.financial_agent
        import insights.agents.customer_agent
        import insights.agents.inventory_agent
        import insights.agents.procurement_agent
        import insights.agents.risk_agent
        import insights.agents.tax_agent
        import insights.agents.general_agent

        from insights.agents import AgentRegistry

        dashboard_types = AgentRegistry.get_all_dashboard_types()
        self.assertGreater(len(dashboard_types), 0)
        self.assertIn("Sales", dashboard_types)
        self.assertIn("Financial", dashboard_types)
        self.assertIn("Customer", dashboard_types)
        self.assertIn("Inventory", dashboard_types)
        self.assertIn("Procurement", dashboard_types)
        self.assertIn("Risk", dashboard_types)
        self.assertIn("Tax", dashboard_types)
        self.assertIn("General", dashboard_types)

    def test_get_agent_returns_instance(self):
        """Test that get_agent returns a valid agent instance"""
        import insights.agents.sales_agent
        from insights.agents import AgentRegistry, BaseIntelligenceAgent

        agent = AgentRegistry.get_agent("Sales")
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, BaseIntelligenceAgent)

    def test_get_agent_unknown_type_returns_none(self):
        """Test that get_agent returns None for unknown dashboard types"""
        from insights.agents import AgentRegistry

        agent = AgentRegistry.get_agent("NonexistentDashboard")
        self.assertIsNone(agent)


class TestBaseIntelligenceAgent(FrappeTestCase):
    """Test suite for BaseIntelligenceAgent functionality"""

    def _get_agent(self):
        """Helper to get a concrete agent instance"""
        import insights.agents.general_agent
        from insights.agents import AgentRegistry
        return AgentRegistry.get_agent("General")

    def test_agent_has_required_attributes(self):
        """Test that agents have required attributes"""
        agent = self._get_agent()
        self.assertTrue(hasattr(agent, 'dashboard_type'))
        self.assertTrue(hasattr(agent, 'agent_name'))
        self.assertTrue(hasattr(agent, 'description'))
        self.assertTrue(len(agent.dashboard_type) > 0)
        self.assertTrue(len(agent.agent_name) > 0)

    def test_set_context(self):
        """Test setting dashboard context"""
        agent = self._get_agent()
        test_context = {
            "summary": "Test summary",
            "total_revenue": 100000,
            "trends": [{"metric": "revenue", "value": "up"}],
            "alerts": [{"message": "Low stock"}]
        }
        agent.set_context(test_context)
        self.assertEqual(agent.context, test_context)
        self.assertIsInstance(agent.compressed_context, dict)

    def test_compress_context(self):
        """Test context compression"""
        agent = self._get_agent()
        full_context = {
            "summary": "Test dashboard",
            "total_revenue": 50000,
            "total_orders": 100,
            "trends": [
                {"metric": "revenue", "value": 50000},
                {"metric": "orders", "value": 100}
            ],
            "alerts": [{"message": "Alert 1"}],
            "top_customers": [
                {"name": f"Customer {i}", "value": 1000 - i * 100}
                for i in range(10)
            ],
            "filters": {"date_range": "Last 12 Months"}
        }
        compressed = agent.compress_context(full_context)

        self.assertIn("summary", compressed)
        self.assertIn("kpis", compressed)
        self.assertIn("trends", compressed)
        self.assertIn("alerts", compressed)
        self.assertIn("date_range", compressed)

    def test_compress_context_size_limit(self):
        """Test that compressed context respects size limits"""
        import json
        agent = self._get_agent()

        # Create a large context
        large_context = {
            "summary": "Large context test",
            "trends": [{"metric": f"trend_{i}", "value": i} for i in range(100)],
            "alerts": [{"message": f"Alert {i}"} for i in range(50)],
            "top_items": [{"name": f"Item {i}", "data": "x" * 100} for i in range(50)]
        }
        compressed = agent.compress_context(large_context)
        compressed_size = len(json.dumps(compressed))
        # Should be under 15KB even for large inputs
        self.assertLess(compressed_size, 15000)

    def test_get_quick_actions(self):
        """Test that agents provide quick actions"""
        agent = self._get_agent()
        actions = agent.get_quick_actions()
        self.assertIsInstance(actions, list)

    def test_get_routing_keywords(self):
        """Test that agents provide routing keywords"""
        agent = self._get_agent()
        keywords = agent.get_routing_keywords()
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)

    def test_build_system_prompt(self):
        """Test system prompt generation"""
        agent = self._get_agent()
        prompt = agent.build_system_prompt({"summary": "Test"})
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_format_context_for_display_empty(self):
        """Test formatting with no context"""
        agent = self._get_agent()
        result = agent.format_context_for_display()
        self.assertEqual(result, "No context available")

    def test_format_context_for_display_with_data(self):
        """Test formatting with context data"""
        agent = self._get_agent()
        agent.set_context({
            "summary": "Test dashboard",
            "total_revenue": 50000,
            "alerts": [{"message": "Test alert"}]
        })
        result = agent.format_context_for_display()
        self.assertIn("Dashboard Context", result)


class TestSpecializedAgents(FrappeTestCase):
    """Test suite for each specialized agent type"""

    AGENT_TYPES = [
        "Sales", "Financial", "Customer", "Inventory",
        "Procurement", "Risk", "Tax", "General"
    ]

    def setUp(self):
        """Import all agents to ensure registration"""
        import insights.agents.sales_agent
        import insights.agents.financial_agent
        import insights.agents.customer_agent
        import insights.agents.inventory_agent
        import insights.agents.procurement_agent
        import insights.agents.risk_agent
        import insights.agents.tax_agent
        import insights.agents.general_agent

    def test_all_agents_instantiate(self):
        """Test that all registered agents can be instantiated"""
        from insights.agents import AgentRegistry

        for agent_type in self.AGENT_TYPES:
            agent = AgentRegistry.get_agent(agent_type)
            self.assertIsNotNone(agent, f"Agent for {agent_type} should not be None")
            self.assertEqual(agent.dashboard_type, agent_type)

    def test_all_agents_have_unique_keywords(self):
        """Test that agent routing keywords don't conflict"""
        from insights.agents import AgentRegistry

        all_keywords = {}
        for agent_type in self.AGENT_TYPES:
            agent = AgentRegistry.get_agent(agent_type)
            keywords = agent.get_routing_keywords()
            all_keywords[agent_type] = set(keywords)

        # Check for uniqueness (some overlap is OK, but core keywords should differ)
        for i, (type_a, kw_a) in enumerate(all_keywords.items()):
            for type_b, kw_b in list(all_keywords.items())[i + 1:]:
                overlap = kw_a & kw_b
                # Allow some overlap but not complete overlap
                self.assertNotEqual(
                    kw_a, kw_b,
                    f"Agents {type_a} and {type_b} have identical keywords"
                )

    def test_all_agents_provide_quick_actions(self):
        """Test that all agents provide quick actions"""
        from insights.agents import AgentRegistry

        for agent_type in self.AGENT_TYPES:
            agent = AgentRegistry.get_agent(agent_type)
            actions = agent.get_quick_actions()
            self.assertIsInstance(actions, list, f"{agent_type} quick_actions should be a list")

    @patch('insights.ai.openrouter_client.OpenRouterClient')
    def test_agent_execute_disabled(self, mock_client_class):
        """Test agent execute when AI is disabled"""
        from insights.agents import AgentRegistry

        mock_client = MagicMock()
        mock_client.is_enabled.return_value = False
        mock_client_class.return_value = mock_client

        agent = AgentRegistry.get_agent("General")
        result = agent.execute("test query", "session-1")

        self.assertFalse(result["success"])
        self.assertIn("not enabled", result["error"].lower())

    @patch('insights.ai.openrouter_client.OpenRouterClient')
    def test_agent_execute_quota_exceeded(self, mock_client_class):
        """Test agent execute when quota is exceeded"""
        from insights.agents import AgentRegistry

        mock_client = MagicMock()
        mock_client.is_enabled.return_value = True
        mock_client.check_quota.return_value = False
        mock_client_class.return_value = mock_client

        agent = AgentRegistry.get_agent("General")
        result = agent.execute("test query", "session-1")

        self.assertFalse(result["success"])
        self.assertIn("quota", result["error"].lower())


class TestAgentRegistryKeywords(FrappeTestCase):
    """Test the routing keywords registry"""

    def setUp(self):
        import insights.agents.sales_agent
        import insights.agents.financial_agent
        import insights.agents.customer_agent
        import insights.agents.inventory_agent
        import insights.agents.procurement_agent
        import insights.agents.risk_agent
        import insights.agents.tax_agent
        import insights.agents.general_agent

    def test_get_all_routing_keywords(self):
        """Test getting all routing keywords from registry"""
        from insights.agents import AgentRegistry

        keywords = AgentRegistry.get_all_routing_keywords()
        self.assertIsInstance(keywords, dict)
        self.assertGreater(len(keywords), 0)

        for dashboard_type, kw_list in keywords.items():
            self.assertIsInstance(kw_list, list)
            self.assertGreater(len(kw_list), 0, f"{dashboard_type} should have keywords")


if __name__ == '__main__':
    unittest.main()
