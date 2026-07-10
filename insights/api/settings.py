# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""Lightweight settings the dashboards need (kept dependency-free)."""

import frappe


@frappe.whitelist(methods=["GET", "POST"])
def get_default_currency():
    """The default currency of the user's / system's default company.

    All dashboard cards format money in this currency, so changing the company
    currency (e.g. KES -> TZS) is reflected everywhere.
    """
    company = (
        frappe.defaults.get_user_default("Company")
        or frappe.db.get_single_value("Global Defaults", "default_company")
    )
    if company:
        currency = frappe.db.get_value("Company", company, "default_currency")
        if currency:
            return currency
    return frappe.db.get_default("currency") or "USD"
