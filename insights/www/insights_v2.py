# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# GNU GPLv3 License. See license.txt


import frappe

from insights.api.telemetry import track_active_site

no_cache = 1


def get_context(context):
    # Removed v3 redirect check - always serve v2 with AI Insights
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    context.csrf_token = csrf_token
    context.site_name = frappe.local.site
    context.socketio_port = frappe.conf.get("socketio_port", 9000)
    
    # Pass socketio_port to frontend via boot
    context.boot = {
        "socketio_port": frappe.conf.get("socketio_port", 9000)
    }
    track_active_site()
