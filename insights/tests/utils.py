# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import json

import frappe
from frappe.utils.install import complete_setup_wizard


def before_tests():
    complete_setup_wizard()
    frappe.db.commit()


def delete_all_records():
    frappe.db.delete("Version", {"ref_doctype": ("like", "Insights%")})
    frappe.db.delete("View Log", {"reference_doctype": ("like", "Insights%")})
    for doctype in frappe.get_all("DocType", filters={"module": "Insights", "issingle": 0}, pluck="name"):
        frappe.db.delete(doctype)


def create_site_db():
    data_source_fixture_path = frappe.get_app_path("insights", "fixtures", "insights_data_source_v3.json")
    with open(data_source_fixture_path) as f:
        site_db = json.load(f)[0]
        frappe.get_doc(site_db).insert()
