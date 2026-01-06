# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


app_name = "insights"
app_title = "Frappe Insights"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "Advanced Business Intelligence and Analytics with AI-powered insights"
app_email = "developers@frappe.io"
app_license = "AGPLv3"
app_version = "3.0.0"

# Required Apps
required_apps = [
    "frappe>=15.0.0",
    "erpnext>=15.0.0"
]

# Optional Apps for enhanced functionality
optional_apps = [
    "hrms>=15.0.0",
    "payments>=0.0.1"
]

# Frappe Framework Hooks
app_include_css = [
    "/assets/insights/css/insights.bundle.css"
]

app_include_js = [
    "/assets/insights/js/insights.bundle.js"
]

# Website and Portal
website_context = {
    "favicon": "/assets/insights/images/favicon.ico",
    "splash_image": "/assets/insights/images/splash.png"
}

# Boot session information
boot_session = "insights.boot.boot_session"

# Override ERPNext standard methods
override_whitelisted_methods = {
    "frappe.desk.query_report.run": "insights.api.reports.run_enhanced_report"
}

# Document Events Hooks
doc_events = {
    "*": {
        "after_insert": "insights.hooks.document_hooks.after_insert",
        "on_update": "insights.hooks.document_hooks.on_update", 
        "on_submit": "insights.hooks.document_hooks.on_submit",
        "on_cancel": "insights.hooks.document_hooks.on_cancel",
        "on_trash": "insights.hooks.document_hooks.on_trash"
    },
    "Sales Invoice": {
        "on_submit": "insights.hooks.sales_hooks.process_sales_invoice_insights"
    },
    "Purchase Invoice": {
        "on_submit": "insights.hooks.purchase_hooks.process_purchase_invoice_insights"
    },
    "Stock Entry": {
        "on_submit": "insights.hooks.stock_hooks.process_stock_entry_insights"
    },
    "Work Order": {
        "on_submit": "insights.hooks.manufacturing_hooks.process_work_order_insights"
    },
    "Employee Checkin": {
        "after_insert": "insights.hooks.hr_hooks.process_employee_checkin_insights"
    },
    "Customer": {
        "after_insert": "insights.hooks.crm_hooks.process_new_customer_insights",
        "on_update": "insights.hooks.crm_hooks.process_customer_update_insights"
    }
}

# Scheduled Tasks
scheduler_events = {
    "cron": {
        # AI Model Performance Monitoring (every 5 minutes)
        "*/5 * * * *": [
            "insights.ai_reasoning.model_router.monitor_model_performance"
        ],
        # Cache Cleanup and Optimization (every 15 minutes)
        "*/15 * * * *": [
            "insights.cache_management.cache_manager.cleanup_expired_cache",
            "insights.cache_management.cache_manager.optimize_cache_distribution"
        ],
        # Performance Pipeline Optimization (every 30 minutes)
        "*/30 * * * *": [
            "insights.performance.performance_pipeline.optimize_pipeline_performance"
        ]
    },
    "hourly": [
        # Aggregate hourly insights
        "insights.processing.aggregation.process_hourly_aggregations",
        # Update real-time dashboards
        "insights.dashboards.realtime_dashboard.update_realtime_metrics",
        # Sync ERPNext data changes
        "insights.integrations.erpnext_v15_integrator.sync_hourly_changes"
    ],
    "daily": [
        # Daily business intelligence reports
        "insights.reports.automated_reports.generate_daily_insights",
        # Customer behavior analysis
        "insights.ai_insights.customer_analytics.analyze_daily_patterns",
        # Sales forecasting updates
        "insights.ai_insights.sales_forecasting.update_daily_forecasts",
        # Inventory optimization recommendations
        "insights.ai_insights.inventory_optimization.generate_daily_recommendations",
        # Performance metrics archival
        "insights.performance.metrics_archival.archive_daily_metrics",
        # Cache statistics and cleanup
        "insights.cache_management.cache_manager.daily_cache_maintenance"
    ],
    "weekly": [
        # Weekly comprehensive business analysis
        "insights.reports.automated_reports.generate_weekly_insights",
        # Customer segmentation analysis
        "insights.ai_insights.customer_analytics.weekly_segmentation_analysis",
        # Financial trend analysis
        "insights.ai_insights.financial_analytics.weekly_trend_analysis",
        # Manufacturing efficiency analysis
        "insights.ai_insights.manufacturing_analytics.weekly_efficiency_analysis",
        # HR workforce analytics
        "insights.ai_insights.hr_analytics.weekly_workforce_analysis",
        # Model performance evaluation
        "insights.ai_reasoning.model_router.weekly_performance_evaluation"
    ],
    "monthly": [
        # Monthly executive dashboard
        "insights.reports.executive_reports.generate_monthly_executive_report",
        # Comprehensive customer lifetime value analysis
        "insights.ai_insights.customer_analytics.monthly_clv_analysis",
        # Advanced financial forecasting
        "insights.ai_insights.financial_analytics.monthly_financial_forecast",
        # Strategic business recommendations
        "insights.ai_insights.strategic_analytics.monthly_strategic_analysis",
        # Model retraining and optimization
        "insights.ai_reasoning.model_router.monthly_model_retraining"
    ]
}

# Background Jobs (Celery/RQ)
scheduler_events["daily_long"] = [
    # Large dataset processing
    "insights.processing.batch_processing.process_large_datasets",
    # ML model training
    "insights.ai_insights.ml_training.train_predictive_models",
    # Data warehouse synchronization
    "insights.integrations.data_warehouse.sync_data_warehouse"
]

# Jinja Environment Extensions
jenv = {
    "methods": [
        "insights.utils.jinja_methods.get_insights_data",
        "insights.utils.jinja_methods.format_insights_number",
        "insights.utils.jinja_methods.get_trend_indicator"
    ]
}

# Website Route Rules for Public Dashboards
website_route_rules = [
    {"from_route": "/insights", "to_route": "/insights_v2"},
    {"from_route": "/insights/<path:dashboard_path>", "to_route": "insights/public_dashboard"},
    {"from_route": "/analytics/<path:report_path>", "to_route": "insights/public_report"},
    {"from_route": "/ai-insights/<path:insight_path>", "to_route": "insights/ai_insight_view"}
]

# Session Creation Hook for User Context
on_session_creation = [
    "insights.auth.session_handler.setup_user_insights_context"
]

# Logout Hook for Analytics
on_logout = [
    "insights.analytics.user_analytics.track_user_logout"
]

# API Rate Limiting
api_rate_limits = {
    "insights.api.ai_query.process_natural_language_query": {
        "requests": 100,
        "window": 3600  # 1 hour
    },
    "insights.api.reports.generate_report": {
        "requests": 500,
        "window": 3600
    }
}

# WebSocket Events for Real-time Updates
realtime_events = {
    "insights_data_updated": "insights.realtime.handlers.handle_data_update",
    "insights_dashboard_refresh": "insights.realtime.handlers.handle_dashboard_refresh",
    "insights_ai_response": "insights.realtime.handlers.handle_ai_response"
}

# Email Templates
email_brand_logo = "/assets/insights/images/insights_logo.png"

# Fixtures for Initial Setup
fixtures = [
    {"doctype": "Insights Settings", "filters": {"name": "Insights Settings"}},
    {"doctype": "AI Model Configuration", "filters": {}},
    {"doctype": "Dashboard Template", "filters": {}},
    {"doctype": "Report Template", "filters": {}}
]

# Translation Contribution
translate_link_fields = [
    {"doctype": "Insights Dashboard", "fieldname": "title"},
    {"doctype": "Insights Report", "fieldname": "report_name"},
    {"doctype": "Insights Widget", "fieldname": "widget_title"}
]

# Custom Fields for ERPNext Integration
custom_fields = {
    "Sales Invoice": [
        {
            "fieldname": "insights_analyzed",
            "label": "Insights Analyzed",
            "fieldtype": "Check",
            "default": 0,
            "read_only": 1
        },
        {
            "fieldname": "ai_insights_data",
            "label": "AI Insights Data",
            "fieldtype": "Long Text",
            "hidden": 1
        }
    ],
    "Customer": [
        {
            "fieldname": "ai_risk_score",
            "label": "AI Risk Score",
            "fieldtype": "Percent",
            "read_only": 1
        },
        {
            "fieldname": "customer_segment",
            "label": "Customer Segment", 
            "fieldtype": "Select",
            "options": "High Value\nMedium Value\nLow Value\nAt Risk\nNew Customer",
            "read_only": 1
        }
    ],
    "Item": [
        {
            "fieldname": "demand_forecast",
            "label": "AI Demand Forecast",
            "fieldtype": "Float",
            "read_only": 1
        },
        {
            "fieldname": "reorder_recommendation",
            "label": "AI Reorder Recommendation",
            "fieldtype": "Float", 
            "read_only": 1
        }
    ]
}

# Property Setters for UI Customization  
property_setters = [
    {
        "doctype": "Sales Invoice",
        "property": "default_print_format",
        "value": "Insights Enhanced Sales Invoice"
    }
]

# Dashboard Charts Integration
dashboard_charts = [
    {
        "chart_name": "AI Sales Forecast",
        "doctype": "Sales Invoice",
        "is_public": 1,
        "chart_type": "Line",
        "source": "insights.dashboards.charts.ai_sales_forecast"
    },
    {
        "chart_name": "Customer Risk Analysis", 
        "doctype": "Customer",
        "is_public": 1,
        "chart_type": "Donut",
        "source": "insights.dashboards.charts.customer_risk_analysis"
    }
]

# Number Cards for Quick Metrics
number_cards = [
    {
        "name": "AI Revenue Forecast",
        "doctype": "Sales Invoice", 
        "function": "insights.dashboards.cards.ai_revenue_forecast",
        "is_public": 1
    },
    {
        "name": "Customer Health Score",
        "doctype": "Customer",
        "function": "insights.dashboards.cards.customer_health_score", 
        "is_public": 1
    }
]

# Notification Configuration
notification_config = [
    {
        "name": "High Risk Customer Alert",
        "doctype": "Customer",
        "subject": "High Risk Customer Detected: {customer_name}",
        "condition": "doc.ai_risk_score > 75",
        "recipients": ["Sales Manager", "Account Manager"]
    },
    {
        "name": "Inventory Shortage Prediction",
        "doctype": "Item",
        "subject": "Predicted Stock Shortage: {item_name}",
        "condition": "doc.demand_forecast > doc.projected_qty",
        "recipients": ["Stock Manager", "Purchase Manager"]
    }
]

# Integration with External BI Tools
external_integrations = {
    "power_bi": {
        "enabled": True,
        "connector": "insights.integrations.power_bi.PowerBIConnector"
    },
    "tableau": {
        "enabled": True,
        "connector": "insights.integrations.tableau.TableauConnector"
    },
    "grafana": {
        "enabled": True,
        "connector": "insights.integrations.grafana.GrafanaConnector"
    }
}

# Machine Learning Model Registry
ml_models = {
    "sales_forecasting": {
        "model_type": "time_series",
        "framework": "prophet",
        "update_frequency": "daily"
    },
    "customer_segmentation": {
        "model_type": "clustering", 
        "framework": "scikit-learn",
        "update_frequency": "weekly"
    },
    "churn_prediction": {
        "model_type": "classification",
        "framework": "xgboost",
        "update_frequency": "weekly"
    }
}

# Data Export Configurations
export_formats = {
    "pdf": {
        "engine": "weasyprint",
        "options": {"page_size": "A4", "orientation": "portrait"}
    },
    "excel": {
        "engine": "openpyxl", 
        "options": {"include_charts": True, "format_numbers": True}
    },
    "powerpoint": {
        "engine": "python-pptx",
        "options": {"template": "insights_template.pptx"}
    }
}

# API Versioning
api_versions = {
    "v1": {
        "base_url": "/api/insights/v1",
        "methods": [
            "insights.api.v1.reports.get_report",
            "insights.api.v1.dashboards.get_dashboard",
            "insights.api.v1.ai.natural_language_query"
        ]
    },
    "v2": {
        "base_url": "/api/insights/v2", 
        "methods": [
            "insights.api.v2.analytics.get_analytics",
            "insights.api.v2.ai.enhanced_query",
            "insights.api.v2.streaming.stream_data"
        ]
    }
}

# Security and Permissions
permission_query_conditions = {
    "Insights Dashboard": "insights.permissions.dashboard_query_conditions",
    "Insights Report": "insights.permissions.report_query_conditions"
}

has_permission = {
    "Insights Dashboard": "insights.permissions.has_dashboard_permission",
    "Insights Report": "insights.permissions.has_report_permission"
}

# Performance Monitoring
performance_metrics = {
    "query_execution_time": {
        "threshold": 5.0,  # seconds
        "alert": True
    },
    "cache_hit_rate": {
        "threshold": 0.8,  # 80%
        "alert": True  
    },
    "ai_response_time": {
        "threshold": 10.0,  # seconds
        "alert": True
    }
}

# Development and Testing Hooks
if frappe.conf.get("developer_mode"):
    # Additional hooks for development
    doc_events["*"]["before_save"] = "insights.dev.hooks.log_document_changes"
    
    # Test data generators
    test_dependencies = [
        "insights.tests.fixtures.create_test_data"
    ]

# Mobile App Integration (if applicable)
mobile_app_config = {
    "app_name": "Frappe Insights Mobile",
    "supported_platforms": ["iOS", "Android"],
    "api_endpoints": [
        "insights.mobile.api.get_mobile_dashboard",
        "insights.mobile.api.get_mobile_reports"
    ]
}

# Backup and Archive Configuration
backup_config = {
    "insights_data": {
        "frequency": "daily",
        "retention": "90 days",
        "include_cache": False
    },
    "ml_models": {
        "frequency": "weekly", 
        "retention": "1 year",
        "version_control": True
    }
}