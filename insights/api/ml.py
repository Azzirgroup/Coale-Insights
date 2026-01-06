# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Consolidated ML API Endpoints
Provides a unified interface for all ML models
"""

import frappe
from typing import Dict, Any, List
from datetime import datetime


@frappe.whitelist()
def get_ml_status() -> Dict[str, Any]:
    """Get status of all ML models and their last training times"""
    from insights.ml.base import BaseMLModel
    
    models = [
        "customer_segmentation",
        "abc_xyz_classification", 
        "sales_forecast",
        "payment_model",
        "demand_forecast",
        "product_recommendations"
    ]
    
    base = BaseMLModel()
    status = {}
    
    for model_name in models:
        cached = base.get_cached_results(model_name)
        if cached:
            status[model_name] = {
                "status": "trained",
                "last_trained": cached.get('training_date') or cached.get('segmentation_date') or cached.get('forecast_date'),
                "has_data": True
            }
        else:
            status[model_name] = {
                "status": "not_trained",
                "has_data": False
            }
    
    return {
        "status": "success",
        "models": status
    }


@frappe.whitelist()
def run_all_models() -> Dict[str, Any]:
    """Run all ML models (use with caution - resource intensive)"""
    results = {}
    
    try:
        # Customer Segmentation
        from insights.ml.customer_segmentation import run_customer_segmentation
        results['customer_segmentation'] = run_customer_segmentation()
    except Exception as e:
        results['customer_segmentation'] = {"status": "error", "message": str(e)}
    
    try:
        # ABC/XYZ Classification
        from insights.ml.abc_xyz_classification import run_abc_xyz_classification
        results['abc_xyz_classification'] = run_abc_xyz_classification()
    except Exception as e:
        results['abc_xyz_classification'] = {"status": "error", "message": str(e)}
    
    try:
        # Sales Forecasting
        from insights.ml.sales_forecasting import run_sales_forecast
        results['sales_forecast'] = run_sales_forecast()
    except Exception as e:
        results['sales_forecast'] = {"status": "error", "message": str(e)}
    
    try:
        # Payment Prediction
        from insights.ml.payment_prediction import run_payment_prediction
        results['payment_prediction'] = run_payment_prediction()
    except Exception as e:
        results['payment_prediction'] = {"status": "error", "message": str(e)}
    
    try:
        # Demand Forecasting
        from insights.ml.demand_forecasting import run_demand_forecast
        results['demand_forecast'] = run_demand_forecast()
    except Exception as e:
        results['demand_forecast'] = {"status": "error", "message": str(e)}
    
    try:
        # Product Recommendations
        from insights.ml.product_recommendations import run_recommendation_training
        results['product_recommendations'] = run_recommendation_training()
    except Exception as e:
        results['product_recommendations'] = {"status": "error", "message": str(e)}
    
    return {
        "status": "success",
        "run_date": datetime.now().isoformat(),
        "results": results
    }


# ============== Customer Segmentation APIs ==============

@frappe.whitelist()
def customer_segmentation(refresh: bool = False) -> Dict[str, Any]:
    """Get customer segmentation results"""
    from insights.ml.customer_segmentation import CustomerSegmentation
    
    model = CustomerSegmentation()
    
    if not refresh:
        cached = model.get_cached_results("customer_segmentation")
        if cached:
            return cached
    
    return model.train()


@frappe.whitelist()
def get_segment_summary() -> Dict[str, Any]:
    """Get summary of customer segments"""
    from insights.ml.customer_segmentation import get_customer_segment
    
    result = customer_segmentation()
    
    if result.get('status') != 'success':
        return result
    
    summary = result.get('segment_summary', {})
    
    return {
        "status": "success",
        "segments": [
            {
                "segment": seg,
                "customer_count": data.get('count', 0),
                "total_revenue": data.get('total_revenue', 0),
                "avg_revenue": data.get('avg_revenue', 0)
            }
            for seg, data in summary.items()
        ]
    }


# ============== Inventory Analytics APIs ==============

@frappe.whitelist()
def inventory_classification(refresh: bool = False) -> Dict[str, Any]:
    """Get ABC/XYZ inventory classification"""
    from insights.ml.abc_xyz_classification import ABCXYZClassification
    
    model = ABCXYZClassification()
    
    if not refresh:
        cached = model.get_cached_results("abc_xyz_classification")
        if cached:
            return cached
    
    return model.train()


@frappe.whitelist()
def get_inventory_recommendations() -> Dict[str, Any]:
    """Get inventory management recommendations"""
    result = inventory_classification()
    
    if result.get('status') != 'success':
        return result
    
    # Extract key recommendations
    items = result.get('items', [])
    
    recommendations = {
        "high_priority": [i for i in items if i['combined_class'] in ['AX', 'AY', 'AZ']],
        "medium_priority": [i for i in items if i['combined_class'] in ['BX', 'BY', 'BZ']],
        "low_priority": [i for i in items if i['combined_class'] in ['CX', 'CY', 'CZ']]
    }
    
    return {
        "status": "success",
        "recommendations": {
            "high_priority_count": len(recommendations['high_priority']),
            "medium_priority_count": len(recommendations['medium_priority']),
            "low_priority_count": len(recommendations['low_priority']),
            "top_high_priority": recommendations['high_priority'][:10]
        }
    }


# ============== Sales Forecasting APIs ==============

@frappe.whitelist()
def sales_forecast(periods: int = 30, refresh: bool = False) -> Dict[str, Any]:
    """Get sales forecast"""
    from insights.ml.sales_forecasting import SalesForecasting
    
    model = SalesForecasting()
    
    if not refresh:
        cached = model.get_cached_results("sales_forecast")
        if cached:
            return cached
    
    return model.train(periods=int(periods))


@frappe.whitelist()
def get_forecast_chart_data() -> Dict[str, Any]:
    """Get forecast data formatted for charts"""
    result = sales_forecast()
    
    if result.get('status') != 'success':
        return result
    
    forecast = result.get('forecast', [])
    
    return {
        "status": "success",
        "chart_data": {
            "labels": [f['ds'][:10] if isinstance(f['ds'], str) else str(f['ds'])[:10] for f in forecast],
            "datasets": [
                {
                    "name": "Forecast",
                    "values": [round(f['yhat'], 2) for f in forecast]
                },
                {
                    "name": "Upper Bound",
                    "values": [round(f['yhat_upper'], 2) for f in forecast]
                },
                {
                    "name": "Lower Bound", 
                    "values": [round(f['yhat_lower'], 2) for f in forecast]
                }
            ]
        }
    }


# ============== Payment Prediction APIs ==============

@frappe.whitelist()
def payment_risk_analysis(refresh: bool = False) -> Dict[str, Any]:
    """Get payment risk analysis"""
    from insights.ml.payment_prediction import PaymentPrediction
    
    model = PaymentPrediction()
    
    if refresh:
        model.train()
    
    return model.predict()


@frappe.whitelist()
def get_high_risk_invoices() -> Dict[str, Any]:
    """Get high risk invoices only"""
    result = payment_risk_analysis()
    
    if result.get('status') != 'success':
        return result
    
    predictions = result.get('predictions', [])
    high_risk = [p for p in predictions if p['risk_level'] == 'High']
    
    return {
        "status": "success",
        "total_high_risk": len(high_risk),
        "total_amount_at_risk": sum(p['outstanding_amount'] for p in high_risk),
        "invoices": high_risk
    }


# ============== Demand Forecasting APIs ==============

@frappe.whitelist()
def demand_forecast(periods: int = 4, top_items: int = 100, refresh: bool = False) -> Dict[str, Any]:
    """Get demand forecast"""
    from insights.ml.demand_forecasting import DemandForecasting
    
    model = DemandForecasting()
    
    if not refresh:
        cached = model.get_cached_results("demand_forecast")
        if cached:
            return cached
    
    return model.train(periods=int(periods), top_items=int(top_items))


@frappe.whitelist()
def get_reorder_alerts() -> Dict[str, Any]:
    """Get items that need to be reordered"""
    result = demand_forecast()
    
    if result.get('status') != 'success':
        return result
    
    forecasts = result.get('forecasts', [])
    reorder_items = [f for f in forecasts if f['stock_status'] == 'Reorder Now']
    
    return {
        "status": "success",
        "alert_count": len(reorder_items),
        "items": reorder_items
    }


# ============== Product Recommendations APIs ==============

@frappe.whitelist()
def product_recommendations(refresh: bool = False) -> Dict[str, Any]:
    """Get product recommendation model results"""
    from insights.ml.product_recommendations import ProductRecommendations
    
    model = ProductRecommendations()
    
    if not refresh:
        cached = model.get_cached_results("product_recommendations")
        if cached:
            return cached
    
    return model.train()


@frappe.whitelist()
def recommend_for_item(item_code: str) -> Dict[str, Any]:
    """Get recommendations for a specific item"""
    from insights.ml.product_recommendations import get_item_recommendations
    return get_item_recommendations(item_code)


@frappe.whitelist()
def recommend_for_customer(customer: str) -> Dict[str, Any]:
    """Get personalized recommendations for a customer"""
    from insights.ml.product_recommendations import get_customer_recommendations
    return get_customer_recommendations(customer)


@frappe.whitelist()
def recommend_for_cart(items: str) -> Dict[str, Any]:
    """Get recommendations based on cart items"""
    from insights.ml.product_recommendations import get_cart_recommendations
    return get_cart_recommendations(items)


# ============== Dashboard Data APIs ==============

@frappe.whitelist()
def get_dashboard_data(dashboard_type: str) -> Dict[str, Any]:
    """Get ML data for specific dashboard"""
    
    if dashboard_type == "customer":
        return customer_segmentation()
    
    elif dashboard_type == "inventory":
        return {
            "classification": inventory_classification(),
            "demand": demand_forecast()
        }
    
    elif dashboard_type == "sales":
        return sales_forecast()
    
    elif dashboard_type == "financial":
        return payment_risk_analysis()
    
    elif dashboard_type == "procurement":
        demand = demand_forecast()
        return {
            "reorder_alerts": [f for f in demand.get('forecasts', []) if f['stock_status'] == 'Reorder Now']
        }
    
    elif dashboard_type == "production":
        return demand_forecast()
    
    else:
        return {"status": "error", "message": f"Unknown dashboard type: {dashboard_type}"}


@frappe.whitelist()
def get_ml_insights_summary() -> Dict[str, Any]:
    """Get a summary of all ML insights for the main dashboard"""
    summary = {}
    
    # Customer segments
    try:
        seg_result = customer_segmentation()
        if seg_result.get('status') == 'success':
            summary['customers'] = {
                "total_segmented": seg_result.get('total_customers', 0),
                "top_segment": max(
                    seg_result.get('segment_summary', {}).items(),
                    key=lambda x: x[1].get('count', 0),
                    default=('Unknown', {})
                )[0]
            }
    except:
        summary['customers'] = {"status": "unavailable"}
    
    # Payment risk
    try:
        payment_result = payment_risk_analysis()
        if payment_result.get('status') == 'success':
            summary['payments'] = {
                "outstanding_invoices": payment_result.get('summary', {}).get('total_invoices', 0),
                "high_risk_count": payment_result.get('summary', {}).get('high_risk_count', 0),
                "high_risk_amount": payment_result.get('summary', {}).get('high_risk_amount', 0)
            }
    except:
        summary['payments'] = {"status": "unavailable"}
    
    # Reorder alerts
    try:
        demand_result = demand_forecast()
        if demand_result.get('status') == 'success':
            summary['inventory'] = {
                "reorder_now_count": demand_result.get('summary', {}).get('reorder_now_count', 0),
                "items_analyzed": demand_result.get('summary', {}).get('total_items_analyzed', 0)
            }
    except:
        summary['inventory'] = {"status": "unavailable"}
    
    # Sales forecast
    try:
        forecast_result = sales_forecast()
        if forecast_result.get('status') == 'success':
            summary['sales'] = {
                "forecast_total": forecast_result.get('forecast_summary', {}).get('total_forecast', 0),
                "trend": forecast_result.get('forecast_summary', {}).get('trend', 'stable')
            }
    except:
        summary['sales'] = {"status": "unavailable"}
    
    # Customer Intelligence
    try:
        intel_result = customer_intelligence()
        if intel_result.get('status') == 'success':
            intel_summary = intel_result.get('summary', {})
            summary['customer_intelligence'] = {
                "total_customers": intel_summary.get('total_customers', 0),
                "total_clv": intel_summary.get('total_clv', 0),
                "avg_health_score": intel_summary.get('avg_health_score', 0),
                "at_risk_count": len(intel_result.get('at_risk_customers', [])),
                "actions_pending": len(intel_result.get('next_best_actions', []))
            }
    except:
        summary['customer_intelligence'] = {"status": "unavailable"}
    
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(),
        "summary": summary
    }


# ============== Customer Intelligence APIs ==============

@frappe.whitelist()
def customer_intelligence(refresh: bool = False, async_mode: bool = False) -> Dict[str, Any]:
    """Get comprehensive customer intelligence results"""
    from insights.ml.customer_intelligence import CustomerIntelligence, run_customer_intelligence
    
    if async_mode:
        return run_customer_intelligence(update_customers=True, async_mode=True)
    
    model = CustomerIntelligence()
    
    if not refresh:
        cached = model.get_cached_results("customer_intelligence")
        if cached:
            return cached
    
    return model.train()


@frappe.whitelist()
def customer_intelligence_status() -> Dict[str, Any]:
    """Check status of async customer intelligence job"""
    from insights.ml.customer_intelligence import get_customer_intelligence_status
    return get_customer_intelligence_status()


@frappe.whitelist()
def customer_360(customer_id: str) -> Dict[str, Any]:
    """Get 360-degree view of a specific customer"""
    from insights.ml.customer_intelligence import get_customer_360
    return get_customer_360(customer_id)


@frappe.whitelist()
def customer_360_detail(customer_id: str, include_purchases: bool = True, include_recommendations: bool = True) -> Dict[str, Any]:
    """Get comprehensive 360-degree view with purchase history and recommendations"""
    from insights.ml.customer_intelligence import get_customer_360_detail
    return get_customer_360_detail(customer_id, include_purchases, include_recommendations)


@frappe.whitelist()
def purchase_patterns(top_percentile: int = 20) -> Dict[str, Any]:
    """Get purchase patterns for top customers by CLV"""
    from insights.ml.customer_intelligence import get_purchase_patterns
    return get_purchase_patterns(top_percentile)


@frappe.whitelist()
def cross_sell_opportunities(tier_filter: str = "Diamond,Platinum") -> Dict[str, Any]:
    """Get cross-sell opportunities for high-value customers"""
    from insights.ml.customer_intelligence import get_cross_sell_opportunities
    return get_cross_sell_opportunities(tier_filter)


@frappe.whitelist()
def at_risk_customers() -> Dict[str, Any]:
    """Get customers at high churn risk"""
    from insights.ml.customer_intelligence import get_at_risk_customers
    return get_at_risk_customers()


@frappe.whitelist()
def geographic_insights() -> Dict[str, Any]:
    """Get geographic analysis by territory"""
    from insights.ml.customer_intelligence import get_geographic_insights
    return get_geographic_insights()


@frappe.whitelist()
def next_best_actions() -> Dict[str, Any]:
    """Get next best action recommendations"""
    from insights.ml.customer_intelligence import get_next_actions
    return get_next_actions()


@frappe.whitelist()
def pareto_analysis() -> Dict[str, Any]:
    """Get 80/20 Pareto analysis"""
    from insights.ml.customer_intelligence import get_pareto_analysis
    return get_pareto_analysis()


@frappe.whitelist()
def cohort_retention() -> Dict[str, Any]:
    """Get cohort retention analysis"""
    from insights.ml.customer_intelligence import get_cohort_analysis
    return get_cohort_analysis()


@frappe.whitelist()
def refresh_customer_scores() -> Dict[str, Any]:
    """Force refresh and update all customer scores"""
    from insights.ml.customer_intelligence import refresh_customer_scores as _refresh
    return _refresh()


# ==================== SALES INTELLIGENCE ENDPOINTS ====================

@frappe.whitelist()
def sales_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """Get comprehensive sales intelligence analysis"""
    from insights.ml.sales_intelligence import run_sales_intelligence
    return run_sales_intelligence(refresh=refresh)


@frappe.whitelist()
def payment_mix() -> Dict[str, Any]:
    """Get cash vs credit payment mix analysis"""
    from insights.ml.sales_intelligence import get_payment_mix
    return get_payment_mix()


@frappe.whitelist()
def sales_rep_performance() -> Dict[str, Any]:
    """Get individual sales rep performance metrics"""
    from insights.ml.sales_intelligence import get_sales_rep_performance
    return get_sales_rep_performance()


@frappe.whitelist()
def revenue_breakdown() -> Dict[str, Any]:
    """Get revenue by product group, customer segment, territory"""
    from insights.ml.sales_intelligence import get_revenue_breakdown
    return get_revenue_breakdown()


@frappe.whitelist()
def margin_analysis() -> Dict[str, Any]:
    """Get gross margin analysis by product group"""
    from insights.ml.sales_intelligence import get_margin_analysis
    return get_margin_analysis()


@frappe.whitelist()
def sales_comparisons() -> Dict[str, Any]:
    """Get MoM and YoY comparisons"""
    from insights.ml.sales_intelligence import get_sales_comparisons
    return get_sales_comparisons()


# ==================== FORECAST TRAINING ENDPOINTS ====================

@frappe.whitelist()
def train_forecast_models(model_type: str = 'all') -> Dict[str, Any]:
    """
    Train forecast ML models on demand
    
    Args:
        model_type: 'sales', 'demand', or 'all'
    """
    results = {}
    
    try:
        if model_type in ['sales', 'all']:
            from insights.ml.sales_forecasting import SalesForecasting
            frappe.publish_progress(25, title='Training Forecasts', description='Training Sales Forecast...')
            model = SalesForecasting(method="auto")
            results['sales_forecast'] = model.train(periods=90)
        
        if model_type in ['demand', 'all']:
            from insights.ml.demand_forecasting import DemandForecasting
            frappe.publish_progress(75, title='Training Forecasts', description='Training Demand Forecast...')
            model = DemandForecasting()
            results['demand_forecast'] = model.train(periods=4, top_items=100)
        
        frappe.publish_progress(100, title='Training Forecasts', description='Complete!')
        
        return {
            "status": "success",
            "message": f"Successfully trained {model_type} forecast models",
            "results": results
        }
        
    except Exception as e:
        frappe.log_error(f"Forecast training failed: {str(e)}", "ML Training")
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_historical_and_forecast_by_dimension(dimension: str = 'product_group') -> Dict[str, Any]:
    """
    Get historical sales and forecasted sales grouped by dimension
    
    Args:
        dimension: 'product_group', 'territory', or 'both'
    """
    import pandas as pd
    from datetime import datetime, timedelta
    
    def convert_to_native(data_list: list, keys_config: dict) -> list:
        """Convert frappe _dict to native Python types for pandas compatibility"""
        result = []
        for item in data_list:
            row = {}
            for key, converter in keys_config.items():
                value = item.get(key)
                if value is not None:
                    row[key] = converter(value)
                else:
                    row[key] = converter(0) if converter in [int, float] else ''
            result.append(row)
        return result
    
    try:
        results = {
            "status": "success",
            "historical": {},
            "forecast": {},
            "combined": []
        }
        
        # Get historical data by product group (using Parent Item Group)
        if dimension in ['product_group', 'both']:
            product_historical_raw = frappe.db.sql("""
                SELECT 
                    DATE_FORMAT(si.posting_date, '%Y-%m') as period,
                    COALESCE(ig.parent_item_group, COALESCE(i.item_group, 'Uncategorized')) as product_group,
                    SUM(sii.amount) as revenue,
                    COUNT(DISTINCT si.name) as transactions
                FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si ON sii.parent = si.name
                LEFT JOIN `tabItem` i ON sii.item_code = i.name
                LEFT JOIN `tabItem Group` ig ON i.item_group = ig.name
                WHERE si.docstatus = 1
                    AND si.posting_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(si.posting_date, '%Y-%m'), COALESCE(ig.parent_item_group, COALESCE(i.item_group, 'Uncategorized'))
                ORDER BY period, product_group
            """, as_dict=True)
            
            # Convert to native types for pandas compatibility
            product_historical = convert_to_native(product_historical_raw, {
                'period': str,
                'product_group': str,
                'revenue': float,
                'transactions': int
            })
            
            results['historical']['by_product_group'] = product_historical
            
            # Generate simple forecast by product group (3 months ahead)
            if product_historical:
                df = pd.DataFrame(product_historical)
                
                # Get last 3 months avg for each group
                recent_avg = df.groupby('product_group').agg({
                    'revenue': 'mean',
                    'transactions': 'mean'
                }).reset_index()
                
                forecast_periods = []
                today = datetime.now()
                for i in range(1, 4):
                    future_date = today + timedelta(days=30*i)
                    period = future_date.strftime('%Y-%m')
                    for _, row in recent_avg.iterrows():
                        forecast_periods.append({
                            'period': period,
                            'product_group': str(row['product_group']),
                            'revenue': round(float(row['revenue']) * (1 + 0.02 * i), 2),  # 2% growth assumption
                            'transactions': int(row['transactions']),
                            'is_forecast': True
                        })
                
                results['forecast']['by_product_group'] = forecast_periods
        
        # Get historical data by territory
        if dimension in ['territory', 'both']:
            territory_historical_raw = frappe.db.sql("""
                SELECT 
                    DATE_FORMAT(si.posting_date, '%Y-%m') as period,
                    COALESCE(si.territory, 'Unknown') as territory,
                    SUM(si.grand_total) as revenue,
                    COUNT(si.name) as transactions
                FROM `tabSales Invoice` si
                WHERE si.docstatus = 1
                    AND si.posting_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                    AND si.territory != 'All Territories'
                GROUP BY DATE_FORMAT(si.posting_date, '%Y-%m'), si.territory
                ORDER BY period, territory
            """, as_dict=True)
            
            # Convert to native types for pandas compatibility
            territory_historical = convert_to_native(territory_historical_raw, {
                'period': str,
                'territory': str,
                'revenue': float,
                'transactions': int
            })
            
            # Add "All Territories" as sum of all territories per period
            if territory_historical:
                df = pd.DataFrame(territory_historical)
                all_terr_totals = df.groupby('period').agg({
                    'revenue': 'sum',
                    'transactions': 'sum'
                }).reset_index()
                
                for _, row in all_terr_totals.iterrows():
                    territory_historical.append({
                        'period': str(row['period']),
                        'territory': 'All Territories',
                        'revenue': float(row['revenue']),
                        'transactions': int(row['transactions'])
                    })
            
            results['historical']['by_territory'] = territory_historical
            
            # Generate simple forecast by territory (3 months ahead)
            if territory_historical:
                df = pd.DataFrame(territory_historical)
                # Exclude "All Territories" from average calculation to avoid double counting
                df_no_all = df[df['territory'] != 'All Territories']
                
                recent_avg = df_no_all.groupby('territory').agg({
                    'revenue': 'mean',
                    'transactions': 'mean'
                }).reset_index()
                
                forecast_periods = []
                today = datetime.now()
                for i in range(1, 4):
                    future_date = today + timedelta(days=30*i)
                    period = future_date.strftime('%Y-%m')
                    period_total_revenue = 0
                    period_total_transactions = 0
                    
                    for _, row in recent_avg.iterrows():
                        revenue = round(float(row['revenue']) * (1 + 0.02 * i), 2)
                        transactions = int(row['transactions'])
                        forecast_periods.append({
                            'period': period,
                            'territory': str(row['territory']),
                            'revenue': revenue,
                            'transactions': transactions,
                            'is_forecast': True
                        })
                        period_total_revenue += revenue
                        period_total_transactions += transactions
                    
                    # Add "All Territories" total for this forecast period
                    forecast_periods.append({
                        'period': period,
                        'territory': 'All Territories',
                        'revenue': round(period_total_revenue, 2),
                        'transactions': period_total_transactions,
                        'is_forecast': True
                    })
                
                results['forecast']['by_territory'] = forecast_periods
        
        # Build combined view for easier charting
        if dimension in ['product_group', 'both'] and 'by_product_group' in results['historical']:
            combined = []
            for item in results['historical']['by_product_group']:
                # Historical data is already converted, just add is_forecast flag
                combined.append({**item, 'is_forecast': False})
            if 'by_product_group' in results['forecast']:
                combined.extend(results['forecast']['by_product_group'])
            results['combined_product_group'] = sorted(combined, key=lambda x: (x['product_group'], x['period']))
        
        if dimension in ['territory', 'both'] and 'by_territory' in results['historical']:
            combined = []
            for item in results['historical']['by_territory']:
                # Historical data is already converted, just add is_forecast flag
                combined.append({**item, 'is_forecast': False})
            if 'by_territory' in results['forecast']:
                combined.extend(results['forecast']['by_territory'])
            results['combined_territory'] = sorted(combined, key=lambda x: (x['territory'], x['period']))
        
        return results
        
    except Exception as e:
        frappe.log_error(f"Failed to get dimensional forecast: {str(e)}", "ML Forecast")
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# INVENTORY INTELLIGENCE ENDPOINTS
# ============================================================================

@frappe.whitelist()
def inventory_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """
    Get comprehensive inventory intelligence data
    
    Args:
        refresh: If True, regenerate all analytics. If False, return cached data if available.
    
    Returns:
        Dictionary containing:
        - stock_overview: Overall stock health and metrics
        - turnover_analysis: Turnover ratios by product group, fast/slow movers
        - aging_analysis: FIFO-based aging buckets
        - warehouse_analysis: Multi-warehouse stock distribution
        - transfer_recommendations: Suggested stock transfers
        - dead_stock: Obsolete inventory identification
        - procurement_insights: Supplier performance and reorder needs
        - abc_xyz: ABC/XYZ classification data (if available)
        - demand_planning: Demand forecast data (if available)
    """
    try:
        from insights.ml.inventory_intelligence import run_inventory_intelligence
        
        if isinstance(refresh, str):
            refresh = refresh.lower() == 'true'
        
        return run_inventory_intelligence(refresh=refresh)
        
    except Exception as e:
        frappe.log_error(f"Inventory Intelligence API failed: {str(e)}", "ML API")
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def train_inventory_intelligence() -> Dict[str, Any]:
    """
    Train/refresh inventory intelligence model
    Regenerates all inventory analytics including:
    - Stock overview and health score
    - Turnover analysis
    - Aging analysis (FIFO)
    - Warehouse analysis
    - Transfer recommendations
    - Dead stock identification
    - Procurement insights
    
    Also integrates ABC/XYZ and Demand Forecasting if available.
    """
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        result = model.train(include_abc_xyz=True, include_demand=True)
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Train Inventory Intelligence failed: {str(e)}", "ML Training")
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_stock_overview() -> Dict[str, Any]:
    """Get quick stock overview metrics"""
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        return {
            "status": "success",
            "data": model._calculate_stock_overview()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_turnover_analysis() -> Dict[str, Any]:
    """Get inventory turnover analysis"""
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        return {
            "status": "success",
            "data": model._calculate_turnover_analysis()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_aging_analysis() -> Dict[str, Any]:
    """Get FIFO-based stock aging analysis"""
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        return {
            "status": "success",
            "data": model._calculate_aging_analysis()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_warehouse_analysis() -> Dict[str, Any]:
    """Get multi-warehouse stock analysis"""
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        return {
            "status": "success",
            "data": model._calculate_warehouse_analysis()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_transfer_recommendations() -> Dict[str, Any]:
    """Get stock transfer recommendations between warehouses"""
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        return {
            "status": "success",
            "data": model._generate_transfer_recommendations()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_dead_stock() -> Dict[str, Any]:
    """Get dead/obsolete stock identification"""
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        return {
            "status": "success",
            "data": model._identify_dead_stock()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_procurement_insights() -> Dict[str, Any]:
    """Get procurement and supplier insights"""
    try:
        from insights.ml.inventory_intelligence import InventoryIntelligence
        
        model = InventoryIntelligence()
        return {
            "status": "success",
            "data": model._calculate_procurement_insights()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# Procurement Intelligence Endpoints
# ============================================================================

@frappe.whitelist()
def procurement_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """Get comprehensive procurement intelligence data"""
    try:
        from insights.ml.procurement_intelligence import run_procurement_intelligence
        
        return run_procurement_intelligence(refresh=refresh)
        
    except Exception as e:
        frappe.log_error(f"Procurement Intelligence API Error: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def train_procurement_intelligence() -> Dict[str, Any]:
    """Train/refresh procurement intelligence model"""
    try:
        from insights.ml.procurement_intelligence import ProcurementIntelligence
        
        model = ProcurementIntelligence()
        result = model.train()
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_spend_overview() -> Dict[str, Any]:
    """Get procurement spend overview"""
    try:
        from insights.ml.procurement_intelligence import ProcurementIntelligence
        
        model = ProcurementIntelligence()
        return {
            "status": "success",
            "data": model._calculate_spend_overview()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_supplier_performance() -> Dict[str, Any]:
    """Get supplier performance scores and metrics"""
    try:
        from insights.ml.procurement_intelligence import ProcurementIntelligence
        
        model = ProcurementIntelligence()
        return {
            "status": "success",
            "data": model._calculate_supplier_performance()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_purchase_analytics() -> Dict[str, Any]:
    """Get purchase cycle analytics"""
    try:
        from insights.ml.procurement_intelligence import ProcurementIntelligence
        
        model = ProcurementIntelligence()
        return {
            "status": "success",
            "data": model._analyze_purchase_cycles()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_price_intelligence() -> Dict[str, Any]:
    """Get price intelligence and variance analysis"""
    try:
        from insights.ml.procurement_intelligence import ProcurementIntelligence
        
        model = ProcurementIntelligence()
        return {
            "status": "success",
            "data": model._calculate_price_intelligence()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_procurement_risks() -> Dict[str, Any]:
    """Get procurement risk assessment"""
    try:
        from insights.ml.procurement_intelligence import ProcurementIntelligence
        
        model = ProcurementIntelligence()
        return {
            "status": "success",
            "data": model._assess_procurement_risks()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_procurement_forecast() -> Dict[str, Any]:
    """Get procurement spend forecasts"""
    try:
        from insights.ml.procurement_intelligence import ProcurementIntelligence
        
        model = ProcurementIntelligence()
        return {
            "status": "success",
            "data": model._generate_procurement_forecast()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# Financial Intelligence Endpoints (Kenya Edition)
# ============================================================================

@frappe.whitelist()
def financial_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """Get comprehensive financial intelligence data with KRA tax and forex analysis"""
    try:
        from insights.ml.financial_intelligence import run_financial_intelligence
        
        return run_financial_intelligence(refresh=refresh)
        
    except Exception as e:
        frappe.log_error(f"Financial Intelligence API Error: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def train_financial_intelligence() -> Dict[str, Any]:
    """Train/refresh financial intelligence model"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        result = model.train()
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_financial_overview() -> Dict[str, Any]:
    """Get P&L overview and key metrics"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._calculate_financial_overview()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_cash_flow_analysis() -> Dict[str, Any]:
    """Get cash flow metrics and position"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._calculate_cash_flow()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_receivables_analysis() -> Dict[str, Any]:
    """Get accounts receivable analysis"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._analyze_receivables()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_payables_analysis() -> Dict[str, Any]:
    """Get accounts payable analysis"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._analyze_payables()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_budget_analysis() -> Dict[str, Any]:
    """Get budget variance analysis"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._analyze_budget_variance()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_financial_ratios() -> Dict[str, Any]:
    """Get financial ratios"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._calculate_financial_ratios()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_kra_tax_analysis() -> Dict[str, Any]:
    """Get KRA tax analysis (16% VAT, 2% VAT WHT)"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._analyze_kra_tax()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_forex_exposure() -> Dict[str, Any]:
    """Get forex exposure analysis"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._analyze_forex_exposure()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_financial_forecasts() -> Dict[str, Any]:
    """Get financial forecasts"""
    try:
        from insights.ml.financial_intelligence import FinancialIntelligence
        
        model = FinancialIntelligence()
        return {
            "status": "success",
            "data": model._generate_financial_forecasts()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# TAX INTELLIGENCE ENDPOINTS (Kenya Corporate Tax)
# ============================================================================

@frappe.whitelist(allow_guest=False)
def tax_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """
    Get comprehensive tax intelligence data for Kenya corporate tax
    
    Features:
    - Corporate tax computation (30% rate)
    - Allowable vs non-allowable expense segregation
    - Capital allowances from Asset doctype
    - KRA quarterly instalment schedule
    - Withholding Tax (WHT) tracking
    - Tax forecasting and optimization insights
    
    Args:
        refresh: If True, regenerate all tax analytics. If False, return cached data.
    
    Returns:
        Dictionary containing tax_overview, income_analysis, expense_analysis,
        capital_allowances, kra_schedule, wht_analysis, tax_forecast, optimization_insights
    """
    try:
        from insights.ml.tax_intelligence import run_tax_intelligence
        
        return run_tax_intelligence(refresh=refresh)
        
    except Exception as e:
        frappe.log_error(f"Tax Intelligence API Error: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def train_tax_intelligence() -> Dict[str, Any]:
    """Train/refresh tax intelligence model"""
    try:
        from insights.ml.tax_intelligence import TaxIntelligence
        
        model = TaxIntelligence()
        result = model.train()
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_tax_overview() -> Dict[str, Any]:
    """Get tax overview with taxable income calculation"""
    try:
        from insights.ml.tax_intelligence import TaxIntelligence
        
        model = TaxIntelligence()
        return {
            "status": "success",
            "data": model._calculate_tax_overview()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_capital_allowances() -> Dict[str, Any]:
    """Get capital allowances from Asset doctype"""
    try:
        from insights.ml.tax_intelligence import TaxIntelligence
        
        model = TaxIntelligence()
        return {
            "status": "success",
            "data": model._calculate_capital_allowances()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_kra_instalment_schedule() -> Dict[str, Any]:
    """Get KRA quarterly instalment schedule"""
    try:
        from insights.ml.tax_intelligence import TaxIntelligence
        
        model = TaxIntelligence()
        overview = model._calculate_tax_overview()
        return {
            "status": "success",
            "data": model._generate_kra_schedule(overview)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_wht_analysis() -> Dict[str, Any]:
    """Get Withholding Tax (WHT) analysis"""
    try:
        from insights.ml.tax_intelligence import TaxIntelligence
        
        model = TaxIntelligence()
        return {
            "status": "success",
            "data": model._analyze_wht()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_expense_classification() -> Dict[str, Any]:
    """Get expense classification (allowable vs non-allowable)"""
    try:
        from insights.ml.tax_intelligence import TaxIntelligence
        
        model = TaxIntelligence()
        return {
            "status": "success",
            "data": model._analyze_expenses()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_tax_forecast() -> Dict[str, Any]:
    """Get tax liability forecast and projections"""
    try:
        from insights.ml.tax_intelligence import TaxIntelligence
        
        model = TaxIntelligence()
        overview = model._calculate_tax_overview()
        return {
            "status": "success",
            "data": model._generate_tax_forecast(overview)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# RISK INTELLIGENCE & ANALYTICS ENDPOINTS
# ============================================================================

@frappe.whitelist()
def risk_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """
    Get comprehensive risk intelligence and analytics data
    
    Args:
        refresh: If True, regenerate all risk analytics. If False, return cached data if available.
    
    Returns:
        Dictionary containing:
        - risk_overview: Overall risk assessment and key metrics
        - credit_risk: Customer payment behavior and default probability
        - cashflow_risk: Cash flow volatility and forecasting
        - operational_risk: Process efficiency and performance risks
        - compliance_risk: Regulatory and policy compliance assessment
        - predictive_analytics: Prophet forecasting and anomaly detection
        - risk_matrix: Risk impact vs probability visualization
        - early_warnings: Active risk alerts and recommendations
    """
    try:
        from insights.ml.risk_intelligence import run_risk_intelligence
        
        if isinstance(refresh, str):
            refresh = refresh.lower() == 'true'
        
        return run_risk_intelligence(refresh=refresh)
        
    except Exception as e:
        frappe.log_error(f"Risk Intelligence API Error: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def train_risk_intelligence() -> Dict[str, Any]:
    """Train/refresh risk intelligence model"""
    try:
        from insights.ml.risk_intelligence import RiskIntelligence
        
        model = RiskIntelligence()
        result = model.train()
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_credit_risk() -> Dict[str, Any]:
    """Get detailed credit risk analysis"""
    try:
        from insights.ml.risk_intelligence import RiskIntelligence
        
        model = RiskIntelligence()
        return {
            "status": "success",
            "data": model._analyze_credit_risk()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_cashflow_risk() -> Dict[str, Any]:
    """Get cash flow risk analysis with Prophet forecasting"""
    try:
        from insights.ml.risk_intelligence import RiskIntelligence
        
        model = RiskIntelligence()
        return {
            "status": "success",
            "data": model._analyze_cashflow_risk()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_operational_risk() -> Dict[str, Any]:
    """Get operational risk analysis"""
    try:
        from insights.ml.risk_intelligence import RiskIntelligence
        
        model = RiskIntelligence()
        return {
            "status": "success",
            "data": model._analyze_operational_risk()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_compliance_risk() -> Dict[str, Any]:
    """Get compliance risk analysis"""
    try:
        from insights.ml.risk_intelligence import RiskIntelligence
        
        model = RiskIntelligence()
        return {
            "status": "success",
            "data": model._analyze_compliance_risk()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_predictive_analytics() -> Dict[str, Any]:
    """Get predictive analytics with Prophet forecasting"""
    try:
        from insights.ml.risk_intelligence import RiskIntelligence
        
        model = RiskIntelligence()
        return {
            "status": "success",
            "data": model._generate_predictive_analytics()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_risk_alerts() -> Dict[str, Any]:
    """Get active risk alerts and early warnings"""
    try:
        from insights.ml.risk_intelligence import RiskIntelligence
        
        model = RiskIntelligence()
        return {
            "status": "success",
            "data": model._generate_early_warnings()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# Strategic Finance Intelligence Endpoints
# ============================================================================

@frappe.whitelist(allow_guest=True)
def strategic_finance_intelligence(refresh: bool = False) -> Dict[str, Any]:
    """Get comprehensive strategic finance intelligence data with forecasting and scenario analysis"""
    try:
        from insights.ml.strategic_finance_intelligence import run_strategic_finance_intelligence
        
        return run_strategic_finance_intelligence(refresh=refresh)
        
    except Exception as e:
        frappe.log_error(f"Strategic Finance Intelligence API Error: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def train_strategic_finance_intelligence() -> Dict[str, Any]:
    """Train/refresh strategic finance intelligence model"""
    try:
        from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
        
        model = StrategicFinanceIntelligence()
        result = model.train()
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_executive_summary() -> Dict[str, Any]:
    """Get executive-level KPIs and trends"""
    try:
        from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
        
        model = StrategicFinanceIntelligence()
        return {
            "status": "success",
            "data": model._calculate_executive_summary()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_cash_forecast() -> Dict[str, Any]:
    """Get 90-day cash flow forecast with scenarios"""
    try:
        from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
        
        model = StrategicFinanceIntelligence()
        return {
            "status": "success",
            "data": model._forecast_cash_flow()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_capital_planning() -> Dict[str, Any]:
    """Get capital planning and CAPEX analysis"""
    try:
        from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
        
        model = StrategicFinanceIntelligence()
        return {
            "status": "success",
            "data": model._analyze_capital_planning()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_working_capital_analysis() -> Dict[str, Any]:
    """Get working capital metrics and trends"""
    try:
        from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
        
        model = StrategicFinanceIntelligence()
        return {
            "status": "success",
            "data": model._analyze_working_capital()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_scenario_analysis() -> Dict[str, Any]:
    """Get scenario analysis with sensitivity and Monte Carlo"""
    try:
        from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
        
        model = StrategicFinanceIntelligence()
        return {
            "status": "success",
            "data": model._generate_scenario_analysis()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_period_comparison() -> Dict[str, Any]:
    """Get period-over-period comparison (MoM, QoQ, YoY)"""
    try:
        from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
        
        model = StrategicFinanceIntelligence()
        return {
            "status": "success",
            "data": model._compare_periods()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
