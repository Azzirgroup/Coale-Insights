# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Override for frappe.desk.doctype.dashboard_chart.dashboard_chart.get

Adds support for Custom chart type delegation to Dashboard Chart Source,
which is missing from stock Frappe. For all other chart types (Count, Sum,
Average, Group By, Report) the call is forwarded to the original Frappe
implementation unchanged.
"""

import frappe
from frappe import _
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
	refresh=None,
):
	# Resolve chart doc
	if chart_name:
		chart_doc = frappe.get_doc("Dashboard Chart", chart_name)
	else:
		chart_doc = frappe._dict(frappe.parse_json(chart))

	# Custom chart type — delegate to the registered Dashboard Chart Source
	if chart_doc.chart_type == "Custom":
		if chart_doc.source:
			return _get_custom_chart_data(
				chart_doc,
				no_cache=no_cache,
				filters=filters,
				from_date=from_date,
				to_date=to_date,
				timespan=timespan,
				time_interval=time_interval,
				heatmap_year=heatmap_year,
			)
		else:
			frappe.throw(
				_("Custom chart {0} has no source configured").format(chart_doc.name)
			)

	# All other chart types — delegate to the original Frappe implementation
	from frappe.desk.doctype.dashboard_chart.dashboard_chart import (
		get as _original_get,
	)

	return _original_get(
		chart_name=chart_name,
		chart=chart,
		no_cache=no_cache,
		filters=filters,
		from_date=from_date,
		to_date=to_date,
		timespan=timespan,
		time_interval=time_interval,
		heatmap_year=heatmap_year,
		refresh=refresh,
	)


def _get_custom_chart_data(
	chart_doc,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	"""Resolve the Dashboard Chart Source and call its get_data() method."""
	from frappe.modules import scrub as scrub_name

	source_doc = frappe.get_doc("Dashboard Chart Source", chart_doc.source)
	app_name = frappe.db.get_value("Module Def", source_doc.module, "app_name")
	scrubbed_module = scrub_name(source_doc.module)
	scrubbed_source = scrub_name(source_doc.name)

	method_path = (
		f"{app_name}.{scrubbed_module}.dashboard_chart_source"
		f".{scrubbed_source}.{scrubbed_source}.get_data"
	)
	method = frappe.get_attr(method_path)

	# Parse filters the same way the original get() does
	parsed_filters = frappe.parse_json(filters) or frappe.parse_json(
		chart_doc.get("filters_json")
	)
	if not parsed_filters:
		parsed_filters = []

	return method(
		chart_name=chart_doc.name,
		chart=chart_doc,
		no_cache=no_cache,
		filters=parsed_filters,
		from_date=from_date,
		to_date=to_date,
		timespan=timespan,
		time_interval=time_interval,
		heatmap_year=heatmap_year,
	)
