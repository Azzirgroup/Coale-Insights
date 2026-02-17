import frappe

from insights.decorators import insights_whitelist, validate_type


# v3 API


@insights_whitelist()
def get_dashboards(search_term=None, limit=50):
    dashboards = frappe.get_list(
        "Insights Dashboard v3",
        or_filters={
            "name": ["like", f"%{search_term}%" if search_term else "%"],
            "title": ["like", f"%{search_term}%" if search_term else "%"],
        },
        fields=[
            "name",
            "title",
            "workbook",
            "creation",
            "modified",
            "preview_image",
            "items",
        ],
        order_by="creation desc",
        limit=limit,
    )

    if not dashboards:
        return dashboards

    dashboard_names = [d.name for d in dashboards]

    # Batch fetch view counts — single SQL instead of N queries
    view_counts = {}
    if dashboard_names:
        view_count_rows = frappe.db.sql("""
            SELECT reference_name, COUNT(*) as cnt
            FROM `tabView Log`
            WHERE reference_doctype = 'Insights Dashboard v3'
            AND reference_name IN ({placeholders})
            GROUP BY reference_name
        """.format(placeholders=", ".join(["%s"] * len(dashboard_names))),
            tuple(dashboard_names), as_dict=True
        )
        for row in view_count_rows:
            view_counts[row.reference_name] = row.cnt

    for dashboard in dashboards:
        items = frappe.parse_json(dashboard["items"])
        charts = [item for item in items if item["type"] == "chart"]
        dashboard["charts"] = len(charts)
        dashboard["views"] = view_counts.get(dashboard.name, 0)
        del dashboard["items"]

    return dashboards


@insights_whitelist()
@validate_type
def update_dashboard_preview(dashboard_name: str):
    dashboard = frappe.get_doc("Insights Dashboard v3", dashboard_name)
    file_url = dashboard.generate_dashboard_preview()
    if not file_url:
        frappe.msgprint("Preview generation is not configured. Dashboards will work without previews.", indicator="orange")
    return file_url
