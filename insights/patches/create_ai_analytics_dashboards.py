# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to create pre-configured AI Analytics dashboards
"""

import frappe
import json
from frappe import _


def execute():
    """Create default AI Analytics dashboards"""
    
    # Check if dashboards already exist
    existing = frappe.get_all(
        "Insights Dashboard v3",
        filters={"title": ["like", "%Analytics%"]},
        pluck="name"
    )
    
    if existing:
        return
    
    # First create or get a workbook for AI Analytics
    workbook_name = get_or_create_workbook()
    
    dashboards = [
        {
            "title": "Financial Analytics",
            "type": "financial",
            "description": "Revenue, expenses, profit/loss, and cash flow analysis with AI insights",
        },
        {
            "title": "Sales Intelligence",
            "type": "sales",
            "description": "Sales performance, customer insights, and conversion analysis",
        },
        {
            "title": "Procurement Analytics",
            "type": "procurement",
            "description": "Supplier performance, spend analysis, and cost optimization",
        },
        {
            "title": "Inventory Insights",
            "type": "inventory",
            "description": "Stock levels, turnover analysis, and slow-moving inventory",
        },
        {
            "title": "Production Analytics",
            "type": "production",
            "description": "Manufacturing efficiency and work order analysis",
        },
        {
            "title": "Customer Intelligence",
            "type": "customer",
            "description": "Customer segmentation, retention, and lifetime value analysis",
        }
    ]
    
    for dashboard_config in dashboards:
        try:
            create_ai_dashboard(dashboard_config, workbook_name)
        except Exception as e:
            frappe.log_error(f"Error creating {dashboard_config['title']}: {str(e)}", "AI Dashboard Creation")
    
    frappe.db.commit()


def get_or_create_workbook():
    """Get existing or create new workbook for AI Analytics"""
    existing = frappe.get_all(
        "Insights Workbook",
        filters={"title": "AI Analytics Workbook"},
        pluck="name"
    )
    
    if existing:
        return existing[0]
    
    workbook = frappe.new_doc("Insights Workbook")
    workbook.title = "AI Analytics Workbook"
    workbook.insert(ignore_permissions=True)
    return workbook.name


def create_ai_dashboard(config, workbook_name):
    """Create a single AI analytics dashboard"""
    
    doc = frappe.new_doc("Insights Dashboard v3")
    doc.title = config["title"]
    doc.is_public = 1
    doc.workbook = workbook_name
    doc.items = json.dumps([])
    doc.insert(ignore_permissions=True)
