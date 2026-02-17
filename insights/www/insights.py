# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# GNU GPLv3 License. See license.txt


import frappe
from insights.api.telemetry import track_active_site

no_cache = 1


def get_context(context):
    """Single unified Insights app with AI Analytics"""
    setup_complete = check_setup_complete()
    if not setup_complete:
        frappe.local.flags.redirect_location = "/app/setup-wizard"
        raise frappe.Redirect
    
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    context.csrf_token = csrf_token
    context.site_name = frappe.local.site
    context.boot = {
        "csrf_token": csrf_token,
        "site_name": frappe.local.site,
        "socketio_port": frappe.conf.get("socketio_port", 9001),
    }
    track_active_site()


def get_user_permissions():
    """Get user permissions for insights access"""
    
    permissions = {
        "can_view_dashboards": has_permission("Insights Dashboard v3", "read"),
        "can_create_dashboards": has_permission("Insights Dashboard v3", "create"),
        "can_view_reports": has_permission("Insights Report", "read"),
        "can_create_reports": has_permission("Insights Report", "create"),
        "can_use_ai": has_permission("AI Query", "create"),
        "can_export": has_permission("Insights Export", "create"),
        "can_admin": "System Manager" in frappe.get_roles()
    }
    
    return permissions


def has_permission(doctype, ptype):
    """Check if user has specific permission"""
    try:
        return frappe.has_permission(doctype, ptype)
    except:
        return False


def check_setup_complete():
    try:
        return frappe.is_setup_complete()
    except AttributeError:
        return frappe.db.get_single_value("System Settings", "setup_complete")
