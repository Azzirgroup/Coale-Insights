# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Customer Intelligence - Predict
Get cached or fresh predictions for customer intelligence.
"""

from typing import Dict, Any


def predict(intelligence, customer: str = None) -> Dict[str, Any]:
    """Get cached or fresh predictions"""
    cached = intelligence.get_cached_results("customer_intelligence")
    if not cached:
        cached = intelligence.train()

    if customer:
        customers = cached.get('customers', [])
        cust_data = next((c for c in customers if c['customer_id'] == customer), None)
        if cust_data:
            actions = [a for a in cached.get('next_best_actions', []) if a['customer_id'] == customer]
            return {"status": "success", "customer": cust_data, "actions": actions[0] if actions else None}
        return {"status": "error", "message": "Customer not found"}

    return cached
