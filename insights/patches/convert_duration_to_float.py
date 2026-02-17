import frappe


def execute():
    try:
        if not frappe.db.a_row_exists("Insights Query"):
            return
        Query = frappe.qb.DocType("Insights Query")
        frappe.qb.update(Query).set(Query.execution_time, 0).run()
    except Exception:
        # V2 DocType may have been removed
        pass
