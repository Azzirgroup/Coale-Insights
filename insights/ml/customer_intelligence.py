# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Customer Intelligence Analytics
Comprehensive customer analytics including CLV, churn prediction, health scoring, and geographic analysis
"""

import frappe
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from insights.ml.base import BaseMLModel


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
    """
    
    # 24 month lookback for performance
    DATE_FILTER = "AND si.posting_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)"
    CUSTOMER_THRESHOLD = 5000  # Async threshold
    
    def __init__(self):
        super().__init__()
        self.model_name = "CustomerIntelligence"
        
    # ==================== DATA COLLECTION ====================
    
    def _get_customer_transactions(self) -> pd.DataFrame:
        """Get comprehensive customer transaction data (last 24 months)"""
        query = f"""
            SELECT 
                c.name as customer_id,
                c.customer_name,
                c.customer_group,
                c.territory,
                c.creation as customer_since,
                c.account_manager,
                si.name as invoice_id,
                si.posting_date,
                si.due_date,
                si.grand_total,
                si.net_total,
                si.outstanding_amount,
                si.status,
                DATEDIFF(CURDATE(), si.posting_date) as days_since_transaction,
                CASE 
                    WHEN si.outstanding_amount = 0 THEN 'Paid'
                    WHEN si.due_date < CURDATE() THEN 'Overdue'
                    ELSE 'Outstanding'
                END as payment_status
            FROM `tabCustomer` c
            LEFT JOIN `tabSales Invoice` si ON c.name = si.customer AND si.docstatus = 1
                {self.DATE_FILTER}
            WHERE c.disabled = 0
            ORDER BY c.name, si.posting_date DESC
        """
        return self.get_training_data(query)
    
    def _get_territory_data(self) -> pd.DataFrame:
        """Get territory hierarchy for geographic analysis"""
        query = """
            SELECT 
                name as territory,
                parent_territory,
                territory_manager,
                lft, rgt, is_group
            FROM `tabTerritory`
            ORDER BY lft
        """
        return self.get_training_data(query)
    
    def _get_customer_items(self) -> pd.DataFrame:
        """Get customer purchase details by item (last 24 months)"""
        query = f"""
            SELECT 
                si.customer as customer_id,
                sii.item_code,
                sii.item_name,
                i.item_group,
                i.brand,
                SUM(sii.qty) as total_qty,
                SUM(sii.amount) as total_amount,
                COUNT(DISTINCT si.name) as order_count
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON sii.parent = si.name
            LEFT JOIN `tabItem` i ON sii.item_code = i.name
            WHERE si.docstatus = 1
                {self.DATE_FILTER}
            GROUP BY si.customer, sii.item_code
        """
        return self.get_training_data(query)
    
    def _get_payment_history(self) -> pd.DataFrame:
        """Get customer payment patterns (last 24 months)"""
        query = """
            SELECT 
                pe.party as customer_id,
                pe.posting_date as payment_date,
                pe.paid_amount,
                per.reference_name as invoice,
                si.posting_date as invoice_date,
                DATEDIFF(pe.posting_date, si.posting_date) as days_to_pay
            FROM `tabPayment Entry` pe
            JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
            LEFT JOIN `tabSales Invoice` si ON per.reference_name = si.name
            WHERE pe.docstatus = 1 
                AND pe.payment_type = 'Receive'
                AND pe.party_type = 'Customer'
                AND pe.posting_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
        """
        return self.get_training_data(query)
    
    def _get_quotation_data(self) -> pd.DataFrame:
        """Get quotation conversion data (last 24 months)"""
        query = """
            SELECT 
                q.party_name as customer_id,
                q.name as quotation,
                q.transaction_date,
                q.grand_total,
                q.status,
                CASE WHEN q.status = 'Ordered' THEN 1 ELSE 0 END as converted
            FROM `tabQuotation` q
            WHERE q.docstatus = 1 
                AND q.quotation_to = 'Customer'
                AND q.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
        """
        return self.get_training_data(query)
    
    # ==================== CLV ANALYTICS ====================
    
    def calculate_clv(self, customer_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Customer Lifetime Value using historical + predictive methods
        
        Components:
        - Historical CLV: Total revenue to date
        - Predictive CLV: Based on purchase patterns (BG/NBD simplified)
        - CLV Tier: Bronze/Silver/Gold/Platinum/Diamond
        """
        # Calculate overdue count per customer before aggregation
        if 'payment_status' in customer_df.columns:
            overdue_df = customer_df[customer_df['payment_status'] == 'Overdue'].groupby('customer_id').size().reset_index(name='overdue_count')
        else:
            overdue_df = pd.DataFrame(columns=['customer_id', 'overdue_count'])
        
        # Group by customer
        clv_data = customer_df.groupby('customer_id').agg({
            'grand_total': ['sum', 'mean', 'count'],
            'posting_date': ['min', 'max'],
            'customer_name': 'first',
            'customer_group': 'first',
            'territory': 'first',
            'outstanding_amount': 'sum'
        }).reset_index()
        
        clv_data.columns = [
            'customer_id', 'historical_clv', 'avg_order_value', 'order_count',
            'first_purchase', 'last_purchase', 'customer_name', 'customer_group', 
            'territory', 'outstanding_amount'
        ]
        
        # Merge overdue count
        clv_data = clv_data.merge(overdue_df, on='customer_id', how='left')
        clv_data['overdue_count'] = clv_data['overdue_count'].fillna(0).astype(int)
        
        # Handle NaN values
        clv_data['historical_clv'] = clv_data['historical_clv'].fillna(0)
        clv_data['avg_order_value'] = clv_data['avg_order_value'].fillna(0)
        clv_data['order_count'] = clv_data['order_count'].fillna(0)
        clv_data['outstanding_amount'] = clv_data['outstanding_amount'].fillna(0)
        
        # Calculate customer lifespan in months
        clv_data['first_purchase'] = pd.to_datetime(clv_data['first_purchase'])
        clv_data['last_purchase'] = pd.to_datetime(clv_data['last_purchase'])
        
        # Handle customers with no purchases
        now = pd.Timestamp.now()
        clv_data['first_purchase'] = clv_data['first_purchase'].fillna(now)
        clv_data['last_purchase'] = clv_data['last_purchase'].fillna(now)
        
        clv_data['lifespan_months'] = (
            (clv_data['last_purchase'] - clv_data['first_purchase']).dt.days / 30.44
        ).clip(lower=1)
        
        # Purchase frequency (orders per month)
        clv_data['purchase_frequency'] = clv_data['order_count'] / clv_data['lifespan_months']
        
        # Recency (days since last purchase)
        clv_data['recency_days'] = (now - clv_data['last_purchase']).dt.days
        
        # Predictive CLV (simplified BG/NBD: project 12 months forward)
        clv_data['predicted_12m_clv'] = (
            clv_data['purchase_frequency'] * 12 * clv_data['avg_order_value']
        )
        
        # Customer tenure factor (longer customers get loyalty boost)
        tenure_months = (now - clv_data['first_purchase']).dt.days / 30.44
        clv_data['tenure_factor'] = np.minimum(tenure_months / 24, 1.5)
        
        # Adjusted predictive CLV
        clv_data['adjusted_predicted_clv'] = (
            clv_data['predicted_12m_clv'] * clv_data['tenure_factor']
        )
        
        # Total CLV (historical + predicted)
        clv_data['total_clv'] = clv_data['historical_clv'] + clv_data['adjusted_predicted_clv']
        
        # CLV Score (normalized 0-100)
        max_clv = clv_data['total_clv'].quantile(0.99) or 1
        clv_data['clv_score'] = (clv_data['total_clv'] / max_clv * 100).clip(0, 100)
        
        # CLV Tier - use score-based assignment to handle edge cases
        def assign_clv_tier(score):
            if score >= 80:
                return 'Diamond'
            elif score >= 60:
                return 'Platinum'
            elif score >= 40:
                return 'Gold'
            elif score >= 20:
                return 'Silver'
            else:
                return 'Bronze'
        
        clv_data['clv_tier'] = clv_data['clv_score'].apply(assign_clv_tier)
        
        # ==================== CLV COMPONENT SCORES ====================
        # Calculate individual component scores (0-100 scale) for the CLV breakdown
        clv_data = self._calculate_clv_components(clv_data, tenure_months)
        
        # ==================== RFM SEGMENTATION ====================
        # Calculate RFM scores using quintiles (1-5)
        clv_data = self._calculate_rfm_segment(clv_data)
        
        return clv_data
    
    def _calculate_clv_components(self, df: pd.DataFrame, tenure_months: pd.Series) -> pd.DataFrame:
        """
        Calculate CLV component scores for detailed breakdown:
        - Revenue Score: Based on historical revenue relative to peers
        - Engagement Score: Based on order frequency and recency
        - Longevity Score: Based on customer tenure/relationship length
        - Growth Score: Based on predicted CLV growth potential
        """
        if df.empty:
            return df
        
        # Revenue Score (0-100): Percentile rank of historical CLV
        max_revenue = df['historical_clv'].quantile(0.99) or 1
        df['revenue_score'] = (df['historical_clv'] / max_revenue * 100).clip(0, 100)
        
        # Engagement Score (0-100): Combination of frequency and recency
        # Higher frequency = better, Lower recency = better
        max_freq = df['purchase_frequency'].quantile(0.99) or 1
        freq_score = (df['purchase_frequency'] / max_freq * 50).clip(0, 50)
        
        # Recency score: inverse - more recent (lower days) = higher score
        max_recency = df['recency_days'].quantile(0.99) or 365
        recency_score = ((max_recency - df['recency_days'].clip(0, max_recency)) / max_recency * 50).clip(0, 50)
        
        df['engagement_score'] = (freq_score + recency_score).clip(0, 100)
        
        # Longevity Score (0-100): Based on customer tenure
        # Cap at 24 months for 100% score
        df['longevity_score'] = (tenure_months / 24 * 100).clip(0, 100)
        
        # Growth Score (0-100): Predicted CLV relative to historical
        # Shows growth potential - higher predicted vs historical = higher growth
        # Use ratio of predicted to historical, capped
        historical_safe = df['historical_clv'].replace(0, 1)
        growth_ratio = df['predicted_12m_clv'] / historical_safe
        # Scale: ratio of 1 = 50%, ratio of 2+ = 100%
        df['growth_score'] = ((growth_ratio - 0.5) * 50).clip(0, 100)
        
        return df
    
    def _calculate_rfm_segment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) segment for each customer
        
        Segments:
        - Champions: Best customers (R>=4, F>=4, M>=4)
        - Loyal Customers: Regular high-value buyers
        - Potential Loyalists: Recent with medium engagement
        - New Customers: Very recent, low frequency
        - Promising: Recent, low frequency
        - Need Attention: Medium across all metrics
        - About to Sleep: Declining engagement
        - At Risk: Were good, haven't bought recently
        - Can't Lose: High value but inactive
        - Hibernating: Low activity all around
        - Lost: Haven't purchased in a long time
        """
        if df.empty:
            return df
        
        # RFM Segment mapping
        RFM_SEGMENTS = {
            (5, 5, 5): "Champions", (5, 5, 4): "Champions", (5, 4, 5): "Champions",
            (5, 4, 4): "Champions", (4, 5, 5): "Champions",
            (4, 5, 4): "Loyal Customers", (4, 4, 5): "Loyal Customers", (4, 4, 4): "Loyal Customers",
            (5, 3, 3): "Potential Loyalists", (5, 3, 4): "Potential Loyalists",
            (5, 2, 3): "Potential Loyalists", (4, 3, 3): "Potential Loyalists",
            (5, 1, 1): "New Customers", (5, 1, 2): "New Customers",
            (5, 2, 1): "New Customers", (5, 2, 2): "New Customers",
            (4, 1, 1): "Promising", (4, 1, 2): "Promising", (4, 2, 1): "Promising",
            (3, 3, 3): "Need Attention", (3, 3, 4): "Need Attention",
            (3, 4, 3): "Need Attention", (3, 4, 4): "Need Attention",
            (3, 2, 2): "About to Sleep", (3, 2, 3): "About to Sleep", (3, 1, 2): "About to Sleep",
            (2, 5, 5): "At Risk", (2, 5, 4): "At Risk", (2, 4, 5): "At Risk", (2, 4, 4): "At Risk",
            (1, 5, 5): "Can't Lose", (1, 5, 4): "Can't Lose", (1, 4, 5): "Can't Lose",
            (2, 2, 2): "Hibernating", (2, 2, 3): "Hibernating", (2, 3, 2): "Hibernating", (1, 2, 2): "Hibernating",
            (1, 1, 1): "Lost", (1, 1, 2): "Lost", (1, 2, 1): "Lost", (2, 1, 1): "Lost",
        }
        
        def get_rfm_segment(r: int, f: int, m: int) -> str:
            """Get segment name from RFM scores"""
            segment = RFM_SEGMENTS.get((r, f, m))
            if segment:
                return segment
            # Fallback logic
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            elif r >= 4 and f >= 3:
                return "Loyal Customers"
            elif r >= 4 and f <= 2:
                return "New Customers"
            elif r == 3 and f >= 3:
                return "Need Attention"
            elif r <= 2 and f >= 4:
                return "At Risk"
            elif r <= 2 and f >= 3 and m >= 4:
                return "Can't Lose"
            elif r <= 2 and f <= 2:
                return "Hibernating"
            else:
                return "Need Attention"
        
        try:
            # Calculate R score (Recency) - lower recency_days is better = higher score
            df['R'] = pd.qcut(
                df['recency_days'].rank(method='first'), 
                q=5, labels=[5, 4, 3, 2, 1], duplicates='drop'
            ).astype(int)
        except ValueError:
            # Not enough unique values for 5 bins
            df['R'] = 3
        
        try:
            # Calculate F score (Frequency) - higher order_count is better
            df['F'] = pd.qcut(
                df['order_count'].rank(method='first'), 
                q=5, labels=[1, 2, 3, 4, 5], duplicates='drop'
            ).astype(int)
        except ValueError:
            df['F'] = 3
        
        try:
            # Calculate M score (Monetary) - higher historical_clv is better
            df['M'] = pd.qcut(
                df['historical_clv'].rank(method='first'), 
                q=5, labels=[1, 2, 3, 4, 5], duplicates='drop'
            ).astype(int)
        except ValueError:
            df['M'] = 3
        
        # Calculate RFM Score string (e.g., "555" for Champions)
        df['rfm_score'] = df['R'].astype(str) + df['F'].astype(str) + df['M'].astype(str)
        
        # Assign RFM Segment
        df['rfm_segment'] = df.apply(
            lambda x: get_rfm_segment(int(x['R']), int(x['F']), int(x['M'])), 
            axis=1
        )
        
        return df
    
    # ==================== CHURN PREDICTION ====================
    
    def calculate_churn_risk(self, customer_df: pd.DataFrame, clv_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate churn risk score based on behavioral indicators
        
        Indicators:
        - Declining order frequency
        - Increasing order gaps
        - Reduced order values
        - Outstanding receivables
        - Recency vs. typical purchase cycle
        """
        churn_data = clv_df.copy()
        
        # Get recent vs. historical patterns per customer
        customer_trends = []
        
        for customer_id in clv_df['customer_id'].unique():
            cust_txns = customer_df[customer_df['customer_id'] == customer_id].copy()
            
            if len(cust_txns) < 2 or cust_txns['invoice_id'].isna().all():
                customer_trends.append({
                    'customer_id': customer_id,
                    'frequency_trend': 0,
                    'value_trend': 0,
                    'gap_increasing': 0
                })
                continue
            
            cust_txns = cust_txns[cust_txns['invoice_id'].notna()].sort_values('posting_date')
            cust_txns['posting_date'] = pd.to_datetime(cust_txns['posting_date'])
            
            if len(cust_txns) < 2:
                customer_trends.append({
                    'customer_id': customer_id,
                    'frequency_trend': 0,
                    'value_trend': 0,
                    'gap_increasing': 0
                })
                continue
            
            # Split into recent (last 3 months) vs historical
            cutoff = datetime.now() - timedelta(days=90)
            recent = cust_txns[cust_txns['posting_date'] >= cutoff]
            historical = cust_txns[cust_txns['posting_date'] < cutoff]
            
            # Frequency trend (negative = declining)
            recent_freq = len(recent) / 3 if len(recent) > 0 else 0
            hist_months = max(1, (cutoff - cust_txns['posting_date'].min()).days / 30)
            hist_freq = len(historical) / hist_months if len(historical) > 0 else recent_freq
            freq_trend = (recent_freq - hist_freq) / max(hist_freq, 0.1) if hist_freq > 0 else 0
            
            # Value trend
            recent_aov = recent['grand_total'].mean() if len(recent) > 0 else 0
            hist_aov = historical['grand_total'].mean() if len(historical) > 0 else recent_aov
            value_trend = (recent_aov - hist_aov) / max(hist_aov, 1) if hist_aov > 0 else 0
            
            # Gap analysis
            cust_txns['days_between'] = cust_txns['posting_date'].diff().dt.days
            avg_gap = cust_txns['days_between'].mean() or 30
            recent_gaps = cust_txns.tail(3)['days_between'].mean() or avg_gap
            gap_increasing = 1 if recent_gaps > avg_gap * 1.5 else 0
            
            customer_trends.append({
                'customer_id': customer_id,
                'frequency_trend': float(freq_trend) if not pd.isna(freq_trend) else 0,
                'value_trend': float(value_trend) if not pd.isna(value_trend) else 0,
                'gap_increasing': gap_increasing
            })
        
        trends_df = pd.DataFrame(customer_trends)
        churn_data = churn_data.merge(trends_df, on='customer_id', how='left')
        
        # Fill NaN values
        churn_data['frequency_trend'] = churn_data['frequency_trend'].fillna(0)
        churn_data['value_trend'] = churn_data['value_trend'].fillna(0)
        churn_data['gap_increasing'] = churn_data['gap_increasing'].fillna(0)
        
        # Calculate churn risk score (0-100)
        churn_data['churn_score'] = 50.0
        
        # Recency factor (more days = higher risk)
        avg_purchase_cycle = 30
        if churn_data['order_count'].sum() > 0:
            avg_purchase_cycle = max(30, churn_data['lifespan_months'].mean() * 30 / max(1, churn_data['order_count'].mean()))
        
        churn_data['recency_risk'] = np.minimum(
            (churn_data['recency_days'] / max(avg_purchase_cycle, 30)) * 20, 30
        )
        churn_data['churn_score'] += churn_data['recency_risk']
        
        # Frequency trend (declining = higher risk)
        churn_data['churn_score'] -= churn_data['frequency_trend'].clip(-2, 2) * 10
        
        # Value trend (declining = higher risk)
        churn_data['churn_score'] -= churn_data['value_trend'].clip(-2, 2) * 10
        
        # Gap increasing = higher risk
        churn_data['churn_score'] += churn_data['gap_increasing'] * 15
        
        # Outstanding receivables impact
        receivables_ratio = churn_data['outstanding_amount'] / (churn_data['historical_clv'] + 1)
        churn_data['churn_score'] += np.minimum(receivables_ratio * 10, 15)
        
        # Clip to 0-100
        churn_data['churn_score'] = churn_data['churn_score'].clip(0, 100)
        
        # Churn risk category
        churn_data['churn_risk'] = pd.cut(
            churn_data['churn_score'],
            bins=[-np.inf, 30, 50, 70, np.inf],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        return churn_data
    
    # ==================== CUSTOMER HEALTH SCORING ====================
    
    def calculate_health_score(self, churn_df: pd.DataFrame, payment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite customer health score
        
        Components:
        - Revenue contribution (20%)
        - Purchase engagement (20%)
        - Payment behavior (20%)
        - Relationship longevity (20%)
        - Growth potential (20%)
        """
        health_data = churn_df.copy()
        
        # Payment behavior scores
        if not payment_df.empty:
            payment_metrics = payment_df.groupby('customer_id').agg({
                'days_to_pay': ['mean', 'std'],
                'paid_amount': 'count'
            }).reset_index()
            payment_metrics.columns = ['customer_id', 'avg_days_to_pay', 'payment_std', 'payment_count']
            health_data = health_data.merge(payment_metrics, on='customer_id', how='left')
        else:
            health_data['avg_days_to_pay'] = 30
            health_data['payment_std'] = 0
            health_data['payment_count'] = 0
        
        health_data['avg_days_to_pay'] = health_data['avg_days_to_pay'].fillna(30)
        health_data['payment_std'] = health_data['payment_std'].fillna(0)
        health_data['payment_count'] = health_data['payment_count'].fillna(0)
        
        # 1. Revenue contribution (percentile rank)
        health_data['revenue_score'] = (
            health_data['historical_clv'].rank(pct=True) * 100
        )
        
        # 2. Purchase engagement (frequency + recency)
        freq_rank = health_data['purchase_frequency'].rank(pct=True) * 50
        recency_rank = (1 - health_data['recency_days'].rank(pct=True)) * 50
        health_data['engagement_score'] = freq_rank + recency_rank
        
        # 3. Payment behavior (faster = better)
        max_days = max(health_data['avg_days_to_pay'].max(), 60)
        health_data['payment_score'] = (
            (1 - health_data['avg_days_to_pay'] / max_days) * 100
        ).clip(0, 100)
        
        # 4. Relationship longevity
        tenure_days = (pd.Timestamp.now() - health_data['first_purchase']).dt.days
        health_data['longevity_score'] = (
            tenure_days.rank(pct=True) * 100
        )
        
        # 5. Growth potential (positive trends)
        health_data['growth_score'] = (
            50 +
            health_data['frequency_trend'].clip(-2, 2) * 15 +
            health_data['value_trend'].clip(-2, 2) * 10
        ).clip(0, 100)
        
        # Composite health score
        health_data['health_score'] = (
            health_data['revenue_score'] * 0.20 +
            health_data['engagement_score'] * 0.20 +
            health_data['payment_score'] * 0.20 +
            health_data['longevity_score'] * 0.20 +
            health_data['growth_score'] * 0.20
        )
        
        # Health category
        health_data['health_status'] = pd.cut(
            health_data['health_score'],
            bins=[-np.inf, 40, 60, 80, np.inf],
            labels=['Critical', 'At Risk', 'Healthy', 'Excellent']
        )
        
        return health_data
    
    # ==================== GEOGRAPHIC ANALYSIS ====================
    
    def analyze_geography(self, health_df: pd.DataFrame, territory_df: pd.DataFrame) -> Dict[str, Any]:
        """Geographic distribution analysis using ERPNext territories"""
        # Territory-level analysis
        territory_analysis = health_df.groupby('territory').agg({
            'customer_id': 'count',
            'historical_clv': 'sum',
            'avg_order_value': 'mean',
            'churn_score': 'mean',
            'health_score': 'mean',
            'order_count': 'sum'
        }).reset_index()
        territory_analysis.columns = [
            'territory', 'customer_count', 'total_revenue', 'avg_order_value',
            'avg_churn_risk', 'avg_health_score', 'total_orders'
        ]
        territory_analysis = territory_analysis.sort_values('total_revenue', ascending=False)
        
        # Merge with territory hierarchy
        if not territory_df.empty:
            territory_analysis = territory_analysis.merge(
                territory_df[['territory', 'parent_territory', 'territory_manager']],
                on='territory',
                how='left'
            )
        
        # Customer group analysis
        group_analysis = health_df.groupby('customer_group').agg({
            'customer_id': 'count',
            'historical_clv': 'sum',
            'avg_order_value': 'mean',
            'health_score': 'mean'
        }).reset_index()
        group_analysis.columns = [
            'customer_group', 'customer_count', 'total_revenue', 'avg_order_value', 'avg_health_score'
        ]
        group_analysis = group_analysis.sort_values('total_revenue', ascending=False)
        
        # Territory performance metrics
        total_revenue = territory_analysis['total_revenue'].sum()
        territory_analysis['revenue_share'] = (
            territory_analysis['total_revenue'] / total_revenue * 100
        ).round(2) if total_revenue > 0 else 0
        
        # Penetration rate
        total_customers = territory_analysis['customer_count'].sum()
        territory_analysis['customer_share'] = (
            territory_analysis['customer_count'] / total_customers * 100
        ).round(2) if total_customers > 0 else 0
        
        # Map data for frontend
        map_data = territory_analysis[[
            'territory', 'customer_count', 'total_revenue', 'avg_health_score', 'revenue_share'
        ]].to_dict('records')
        
        return {
            'territory_analysis': territory_analysis.to_dict('records'),
            'customer_group_analysis': group_analysis.to_dict('records'),
            'map_data': map_data,
            'top_territories': territory_analysis.head(10).to_dict('records'),
            'coverage': {
                'territories_covered': len(territory_analysis),
                'customer_groups_covered': len(group_analysis),
                'total_revenue': float(total_revenue),
                'total_customers': int(total_customers)
            }
        }
    
    # ==================== PRODUCT AFFINITY ====================
    
    def analyze_product_affinity(self, items_df: pd.DataFrame, health_df: pd.DataFrame) -> Dict[str, Any]:
        """Product category preferences by customer segment"""
        if items_df.empty:
            return {'tier_preferences': [], 'top_categories': [], 'brand_analysis': []}
        
        # Merge with customer segments
        affinity_data = items_df.merge(
            health_df[['customer_id', 'clv_tier', 'health_status']], 
            on='customer_id', 
            how='left'
        )
        
        # Category preferences by CLV tier
        tier_preferences = affinity_data.groupby(['clv_tier', 'item_group']).agg({
            'total_amount': 'sum',
            'customer_id': 'nunique',
            'order_count': 'sum'
        }).reset_index()
        tier_preferences.columns = ['clv_tier', 'item_group', 'total_revenue', 'customer_count', 'order_count']
        
        # Top categories overall
        top_categories = affinity_data.groupby('item_group').agg({
            'total_amount': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        top_categories.columns = ['item_group', 'total_revenue', 'customer_count']
        top_categories = top_categories.sort_values('total_revenue', ascending=False)
        
        # Brand preferences
        brand_analysis = affinity_data.groupby('brand').agg({
            'total_amount': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        brand_analysis.columns = ['brand', 'total_revenue', 'customer_count']
        brand_analysis = brand_analysis.sort_values('total_revenue', ascending=False)
        
        return {
            'tier_preferences': tier_preferences.to_dict('records'),
            'top_categories': top_categories.head(20).to_dict('records'),
            'brand_analysis': brand_analysis.head(20).to_dict('records')
        }
    
    # ==================== 80/20 PARETO ANALYSIS ====================
    
    def pareto_analysis(self, health_df: pd.DataFrame) -> Dict[str, Any]:
        """80/20 analysis - identify top customers by revenue contribution"""
        if health_df.empty or health_df['historical_clv'].sum() == 0:
            return {
                'total_customers': 0, 'total_revenue': 0, 'top_80_percent_customers': 0,
                'top_10_percent_contribute': 0, 'top_20_percent_contribute': 0,
                'top_customers': [], 'pareto_curve': []
            }
        
        # Sort by revenue
        sorted_df = health_df.sort_values('historical_clv', ascending=False).copy()
        sorted_df['cumulative_revenue'] = sorted_df['historical_clv'].cumsum()
        total_revenue = sorted_df['historical_clv'].sum()
        sorted_df['cumulative_percent'] = (sorted_df['cumulative_revenue'] / total_revenue) * 100
        
        # Find 80% cutoff
        top_80 = sorted_df[sorted_df['cumulative_percent'] <= 80]
        top_80_percent = (len(top_80) / len(sorted_df)) * 100 if len(sorted_df) > 0 else 0
        
        # Revenue concentration
        n_10 = max(1, int(len(sorted_df) * 0.1))
        n_20 = max(1, int(len(sorted_df) * 0.2))
        top_10_revenue = sorted_df.head(n_10)['historical_clv'].sum()
        top_20_revenue = sorted_df.head(n_20)['historical_clv'].sum()
        
        return {
            'total_customers': len(sorted_df),
            'total_revenue': float(total_revenue),
            'top_80_percent_customers': round(top_80_percent, 1),
            'top_10_percent_contribute': round((top_10_revenue / total_revenue) * 100, 1) if total_revenue > 0 else 0,
            'top_20_percent_contribute': round((top_20_revenue / total_revenue) * 100, 1) if total_revenue > 0 else 0,
            'top_customers': sorted_df.head(20)[[
                'customer_id', 'customer_name', 'historical_clv', 'order_count',
                'avg_order_value', 'clv_tier', 'health_status'
            ]].assign(cumulative_percent=sorted_df.head(20)['cumulative_percent']).to_dict('records'),
            'pareto_curve': sorted_df[['customer_name', 'historical_clv', 'cumulative_percent']].head(50).to_dict('records')
        }
    
    # ==================== COHORT ANALYSIS ====================
    
    def cohort_analysis(self, customer_df: pd.DataFrame) -> Dict[str, Any]:
        """Customer retention cohort analysis"""
        df = customer_df[customer_df['invoice_id'].notna()].copy()
        
        if df.empty:
            return {'cohort_retention': [], 'average_retention': {}, 'cohort_count': 0}
        
        df['posting_date'] = pd.to_datetime(df['posting_date'])
        
        # Get first purchase date per customer (cohort)
        first_purchase = df.groupby('customer_id')['posting_date'].min().reset_index()
        first_purchase.columns = ['customer_id', 'first_purchase']
        first_purchase['cohort_month'] = first_purchase['first_purchase'].dt.to_period('M')
        
        df = df.merge(first_purchase[['customer_id', 'cohort_month']], on='customer_id')
        df['transaction_month'] = df['posting_date'].dt.to_period('M')
        
        # Calculate period number
        df['period_number'] = (
            df['transaction_month'].astype('int64') - df['cohort_month'].astype('int64')
        )
        
        # Cohort matrix
        cohort_data = df.groupby(['cohort_month', 'period_number']).agg({
            'customer_id': 'nunique'
        }).reset_index()
        cohort_data.columns = ['cohort_month', 'period_number', 'customers']
        
        # Pivot for retention matrix
        cohort_pivot = cohort_data.pivot(
            index='cohort_month', columns='period_number', values='customers'
        ).fillna(0)
        
        # Calculate retention percentages
        cohort_sizes = cohort_pivot.iloc[:, 0] if len(cohort_pivot.columns) > 0 else pd.Series([0])
        retention_matrix = cohort_pivot.divide(cohort_sizes.replace(0, 1), axis=0) * 100
        
        # Convert to serializable format
        cohort_result = []
        for idx, row in retention_matrix.iterrows():
            cohort_result.append({
                'cohort': str(idx),
                'size': int(cohort_sizes.get(idx, 0)),
                'retention': {int(k): round(v, 1) for k, v in row.items() if not pd.isna(v)}
            })
        
        # Average retention by period
        avg_retention = retention_matrix.mean().to_dict()
        avg_retention = {int(k): round(v, 1) for k, v in avg_retention.items() if not pd.isna(v)}
        
        return {
            'cohort_retention': cohort_result[-12:],
            'average_retention': avg_retention,
            'cohort_count': len(cohort_result)
        }
    
    # ==================== NEXT BEST ACTION ====================
    
    def get_next_best_actions(self, health_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """AI-driven next best action recommendations per customer"""
        actions = []
        
        for _, customer in health_df.iterrows():
            customer_actions = {
                'customer_id': customer['customer_id'],
                'customer_name': customer['customer_name'],
                'clv_tier': str(customer['clv_tier']) if pd.notna(customer['clv_tier']) else 'Unknown',
                'health_status': str(customer['health_status']) if pd.notna(customer['health_status']) else 'Unknown',
                'churn_risk': str(customer['churn_risk']) if pd.notna(customer['churn_risk']) else 'Unknown',
                'recommendations': []
            }
            
            churn_risk = str(customer.get('churn_risk', ''))
            clv_tier = str(customer.get('clv_tier', ''))
            health_status = str(customer.get('health_status', ''))
            recency_days = customer.get('recency_days', 0) or 0
            outstanding = customer.get('outstanding_amount', 0) or 0
            aov = customer.get('avg_order_value', 0) or 0
            freq_trend = customer.get('frequency_trend', 0) or 0
            value_trend = customer.get('value_trend', 0) or 0
            
            # Churn prevention
            if churn_risk in ['High', 'Critical']:
                customer_actions['recommendations'].append({
                    'action': 'CHURN_PREVENTION',
                    'priority': 'High',
                    'description': f"Customer at {churn_risk} churn risk. Last purchase {int(recency_days)} days ago.",
                    'suggestion': "Schedule personal outreach call, offer loyalty discount, or exclusive preview of new products."
                })
            
            # Upsell opportunity
            if clv_tier in ['Gold', 'Platinum', 'Diamond'] and health_status in ['Healthy', 'Excellent']:
                customer_actions['recommendations'].append({
                    'action': 'UPSELL_OPPORTUNITY',
                    'priority': 'Medium',
                    'description': f"High-value customer with strong engagement. AOV: {aov:,.0f}",
                    'suggestion': "Introduce premium product lines, volume discounts, or exclusive partnerships."
                })
            
            # Payment follow-up
            if outstanding > 0:
                priority = 'High' if outstanding > aov * 2 else 'Medium'
                customer_actions['recommendations'].append({
                    'action': 'PAYMENT_FOLLOW_UP',
                    'priority': priority,
                    'description': f"Outstanding balance: {outstanding:,.0f}",
                    'suggestion': "Send payment reminder, offer payment plan if needed."
                })
            
            # Re-engagement
            if recency_days > 60 and clv_tier in ['Silver', 'Gold', 'Platinum', 'Diamond']:
                customer_actions['recommendations'].append({
                    'action': 'RE_ENGAGEMENT',
                    'priority': 'High',
                    'description': f"Valuable customer inactive for {int(recency_days)} days.",
                    'suggestion': "Send 'We miss you' campaign with personalized offer based on past purchases."
                })
            
            # Growth opportunity
            if freq_trend > 0.2 and value_trend > 0.1:
                customer_actions['recommendations'].append({
                    'action': 'GROWTH_OPPORTUNITY',
                    'priority': 'Medium',
                    'description': "Customer showing positive growth trends in frequency and order value.",
                    'suggestion': "Consider for VIP program, early access to new products, or referral program."
                })
            
            # New customer nurturing
            if customer.get('order_count', 0) <= 2 and recency_days < 60:
                customer_actions['recommendations'].append({
                    'action': 'NEW_CUSTOMER_NURTURE',
                    'priority': 'Medium',
                    'description': "New customer - critical period for relationship building.",
                    'suggestion': "Send welcome series, offer first-time buyer discount on next purchase, request feedback."
                })
            
            if customer_actions['recommendations']:
                actions.append(customer_actions)
        
        # Sort by priority
        actions.sort(key=lambda x: (
            0 if any(r['priority'] == 'High' for r in x['recommendations']) else 1,
            -len(x['recommendations'])
        ))
        
        return actions[:100]
    
    # ==================== UPDATE CUSTOMER SCORES ====================
    
    def update_customer_scores(self, health_df: pd.DataFrame) -> Dict[str, Any]:
        """Write calculated scores back to Customer doctype custom fields"""
        updated = 0
        errors = []
        
        for _, row in health_df.iterrows():
            try:
                customer_id = row['customer_id']
                
                # Check if custom fields exist
                if not frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": "custom_clv_tier"}):
                    return {
                        "status": "skipped",
                        "message": "Custom fields not installed. Run 'bench migrate' to create them."
                    }
                
                # Update customer record
                frappe.db.set_value('Customer', customer_id, {
                    'custom_clv_tier': str(row['clv_tier']) if pd.notna(row['clv_tier']) else None,
                    'custom_clv_score': float(row['clv_score']) if pd.notna(row['clv_score']) else 0,
                    'custom_churn_risk': str(row['churn_risk']) if pd.notna(row['churn_risk']) else None,
                    'custom_churn_score': float(row['churn_score']) if pd.notna(row['churn_score']) else 0,
                    'custom_health_score': float(row['health_score']) if pd.notna(row['health_score']) else 0,
                    'custom_health_status': str(row['health_status']) if pd.notna(row['health_status']) else None,
                    'custom_last_ml_update': datetime.now()
                }, update_modified=False)
                
                updated += 1
                
            except Exception as e:
                errors.append(f"{row['customer_id']}: {str(e)}")
        
        if updated > 0:
            frappe.db.commit()
        
        return {
            "status": "success",
            "updated": updated,
            "errors": errors[:10] if errors else []
        }
    
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
    
    def predict(self, customer: str = None) -> Dict[str, Any]:
        """Get cached or fresh predictions"""
        cached = self.get_cached_results("customer_intelligence")
        if not cached:
            cached = self.train()
        
        if customer:
            customers = cached.get('customers', [])
            cust_data = next((c for c in customers if c['customer_id'] == customer), None)
            if cust_data:
                actions = [a for a in cached.get('next_best_actions', []) if a['customer_id'] == customer]
                return {"status": "success", "customer": cust_data, "actions": actions[0] if actions else None}
            return {"status": "error", "message": "Customer not found"}
        
        return cached


# ==================== API FUNCTIONS ====================

@frappe.whitelist()
def run_customer_intelligence(update_customers: bool = True, async_mode: bool = False) -> Dict[str, Any]:
    """Run comprehensive customer intelligence analysis"""
    # Check customer count for async decision
    customer_count = frappe.db.count("Customer", {"disabled": 0})
    
    if async_mode or customer_count > CustomerIntelligence.CUSTOMER_THRESHOLD:
        # Run async via background job
        job = frappe.enqueue(
            "insights.ml.customer_intelligence._run_customer_intelligence_job",
            queue="long",
            timeout=3600,
            update_customers=update_customers
        )
        return {
            "status": "queued",
            "message": f"Analysis queued for {customer_count} customers",
            "job_id": job.id if hasattr(job, 'id') else str(job)
        }
    
    model = CustomerIntelligence()
    return model.train(update_customers=update_customers)


def _run_customer_intelligence_job(update_customers: bool = True):
    """Background job for customer intelligence"""
    try:
        model = CustomerIntelligence()
        result = model.train(update_customers=update_customers)
        
        # Store job result
        frappe.cache.set_value(
            "customer_intelligence_job_result",
            {"status": "completed", "result": result},
            expires_in_sec=3600
        )
        
        frappe.logger().info(f"Customer intelligence completed: {result.get('summary', {}).get('total_customers', 0)} customers")
        return result
    except Exception as e:
        frappe.log_error(f"Customer intelligence job failed: {str(e)}", "ML Scheduler")
        frappe.cache.set_value(
            "customer_intelligence_job_result",
            {"status": "error", "message": str(e)},
            expires_in_sec=3600
        )
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_customer_intelligence() -> Dict[str, Any]:
    """Get cached customer intelligence or run if not available"""
    model = CustomerIntelligence()
    cached = model.get_cached_results("customer_intelligence")
    
    if cached:
        return cached
    
    return model.train()


@frappe.whitelist()
def get_customer_intelligence_status() -> Dict[str, Any]:
    """Check status of async customer intelligence job"""
    result = frappe.cache.get_value("customer_intelligence_job_result")
    if result:
        return result
    return {"status": "not_found", "message": "No recent job found"}


@frappe.whitelist()
def get_customer_360_detail(customer_id: str, include_purchases: bool = True, include_recommendations: bool = True) -> Dict[str, Any]:
    """
    Get comprehensive 360-degree view of a specific customer
    Includes purchase history, cross-sell recommendations, and purchase patterns
    """
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    customers = result.get('customers', [])
    customer = next((c for c in customers if c['customer_id'] == customer_id), None)
    
    if not customer:
        return {"status": "error", "message": "Customer not found"}
    
    response = {
        "status": "success",
        "customer": customer,
    }
    
    # Get purchase history
    if include_purchases:
        purchase_history = _get_customer_purchase_history(customer_id)
        response["purchase_history"] = purchase_history
        response["purchase_patterns"] = _analyze_customer_purchase_patterns(purchase_history)
    
    # Get cross-sell recommendations
    if include_recommendations:
        cross_sell = _get_customer_cross_sell(customer_id, customer.get('clv_tier', 'Bronze'))
        response["cross_sell"] = cross_sell
    
    # Get next best actions
    actions = [a for a in result.get('next_best_actions', []) if a['customer_id'] == customer_id]
    if actions:
        response["customer"]["recommendations"] = actions[0].get('recommendations', [])
    
    return response


def _get_customer_purchase_history(customer_id: str) -> List[Dict[str, Any]]:
    """Get detailed purchase history for a customer"""
    query = """
        SELECT 
            si.name as invoice_id,
            si.posting_date,
            si.due_date,
            si.grand_total,
            si.net_total,
            si.outstanding_amount,
            si.status,
            CASE 
                WHEN si.outstanding_amount = 0 THEN 'Paid'
                WHEN si.due_date < CURDATE() THEN 'Overdue'
                ELSE 'Outstanding'
            END as payment_status
        FROM `tabSales Invoice` si
        WHERE si.customer = %(customer_id)s
        AND si.docstatus = 1
        ORDER BY si.posting_date DESC
        LIMIT 50
    """
    try:
        results = frappe.db.sql(query, {"customer_id": customer_id}, as_dict=True)
        return results
    except Exception:
        return []


def _analyze_customer_purchase_patterns(purchase_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze purchase patterns from history"""
    if not purchase_history or len(purchase_history) < 2:
        return None
    
    try:
        import pandas as pd
        df = pd.DataFrame(purchase_history)
        df['posting_date'] = pd.to_datetime(df['posting_date'])
        
        # Calculate average frequency
        df_sorted = df.sort_values('posting_date')
        if len(df_sorted) >= 2:
            date_diffs = df_sorted['posting_date'].diff().dropna()
            avg_frequency = date_diffs.dt.days.mean()
        else:
            avg_frequency = None
        
        # Preferred day of week
        df['day_of_week'] = df['posting_date'].dt.day_name()
        preferred_day = df['day_of_week'].mode().iloc[0] if len(df) > 0 else None
        
        # Peak month
        df['month'] = df['posting_date'].dt.month_name()
        month_totals = df.groupby('month')['grand_total'].sum()
        peak_month = month_totals.idxmax() if len(month_totals) > 0 else None
        
        return {
            "avg_frequency": round(avg_frequency, 1) if avg_frequency else None,
            "preferred_day": preferred_day,
            "peak_month": peak_month,
            "total_purchases": len(df),
            "total_value": float(df['grand_total'].sum())
        }
    except Exception:
        return None


def _get_customer_cross_sell(customer_id: str, clv_tier: str) -> List[Dict[str, Any]]:
    """Get cross-sell recommendations for a customer"""
    try:
        from insights.ml.product_recommendations import ProductRecommendations
        
        model = ProductRecommendations()
        cached = model.get_cached_results("product_recommendations")
        
        if not cached:
            # Run recommendations if not cached
            cached = model.train()
        
        if cached.get('status') != 'success':
            return []
        
        # Get items this customer has purchased
        purchased_items = frappe.db.sql("""
            SELECT DISTINCT sii.item_code
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON sii.parent = si.name
            WHERE si.customer = %(customer_id)s AND si.docstatus = 1
        """, {"customer_id": customer_id}, as_dict=True)
        
        purchased_set = {item['item_code'] for item in purchased_items}
        
        if not purchased_set:
            return []
        
        # Get recommendations based on association rules
        recommendations = []
        rules_data = cached.get('association_rules', {})
        
        # Handle both dict and list formats
        if isinstance(rules_data, dict):
            rules = rules_data.get('top_rules', [])
        elif isinstance(rules_data, list):
            rules = rules_data
        else:
            rules = []
        
        # Ensure rules is a list
        if not isinstance(rules, list):
            rules = []
        
        for rule in rules[:50]:  # Check top 50 rules
            antecedent = set(rule.get('antecedent', []))
            consequent = rule.get('consequent', [])
            
            # If customer has bought antecedent items
            if antecedent.issubset(purchased_set):
                for item_code in consequent:
                    if item_code not in purchased_set:
                        # Get item details
                        item_info = frappe.db.get_value(
                            "Item", 
                            item_code, 
                            ["item_name", "item_group"], 
                            as_dict=True
                        )
                        if item_info:
                            recommendations.append({
                                "item_code": item_code,
                                "item_name": item_info.get('item_name', item_code),
                                "item_group": item_info.get('item_group', ''),
                                "confidence": rule.get('confidence', 0),
                                "lift": rule.get('lift', 0),
                                "reason": "Frequently bought together"
                            })
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec['item_code'] not in seen:
                seen.add(rec['item_code'])
                unique_recs.append(rec)
        
        # If no recommendations from rules, try frequently bought together
        if not unique_recs:
            fbt_pairs = cached.get('frequently_bought_together', [])
            for pair in fbt_pairs[:30]:
                item1, item2 = pair.get('item1'), pair.get('item2')
                # Recommend the item they haven't bought
                if item1 in purchased_set and item2 not in purchased_set:
                    if item2 not in seen:
                        seen.add(item2)
                        unique_recs.append({
                            "item_code": item2,
                            "item_name": pair.get('item2_name', item2),
                            "item_group": "",
                            "confidence": pair.get('support', 0) * 10,  # Convert support to confidence-like score
                            "lift": pair.get('lift', 0),
                            "reason": "Frequently bought together"
                        })
                elif item2 in purchased_set and item1 not in purchased_set:
                    if item1 not in seen:
                        seen.add(item1)
                        unique_recs.append({
                            "item_code": item1,
                            "item_name": pair.get('item1_name', item1),
                            "item_group": "",
                            "confidence": pair.get('support', 0) * 10,
                            "lift": pair.get('lift', 0),
                            "reason": "Frequently bought together"
                        })
        
        # If still no recommendations, suggest popular items from customer's item groups
        if not unique_recs:
            # Get item groups customer buys from
            customer_groups = frappe.db.sql("""
                SELECT DISTINCT i.item_group, COUNT(*) as cnt
                FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si ON sii.parent = si.name
                JOIN `tabItem` i ON sii.item_code = i.name
                WHERE si.customer = %(customer_id)s AND si.docstatus = 1
                GROUP BY i.item_group
                ORDER BY cnt DESC
                LIMIT 5
            """, {"customer_id": customer_id}, as_dict=True)
            
            if customer_groups:
                group_names = [g['item_group'] for g in customer_groups if g['item_group']]
                if group_names:
                    # Build placeholders for IN clause
                    placeholders = ', '.join(['%s'] * len(group_names))
                    
                    # Get popular items in those groups that customer hasn't bought
                    popular = frappe.db.sql(f"""
                        SELECT sii.item_code, i.item_name, i.item_group, 
                               COUNT(*) as popularity, SUM(sii.qty) as total_qty
                        FROM `tabSales Invoice Item` sii
                        JOIN `tabSales Invoice` si ON sii.parent = si.name
                        JOIN `tabItem` i ON sii.item_code = i.name
                        WHERE si.docstatus = 1 
                          AND i.item_group IN ({placeholders})
                          AND sii.item_code NOT IN (
                              SELECT DISTINCT sii2.item_code 
                              FROM `tabSales Invoice Item` sii2
                              JOIN `tabSales Invoice` si2 ON sii2.parent = si2.name
                              WHERE si2.customer = %s AND si2.docstatus = 1
                          )
                        GROUP BY sii.item_code
                        ORDER BY popularity DESC
                        LIMIT 10
                    """, tuple(group_names) + (customer_id,), as_dict=True)
                    
                    for item in popular:
                        if item['item_code'] not in seen:
                            seen.add(item['item_code'])
                            unique_recs.append({
                                "item_code": item['item_code'],
                                "item_name": item.get('item_name', item['item_code']),
                                "item_group": item.get('item_group', ''),
                                "confidence": min(item.get('popularity', 1) / 10, 0.9),  # Normalize popularity
                                "lift": 1.0,
                                "reason": f"Popular in {item.get('item_group', 'category')}"
                            })
        
        # Final fallback: recommend from popular item groups customer doesn't buy from
        if not unique_recs:
            # Get all item groups customer buys from
            all_customer_groups = frappe.db.sql("""
                SELECT DISTINCT i.item_group
                FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si ON sii.parent = si.name
                JOIN `tabItem` i ON sii.item_code = i.name
                WHERE si.customer = %(customer_id)s AND si.docstatus = 1
            """, {"customer_id": customer_id})
            customer_group_names = set(g[0] for g in all_customer_groups if g[0])
            
            # Get top selling item groups overall
            top_groups = frappe.db.sql("""
                SELECT i.item_group, COUNT(*) as cnt
                FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si ON sii.parent = si.name
                JOIN `tabItem` i ON sii.item_code = i.name
                WHERE si.docstatus = 1 AND i.item_group IS NOT NULL
                GROUP BY i.item_group
                ORDER BY cnt DESC
                LIMIT 20
            """, as_dict=True)
            
            # Find groups customer doesn't buy from
            new_groups = [g['item_group'] for g in top_groups if g['item_group'] not in customer_group_names][:5]
            
            if new_groups:
                placeholders = ', '.join(['%s'] * len(new_groups))
                new_group_items = frappe.db.sql(f"""
                    SELECT sii.item_code, i.item_name, i.item_group, 
                           COUNT(*) as popularity
                    FROM `tabSales Invoice Item` sii
                    JOIN `tabSales Invoice` si ON sii.parent = si.name
                    JOIN `tabItem` i ON sii.item_code = i.name
                    WHERE si.docstatus = 1 
                      AND i.item_group IN ({placeholders})
                    GROUP BY sii.item_code
                    ORDER BY popularity DESC
                    LIMIT 10
                """, tuple(new_groups), as_dict=True)
                
                for item in new_group_items:
                    if item['item_code'] not in seen:
                        seen.add(item['item_code'])
                        unique_recs.append({
                            "item_code": item['item_code'],
                            "item_name": item.get('item_name', item['item_code']),
                            "item_group": item.get('item_group', ''),
                            "confidence": min(item.get('popularity', 1) / 100, 0.7),
                            "lift": 1.0,
                            "reason": f"Explore {item.get('item_group', 'new category')}"
                        })
        
        unique_recs.sort(key=lambda x: x['confidence'], reverse=True)
        return unique_recs[:10]
        
    except Exception as e:
        frappe.log_error(f"Cross-sell error: {str(e)}", "Customer Intelligence")
        return []


@frappe.whitelist()
def get_purchase_patterns(top_percentile: int = 20) -> Dict[str, Any]:
    """
    Get purchase patterns for top customers by CLV
    Analyzes day-of-week, monthly, and seasonal patterns
    """
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    customers = result.get('customers', [])
    if not customers:
        return {"status": "error", "message": "No customer data available"}
    
    # Filter to top percentile by CLV
    customers_sorted = sorted(customers, key=lambda x: x.get('historical_clv', 0), reverse=True)
    top_count = max(1, int(len(customers_sorted) * top_percentile / 100))
    top_customers = customers_sorted[:top_count]
    top_customer_ids = [c['customer_id'] for c in top_customers]
    
    # Get transactions for top customers
    placeholders = ', '.join(['%s'] * len(top_customer_ids))
    query = f"""
        SELECT 
            si.customer,
            si.posting_date,
            si.grand_total,
            DAYNAME(si.posting_date) as day_name,
            DAYOFWEEK(si.posting_date) as day_of_week,
            MONTH(si.posting_date) as month_num,
            MONTHNAME(si.posting_date) as month_name,
            QUARTER(si.posting_date) as quarter,
            HOUR(si.creation) as hour_of_day
        FROM `tabSales Invoice` si
        WHERE si.customer IN ({placeholders})
        AND si.docstatus = 1
        AND si.posting_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        ORDER BY si.posting_date
    """
    
    try:
        transactions = frappe.db.sql(query, tuple(top_customer_ids), as_dict=True)
        
        if not transactions:
            return {"status": "success", "message": "No transaction data", "patterns": None}
        
        import pandas as pd
        df = pd.DataFrame(transactions)
        
        # Day of week analysis
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_analysis = df.groupby('day_name').agg({
            'grand_total': ['count', 'sum', 'mean']
        }).round(2)
        day_analysis.columns = ['order_count', 'total_revenue', 'avg_order_value']
        day_analysis = day_analysis.reindex(day_order).fillna(0)
        
        # Monthly analysis
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_analysis = df.groupby('month_name').agg({
            'grand_total': ['count', 'sum', 'mean']
        }).round(2)
        month_analysis.columns = ['order_count', 'total_revenue', 'avg_order_value']
        month_analysis = month_analysis.reindex(month_order).fillna(0)
        
        # Quarterly/Seasonal analysis
        quarter_analysis = df.groupby('quarter').agg({
            'grand_total': ['count', 'sum', 'mean']
        }).round(2)
        quarter_analysis.columns = ['order_count', 'total_revenue', 'avg_order_value']
        quarter_names = {1: 'Q1 (Jan-Mar)', 2: 'Q2 (Apr-Jun)', 3: 'Q3 (Jul-Sep)', 4: 'Q4 (Oct-Dec)'}
        
        # Peak analysis
        peak_day = day_analysis['order_count'].idxmax() if not day_analysis.empty else None
        peak_month = month_analysis['total_revenue'].idxmax() if not month_analysis.empty else None
        peak_quarter = quarter_analysis['total_revenue'].idxmax() if not quarter_analysis.empty else None
        
        return {
            "status": "success",
            "analysis_scope": {
                "top_percentile": top_percentile,
                "customer_count": len(top_customers),
                "transaction_count": len(transactions),
                "date_range": "Last 12 months"
            },
            "day_of_week": {
                "data": day_analysis.reset_index().to_dict('records'),
                "peak_day": peak_day,
                "heatmap": day_analysis['order_count'].to_dict()
            },
            "monthly": {
                "data": month_analysis.reset_index().to_dict('records'),
                "peak_month": peak_month,
                "trend": month_analysis['total_revenue'].to_dict()
            },
            "seasonal": {
                "data": [
                    {
                        "quarter": quarter_names.get(int(idx), f"Q{int(idx)}"),
                        **row.to_dict()
                    }
                    for idx, row in quarter_analysis.iterrows()
                ],
                "peak_quarter": quarter_names.get(peak_quarter, None)
            },
            "summary": {
                "total_orders": len(transactions),
                "total_revenue": float(df['grand_total'].sum()),
                "avg_order_value": float(df['grand_total'].mean()),
                "peak_day": peak_day,
                "peak_month": peak_month
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Purchase patterns error: {str(e)}", "Customer Intelligence")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_cross_sell_opportunities(tier_filter: str = "Diamond,Platinum") -> Dict[str, Any]:
    """
    Get cross-sell opportunities for customers in specified CLV tiers
    """
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    # Filter customers by tier
    tiers = [t.strip() for t in tier_filter.split(',')]
    customers = [c for c in result.get('customers', []) if c.get('clv_tier') in tiers]
    
    if not customers:
        return {"status": "success", "message": "No customers in specified tiers", "opportunities": []}
    
    # Get cross-sell for each customer
    opportunities = []
    for customer in customers[:50]:  # Limit to top 50
        cross_sell = _get_customer_cross_sell(customer['customer_id'], customer.get('clv_tier', 'Bronze'))
        if cross_sell:
            opportunities.append({
                "customer_id": customer['customer_id'],
                "customer_name": customer.get('customer_name', ''),
                "clv_tier": customer.get('clv_tier', ''),
                "historical_clv": customer.get('historical_clv', 0),
                "health_status": customer.get('health_status', ''),
                "recommendations": cross_sell[:5]  # Top 5 per customer
            })
    
    # Sort by CLV
    opportunities.sort(key=lambda x: x['historical_clv'], reverse=True)
    
    return {
        "status": "success",
        "tier_filter": tiers,
        "customer_count": len(opportunities),
        "opportunities": opportunities
    }



@frappe.whitelist()
def get_at_risk_customers() -> Dict[str, Any]:
    """Get customers at high churn risk"""
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    return {
        "status": "success",
        "at_risk_count": len(result.get('at_risk_customers', [])),
        "customers": result.get('at_risk_customers', [])
    }


@frappe.whitelist()
def get_geographic_insights() -> Dict[str, Any]:
    """Get geographic analysis"""
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    return {
        "status": "success",
        "geographic_analysis": result.get('geographic_analysis', {})
    }


@frappe.whitelist()
def get_next_actions() -> Dict[str, Any]:
    """Get next best action recommendations"""
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    return {
        "status": "success",
        "total_actions": len(result.get('next_best_actions', [])),
        "actions": result.get('next_best_actions', [])
    }


@frappe.whitelist()
def get_pareto_analysis() -> Dict[str, Any]:
    """Get 80/20 Pareto analysis"""
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    return {
        "status": "success",
        "pareto_analysis": result.get('pareto_analysis', {})
    }


@frappe.whitelist()
def get_cohort_analysis() -> Dict[str, Any]:
    """Get cohort retention analysis"""
    result = get_customer_intelligence()
    
    if result.get('status') != 'success':
        return result
    
    return {
        "status": "success",
        "cohort_analysis": result.get('cohort_analysis', {})
    }


@frappe.whitelist()
def refresh_customer_scores() -> Dict[str, Any]:
    """Force refresh and update all customer scores"""
    model = CustomerIntelligence()
    return model.train(update_customers=True)
