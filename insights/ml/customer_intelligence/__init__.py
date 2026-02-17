# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Customer Intelligence Analytics
Comprehensive customer analytics including CLV, churn prediction, health scoring,
and geographic analysis.

This package splits the former monolithic customer_intelligence.py into:
- data.py       : Database queries for customer transactions
- analytics.py  : CLV, RFM, churn risk, health score calculations
- predict.py    : Cached/fresh prediction retrieval
- actions.py    : Geography, next best actions, scores, affinity, pareto, cohort
- api.py        : All @frappe.whitelist() standalone wrapper functions
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

from insights.ml.base import BaseMLModel
from insights.api.ml import get_date_filter_sql

# Import submodules
from insights.ml.customer_intelligence import data as _data
from insights.ml.customer_intelligence import analytics as _analytics
from insights.ml.customer_intelligence import predict as _predict
from insights.ml.customer_intelligence import actions as _actions

# Re-export API functions for backward compatibility
# These were previously importable from insights.ml.customer_intelligence
from insights.ml.customer_intelligence.api import (  # noqa: F401
    run_customer_intelligence,
    _run_customer_intelligence_job,
    get_customer_intelligence,
    get_customer_intelligence_status,
    get_customer_360_detail,
    _get_customer_360_lightweight,
    _get_customer_purchase_history,
    _analyze_customer_purchase_patterns,
    _get_customer_cross_sell,
    get_purchase_patterns,
    get_cross_sell_opportunities,
    get_at_risk_customers,
    get_geographic_insights,
    get_next_actions,
    get_pareto_analysis,
    get_cohort_analysis,
    refresh_customer_scores,
)


class CustomerIntelligence(BaseMLModel):
    """
    Customer Intelligence Analytics Engine

    Provides:
    - Customer Lifetime Value (CLV) Analytics
    - Churn Risk Prediction
    - Customer Health Scoring
    - Geographic Intelligence (Territory-based)
    - Cohort Analysis
    - 80/20 Analysis (Pareto)
    - Next Best Action Recommendations

    Methods delegate to standalone functions in submodules, receiving
    ``self`` (the intelligence instance) as the first argument.
    """

    CUSTOMER_THRESHOLD = 5000  # Async threshold

    def __init__(self, date_filter: str = '12m'):
        super().__init__()
        self.model_name = "CustomerIntelligence"
        self.date_filter = date_filter
        # Generate SQL date filter
        self.DATE_FILTER = get_date_filter_sql(date_filter, 'posting_date', 'si')

    # ==================== DATA COLLECTION ====================

    def _get_customer_transactions(self) -> pd.DataFrame:
        return _data.get_customer_transactions(self)

    def _get_territory_data(self) -> pd.DataFrame:
        return _data.get_territory_data(self)

    def _get_customer_items(self) -> pd.DataFrame:
        return _data.get_customer_items(self)

    def _get_payment_history(self) -> pd.DataFrame:
        return _data.get_payment_history(self)

    def _get_quotation_data(self) -> pd.DataFrame:
        return _data.get_quotation_data(self)

    # ==================== ANALYTICS ====================

    def calculate_clv(self, customer_df: pd.DataFrame) -> pd.DataFrame:
        return _analytics.calculate_clv(self, customer_df)

    def _calculate_clv_components(self, df: pd.DataFrame, tenure_months: pd.Series) -> pd.DataFrame:
        return _analytics._calculate_clv_components(df, tenure_months)

    def _calculate_rfm_segment(self, df: pd.DataFrame) -> pd.DataFrame:
        return _analytics._calculate_rfm_segment(df)

    def calculate_churn_risk(self, customer_df: pd.DataFrame, clv_df: pd.DataFrame) -> pd.DataFrame:
        return _analytics.calculate_churn_risk(self, customer_df, clv_df)

    def calculate_health_score(self, churn_df: pd.DataFrame, payment_df: pd.DataFrame) -> pd.DataFrame:
        return _analytics.calculate_health_score(self, churn_df, payment_df)

    # ==================== ACTIONS ====================

    def analyze_geography(self, health_df: pd.DataFrame, territory_df: pd.DataFrame) -> Dict[str, Any]:
        return _actions.analyze_geography(self, health_df, territory_df)

    def analyze_product_affinity(self, items_df: pd.DataFrame, health_df: pd.DataFrame) -> Dict[str, Any]:
        return _actions.analyze_product_affinity(self, items_df, health_df)

    def pareto_analysis(self, health_df: pd.DataFrame) -> Dict[str, Any]:
        return _actions.pareto_analysis(self, health_df)

    def cohort_analysis(self, customer_df: pd.DataFrame) -> Dict[str, Any]:
        return _actions.cohort_analysis(self, customer_df)

    def get_next_best_actions(self, health_df: pd.DataFrame) -> List[Dict[str, Any]]:
        return _actions.get_next_best_actions(self, health_df)

    def update_customer_scores(self, health_df: pd.DataFrame) -> Dict[str, Any]:
        return _actions.update_customer_scores(self, health_df)

    # ==================== PREDICT ====================

    def predict(self, customer: str = None) -> Dict[str, Any]:
        return _predict.predict(self, customer)

    # ==================== MAIN TRAINING METHOD ====================

    def train(self, update_customers: bool = True) -> Dict[str, Any]:
        """Run complete customer intelligence analysis"""
        # Collect data
        customer_df = self._get_customer_transactions()
        territory_df = self._get_territory_data()
        items_df = self._get_customer_items()
        payment_df = self._get_payment_history()
        quotation_df = self._get_quotation_data()

        if customer_df.empty:
            return {"status": "error", "message": "No customer data found"}

        # Calculate CLV
        clv_df = self.calculate_clv(customer_df)

        # Calculate churn risk
        churn_df = self.calculate_churn_risk(customer_df, clv_df)

        # Calculate health scores
        health_df = self.calculate_health_score(churn_df, payment_df)

        # Geographic analysis
        geo_analysis = self.analyze_geography(health_df, territory_df)

        # Product affinity
        product_affinity = self.analyze_product_affinity(items_df, health_df)

        # Pareto analysis
        pareto = self.pareto_analysis(health_df)

        # Cohort analysis
        cohort = self.cohort_analysis(customer_df)

        # Next best actions
        actions = self.get_next_best_actions(health_df)

        # Quotation conversion rate
        if not quotation_df.empty:
            conversion_rate = quotation_df['converted'].mean() * 100
            total_quotes = len(quotation_df)
            converted_quotes = int(quotation_df['converted'].sum())
        else:
            conversion_rate = 0
            total_quotes = 0
            converted_quotes = 0

        # Update customer records
        update_result = {"status": "skipped"}
        if update_customers:
            update_result = self.update_customer_scores(health_df)

        # Summary statistics
        summary = {
            'total_customers': len(health_df),
            'total_clv': float(health_df['historical_clv'].sum()),
            'avg_clv': float(health_df['historical_clv'].mean()),
            'avg_order_value': float(health_df['avg_order_value'].mean()),
            'avg_health_score': float(health_df['health_score'].mean()),
            'avg_churn_risk': float(health_df['churn_score'].mean()),
            'clv_tier_distribution': {str(k): int(v) for k, v in health_df['clv_tier'].value_counts().to_dict().items()},
            'health_distribution': {str(k): int(v) for k, v in health_df['health_status'].value_counts().to_dict().items()},
            'churn_risk_distribution': {str(k): int(v) for k, v in health_df['churn_risk'].value_counts().to_dict().items()},
            'rfm_segment_distribution': {str(k): int(v) for k, v in health_df['rfm_segment'].value_counts().to_dict().items()} if 'rfm_segment' in health_df.columns else {},
            'quote_conversion_rate': round(conversion_rate, 1),
            'total_quotes': int(total_quotes),
            'converted_quotes': converted_quotes
        }

        # Prepare customer details - include RFM fields and CLV component scores
        customer_fields = [
            'customer_id', 'customer_name', 'customer_group', 'territory',
            'historical_clv', 'predicted_12m_clv', 'total_clv', 'clv_tier', 'clv_score',
            'order_count', 'avg_order_value', 'recency_days', 'purchase_frequency',
            'churn_score', 'churn_risk', 'health_score', 'health_status',
            'outstanding_amount', 'rfm_score', 'rfm_segment',
            'revenue_score', 'engagement_score', 'longevity_score', 'growth_score',
            'avg_days_to_pay', 'payment_score', 'overdue_count'
        ]
        # Only include columns that exist
        available_fields = [f for f in customer_fields if f in health_df.columns]
        customer_details = health_df[available_fields].copy()

        # Convert categorical columns to string first before any fillna
        for col in ['clv_tier', 'churn_risk', 'health_status', 'rfm_segment', 'rfm_score']:
            if col in customer_details.columns:
                customer_details[col] = customer_details[col].astype(str)

        # Convert to serializable types - handle NaN values
        for col in customer_details.columns:
            if customer_details[col].dtype == 'object':
                customer_details[col] = customer_details[col].fillna('').astype(str)
            elif pd.api.types.is_numeric_dtype(customer_details[col]):
                customer_details[col] = customer_details[col].fillna(0)

        # Replace 'nan' strings with defaults
        customer_details['clv_tier'] = customer_details['clv_tier'].replace('nan', 'Bronze')
        customer_details['churn_risk'] = customer_details['churn_risk'].replace('nan', 'Low')
        customer_details['health_status'] = customer_details['health_status'].replace('nan', 'Healthy')
        if 'rfm_segment' in customer_details.columns:
            customer_details['rfm_segment'] = customer_details['rfm_segment'].replace('nan', 'Need Attention')
        if 'rfm_score' in customer_details.columns:
            customer_details['rfm_score'] = customer_details['rfm_score'].replace('nan', '333')

        # Convert DataFrame to dict and clean NaN values for JSON serialization
        def clean_dict_for_json(d):
            """Recursively clean dict for JSON serialization"""
            if isinstance(d, dict):
                return {k: clean_dict_for_json(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict_for_json(item) for item in d]
            elif isinstance(d, float) and (pd.isna(d) or np.isnan(d)):
                return 0
            elif d is None or (isinstance(d, str) and d.lower() == 'nan'):
                return ''
            return d

        customers_list = clean_dict_for_json(customer_details.to_dict('records'))

        results = {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "summary": clean_dict_for_json(summary),
            "customers": customers_list,
            "geographic_analysis": clean_dict_for_json(geo_analysis),
            "product_affinity": clean_dict_for_json(product_affinity),
            "pareto_analysis": clean_dict_for_json(pareto),
            "cohort_analysis": clean_dict_for_json(cohort),
            "next_best_actions": clean_dict_for_json(actions),
            "at_risk_customers": [c for c in customers_list if c.get('churn_risk') in ['High', 'Critical']],
            "top_customers": sorted(customers_list, key=lambda x: x.get('total_clv', 0), reverse=True)[:20],
            "customer_update_result": update_result
        }

        # Cache results
        self.cache_results("customer_intelligence", results, expires_in_hours=12)

        # Log training
        self.log_training({
            "customers_analyzed": len(health_df),
            "at_risk_count": len(results['at_risk_customers']),
            "actions_generated": len(actions),
            "customers_updated": update_result.get('updated', 0)
        })

        return results
