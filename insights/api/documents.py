# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Document method proxy API
Allows public (guest-accessible) doc reads and method execution.
"""

import frappe
from frappe.handler import is_valid_http_method, is_whitelisted
from frappe.monitor import add_data_to_monitor

from insights.api.shared import is_public
from insights.decorators import validate_type


# Methods that guests are allowed to call on specific DocTypes
_PUBLIC_METHODS: dict[str, list[str]] = {
    "Insights Query v3": ["execute", "download_results"],
    "Insights Dashboard v3": ["get_distinct_column_values"],
}


def is_public_method(doctype: str, method: str) -> bool:
    """Return True if the method is in the allow-list for the given DocType."""
    return method in _PUBLIC_METHODS.get(doctype, [])


def _execute_doc_method(doc, method: str, args: dict | None = None, ignore_permissions=False):
    args = frappe.parse_json(args)
    method_obj = getattr(doc, method)
    fn = getattr(method_obj, "__func__", method_obj)

    if not ignore_permissions:
        doc.check_permission("read")
        is_whitelisted(fn)
        is_valid_http_method(fn)

    new_kwargs = frappe.get_newargs(fn, args)
    response = doc.run_method(method, **new_kwargs)
    frappe.response.docs.append(doc)
    frappe.response["message"] = response
    add_data_to_monitor(methodname=method)
    return response


@frappe.whitelist(allow_guest=True)
@validate_type
def get_doc(doctype: str, name: str | int):
    """
    Fetch a document. Requires standard read permission.
    Falls back to allow access for public (shared) documents.

    Security note: access is gated by either frappe.has_permission (via the
    standard frappe.client.get call) or the is_public() check.  Do NOT remove
    the is_public guard below.
    """
    try:
        from frappe.client import get as _get_doc

        return _get_doc(doctype, name)
    except frappe.PermissionError:
        if not is_public(doctype, name):
            raise
        return frappe.get_doc(doctype, name).as_dict()


@frappe.whitelist(allow_guest=True)
def run_doc_method(method: str, docs: dict | str, args: dict | None = None):
    """
    Execute a document method.
    For guest callers the method must be in the public-methods allow-list.

    Security note: The allow-list (_PUBLIC_METHODS) is the sole gate for
    unauthenticated execution.  Keep that list minimal.
    """
    doc = frappe.parse_json(docs)
    doctype = doc.get("doctype")
    name = doc.get("name")

    if not doctype or not name:
        raise frappe.ValidationError("Invalid document")

    try:
        docs = frappe.parse_json(docs)
        doc = frappe.get_doc(docs)
        return _execute_doc_method(doc, method, args)

    except frappe.PermissionError:
        if not is_public(doctype, name):
            raise frappe.PermissionError("You don't have permission to access this document")
        if not is_public_method(doctype, method):
            raise frappe.PermissionError("You don't have permission to access this method")

        doc = frappe.get_doc(doctype, name)
        return _execute_doc_method(doc, method, args, ignore_permissions=True)
