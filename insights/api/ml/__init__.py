# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
ML API Package
Domain-specific ML analytics endpoints. Utility helpers live in utils.py.

All public (whitelisted) functions are re-exported here so that Frappe can
resolve them via the `insights.api.ml.<function>` dotted path.
"""

# Utils
from insights.api.ml.utils import parse_date_filter, get_date_filter_sql  # noqa: F401

# Strategic Finance
from insights.api.ml.strategic_finance import (  # noqa: F401
    strategic_finance_intelligence,
    get_budget_variance_overview,
)

# Customer Intelligence
from insights.api.ml.customer import (  # noqa: F401
    customer_segmentation,
    get_segment_summary,
    customer_intelligence,
    customer_intelligence_status,
    customer_360,
    customer_360_detail,
    purchase_patterns,
    cross_sell_opportunities,
    at_risk_customers,
    geographic_insights,
    next_best_actions,
    refresh_scores,
)

# Sales Intelligence
from insights.api.ml.sales import (  # noqa: F401
    sales_forecast,
    get_forecast_chart_data,
    sales_intelligence,
    payment_mix,
    sales_rep_performance,
    revenue_breakdown,
    margin_analysis,
    sales_comparisons,
    train_forecast_models,
    get_historical_and_forecast_by_dimension,
)

# Inventory Intelligence
from insights.api.ml.inventory import (  # noqa: F401
    inventory_classification,
    get_inventory_recommendations,
    inventory_intelligence,
    train_inventory_intelligence,
    get_stock_overview,
    get_turnover_analysis,
    get_aging_analysis,
    get_warehouse_analysis,
    get_transfer_recommendations,
    get_dead_stock,
)

# Financial Intelligence
from insights.api.ml.financial import (  # noqa: F401
    financial_intelligence,
    train_financial_intelligence,
    get_financial_overview,
    get_cash_flow_analysis,
    get_receivables_analysis,
    get_payables_analysis,
    get_budget_analysis,
    get_financial_ratios,
    get_kra_tax_analysis,
    get_forex_exposure,
    get_financial_forecasts,
)

# Risk Intelligence
from insights.api.ml.risk import risk_intelligence  # noqa: F401

# Procurement Intelligence
from insights.api.ml.procurement import (  # noqa: F401
    get_procurement_insights,
    procurement_intelligence,
    train_procurement_intelligence,
    get_spend_overview,
    get_supplier_performance,
    get_purchase_analytics,
    get_price_intelligence,
    get_procurement_risks,
    get_procurement_forecast,
)

# Tax Intelligence
from insights.api.ml.tax import tax_intelligence  # noqa: F401

# Manufacturing Intelligence
from insights.api.ml.manufacturing import (  # noqa: F401
    get_manufacturing_overview,
    get_oee_analysis,
    get_capacity_analysis,
    get_production_forecast,
    get_manufacturing_recommendations,
)

# HR Intelligence
from insights.api.ml.hr import (  # noqa: F401
    get_hr_overview,
    get_headcount_analytics,
    get_attrition_analytics,
    get_payroll_analytics,
    get_workforce_planning,
    get_hr_insights,
    get_talent_analytics,
    analyze_hr_query,
)

# ESG Intelligence
from insights.api.ml.esg import (  # noqa: F401
    get_esg_overview,
    export_esg_report,
)

# Executive Intelligence
from insights.api.ml.executive import (  # noqa: F401
    get_executive_summary,
    get_business_health_score,
    get_executive_kpis,
    get_executive_alerts,
    get_executive_trends,
    get_executive_insights,
    get_department_insights,
    get_strategic_recommendations,
    analyze_executive_query,
    generate_executive_report,
    send_executive_report,
    get_executive_reports_status,
    get_recent_executive_reports,
    download_executive_report,
    test_executive_intelligence_data,
    preview_executive_report_data,
)

# Predictive Analytics
from insights.api.ml.predictive import (  # noqa: F401
    generate_comprehensive_forecasts,
    detect_anomalies_and_risks,
    analyze_predictive_patterns,
    get_real_time_predictions,
    optimize_prediction_models,
    get_predictive_insights,
    get_risk_assessment,
    get_domain_comparison,
)

# General ML
from insights.api.ml.general import (  # noqa: F401
    get_ml_status,
    run_all_models,
    payment_risk_analysis,
    get_high_risk_invoices,
    demand_forecast,
    get_reorder_alerts,
    product_recommendations,
    recommend_for_item,
    recommend_for_customer,
    recommend_for_cart,
    get_dashboard_data,
    get_ml_insights_summary,
    generate_presentation_data,
)

# Cross-Dashboard Search
from insights.api.ml.search import (  # noqa: F401
    perform_cross_dashboard_search,
    get_search_suggestions,
    get_search_history,
    save_search_favorite,
    get_cross_dashboard_navigation,
    get_search_help,
    search_domain_data,
    get_available_search_filters,
)
