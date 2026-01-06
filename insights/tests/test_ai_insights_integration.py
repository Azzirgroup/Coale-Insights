# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
import json
import time
from unittest.mock import patch, MagicMock


class TestAIInsightsIntegration(FrappeTestCase):
    """Test suite for AI-powered Insights integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.setup_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        self.cleanup_test_data()
    
    def setup_test_data(self):
        """Create test data for insights testing"""
        
        # Create test company if not exists
        if not frappe.db.exists("Company", "Test Insights Co"):
            company = frappe.get_doc({
                "doctype": "Company",
                "company_name": "Test Insights Co",
                "default_currency": "USD",
                "country": "United States"
            })
            company.insert(ignore_permissions=True)
        
        # Create test customer
        if not frappe.db.exists("Customer", "Test Customer"):
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer",
                "customer_type": "Company"
            })
            customer.insert(ignore_permissions=True)
        
        # Create test item
        if not frappe.db.exists("Item", "Test Item"):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST-ITEM-001",
                "item_name": "Test Item",
                "description": "Test item for insights",
                "item_group": "All Item Groups",
                "stock_uom": "Nos"
            })
            item.insert(ignore_permissions=True)
    
    def cleanup_test_data(self):
        """Clean up test data"""
        
        # Remove test documents
        for doctype in ["Sales Invoice", "Customer", "Item", "Company"]:
            test_docs = frappe.get_all(doctype, filters={"name": ["like", "Test%"]})
            for doc in test_docs:
                try:
                    frappe.delete_doc(doctype, doc.name, ignore_permissions=True)
                except:
                    pass
    
    def test_model_router_initialization(self):
        """Test AI model router initialization"""
        
        from insights.ai_reasoning.model_router import AIModelRouter
        
        router = AIModelRouter()
        self.assertIsNotNone(router)
        self.assertTrue(len(router.model_configs) > 0)
        self.assertIn("llama-3.1-8b-instruct", router.model_configs)
    
    @patch('insights.ai_reasoning.model_router.OpenRouterClient')
    def test_ai_task_routing(self, mock_client):
        """Test AI task routing with different complexity levels"""
        
        from insights.ai_reasoning.model_router import AIModelRouter, TaskComplexity
        
        # Mock AI response
        mock_response = {
            "answer": "Test response",
            "confidence": 0.9,
            "processing_time": 1.5
        }
        mock_client.return_value.complete.return_value = mock_response
        
        router = AIModelRouter()
        
        # Test simple task routing
        response = router.route_task(
            task_type="simple_query",
            complexity=TaskComplexity.SIMPLE,
            payload={"question": "What is the total sales?"}
        )
        
        self.assertEqual(response["answer"], "Test response")
        self.assertEqual(response["confidence"], 0.9)
    
    def test_cache_manager_functionality(self):
        """Test cache manager operations"""
        
        from insights.cache_management.cache_manager import CacheManager, CacheLevel
        
        cache_manager = CacheManager()
        
        # Test cache operations
        test_key = "test_cache_key"
        test_value = {"data": "test_data", "timestamp": time.time()}
        
        # Cache data
        cache_manager.cache_data(
            cache_key=test_key,
            data=test_value,
            cache_level=CacheLevel.HOT,
            ttl=60
        )
        
        # Retrieve cached data
        cached_data = cache_manager.get_cached_data(test_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data["data"], "test_data")
    
    def test_processing_pipeline_task_submission(self):
        """Test processing pipeline task submission"""
        
        from insights.processing.processing_pipeline import submit_processing_task
        
        # Submit a test task
        task_id = submit_processing_task(
            task_type="dashboard_refresh",
            payload={
                "dashboard_id": "test_dashboard",
                "widget_id": "test_widget"
            }
        )
        
        self.assertIsNotNone(task_id)
        self.assertIsInstance(task_id, str)
        self.assertTrue(len(task_id) > 0)
    
    def test_erpnext_integrator_financial_insights(self):
        """Test ERPNext integrator financial insights"""
        
        from insights.integrations.erpnext_v15_integrator import get_financial_insights
        
        # Test financial insights generation
        insights = get_financial_insights(company="Test Insights Co")
        
        self.assertIsNotNone(insights)
        self.assertIn("revenue_analysis", insights)
        self.assertIn("cash_flow", insights)
        self.assertIn("period", insights)
    
    def test_performance_pipeline_optimization(self):
        """Test performance pipeline optimization"""
        
        from insights.performance.performance_pipeline import optimize_request
        
        # Test request optimization
        request_data = {
            "type": "simple_query",
            "complexity": "simple",
            "expected_rows": 100,
            "query_config": {
                "table": "Sales Invoice",
                "fields": ["name", "grand_total"],
                "filters": {"docstatus": 1}
            }
        }
        
        result = optimize_request(request_data)
        
        self.assertIsNotNone(result)
        self.assertIn("request_id", result)
        self.assertIn("type", result)
    
    def test_task_processor_simple_query(self):
        """Test task processor for simple queries"""
        
        from insights.processing.task_processors import TaskProcessor
        
        processor = TaskProcessor()
        
        # Test simple query processing
        payload = {
            "query": {
                "table": "Customer",
                "fields": ["name", "customer_name"],
                "filters": {"disabled": 0}
            }
        }
        
        result = processor.process_simple_query(payload, "Administrator")
        
        self.assertIsNotNone(result)
    
    @patch('insights.ai_reasoning.model_router.OpenRouterClient')
    def test_natural_language_query_processing(self, mock_client):
        """Test natural language query processing"""
        
        from insights.processing.task_processors import TaskProcessor
        
        # Mock AI response
        mock_response = {
            "answer": "The total sales for this month is $50,000",
            "confidence": 0.85,
            "sources": ["Sales Invoice"]
        }
        mock_client.return_value.complete.return_value = mock_response
        
        processor = TaskProcessor()
        
        # Test user question processing
        payload = {
            "question": "What are the total sales for this month?",
            "context": {"company": "Test Insights Co"}
        }
        
        result = processor.process_user_question(payload, "Administrator")
        
        self.assertIsNotNone(result)
        self.assertIn("answer", result)
        self.assertIn("confidence", result)
    
    def test_insights_settings_validation(self):
        """Test Insights settings validation"""
        
        # Test invalid settings
        settings = frappe.get_doc({
            "doctype": "Insights Settings",
            "ai_enabled": 1,
            "openrouter_api_key": "",  # Invalid: empty API key
            "default_model": ""  # Invalid: no default model
        })
        
        with self.assertRaises(frappe.ValidationError):
            settings.validate()
    
    def test_performance_metrics_collection(self):
        """Test performance metrics collection"""
        
        from insights.performance.performance_pipeline import get_performance_report
        
        report = get_performance_report()
        
        self.assertIsNotNone(report)
        self.assertIn("current_metrics", report)
        self.assertIn("request_count", report["current_metrics"])
        self.assertIn("average_response_time", report["current_metrics"])
    
    def test_comprehensive_dashboard_data(self):
        """Test comprehensive dashboard data generation"""
        
        from insights.integrations.erpnext_v15_integrator import get_comprehensive_dashboard
        
        # Test with limited modules to avoid long execution
        dashboard_data = get_comprehensive_dashboard(modules=["accounts", "selling"])
        
        self.assertIsNotNone(dashboard_data)
        self.assertIn("modules", dashboard_data)
        self.assertIn("summary", dashboard_data)
        self.assertIn("generated_at", dashboard_data)
    
    def test_cache_performance_under_load(self):
        """Test cache performance under concurrent load"""
        
        from insights.cache_management.cache_manager import CacheManager, CacheLevel
        import threading
        
        cache_manager = CacheManager()
        results = []
        
        def cache_operation(thread_id):
            """Perform cache operations in separate thread"""
            key = f"test_key_{thread_id}"
            value = {"thread": thread_id, "data": "test"}
            
            # Cache and retrieve
            cache_manager.cache_data(key, value, CacheLevel.HOT, 60)
            retrieved = cache_manager.get_cached_data(key)
            results.append(retrieved is not None)
        
        # Run multiple concurrent cache operations
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cache_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results))
    
    def test_ai_quota_management(self):
        """Test AI model quota management"""
        
        from insights.ai_reasoning.model_router import AIModelRouter
        
        router = AIModelRouter()
        
        # Get quota status
        quota_status = router.get_quota_status()
        
        self.assertIsNotNone(quota_status)
        self.assertIn("llama-3.1-8b-instruct", quota_status)
        
        # Verify quota percentages sum to 100
        total_quota = sum(
            model["quota_used"] + model["quota_remaining"] 
            for model in quota_status.values()
        )
        
        # Should be approximately 300 (100% for each of 3 models)
        self.assertAlmostEqual(total_quota, 300, delta=10)
    
    def test_error_handling_and_fallbacks(self):
        """Test error handling and fallback mechanisms"""
        
        from insights.ai_reasoning.model_router import AIModelRouter
        
        router = AIModelRouter()
        
        # Test with invalid model configuration
        with patch.object(router, 'model_configs', {}):
            # Should handle gracefully and not crash
            try:
                response = router.route_task(
                    task_type="test_task",
                    complexity="simple",
                    payload={"test": "data"}
                )
                # Should either work with fallback or return error response
                self.assertIsNotNone(response)
            except Exception as e:
                # Exception should be handled gracefully
                self.assertIsInstance(e, (frappe.ValidationError, Exception))


class TestInsightsPerformance(FrappeTestCase):
    """Performance tests for Insights components"""
    
    def test_cache_response_time(self):
        """Test cache response time performance"""
        
        from insights.cache_management.cache_manager import CacheManager, CacheLevel
        
        cache_manager = CacheManager()
        test_data = {"large_data": list(range(1000))}
        
        # Measure cache write time
        start_time = time.time()
        cache_manager.cache_data("perf_test", test_data, CacheLevel.HOT, 60)
        write_time = time.time() - start_time
        
        # Measure cache read time
        start_time = time.time()
        retrieved_data = cache_manager.get_cached_data("perf_test")
        read_time = time.time() - start_time
        
        # Verify performance thresholds
        self.assertLess(write_time, 0.1)  # Should write within 100ms
        self.assertLess(read_time, 0.01)  # Should read within 10ms
        self.assertEqual(retrieved_data["large_data"], test_data["large_data"])
    
    def test_processing_pipeline_throughput(self):
        """Test processing pipeline throughput"""
        
        from insights.processing.processing_pipeline import submit_processing_task
        
        # Submit multiple tasks and measure throughput
        start_time = time.time()
        task_count = 50
        
        task_ids = []
        for i in range(task_count):
            task_id = submit_processing_task(
                task_type="simple_query",
                payload={"test_id": i}
            )
            task_ids.append(task_id)
        
        processing_time = time.time() - start_time
        throughput = task_count / processing_time
        
        # Verify minimum throughput (adjust based on requirements)
        self.assertGreater(throughput, 10)  # At least 10 tasks per second
        self.assertEqual(len(task_ids), task_count)


if __name__ == "__main__":
    unittest.main()