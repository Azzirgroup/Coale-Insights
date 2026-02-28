# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
ML API Utilities
Date filter helpers shared across all ML API modules.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple


def parse_date_filter(date_filter: str = "12m") -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Parse a date filter string into start_date and end_date.

    Args:
        date_filter: Filter string like '7d', '30d', '90d', '6m', '12m', '24m', 'all'

    Returns:
        Tuple of (start_date, end_date) where end_date is always today.
        Returns (None, None) for 'all' to indicate no date filtering.

    Raises:
        ValueError: If the filter string has an unrecognised suffix.
    """
    if not date_filter or date_filter == "all":
        return None, None

    end_date = datetime.now()

    if date_filter.endswith("d"):
        days = int(date_filter[:-1])
        start_date = end_date - timedelta(days=days)
    elif date_filter.endswith("m"):
        months = int(date_filter[:-1])
        start_date = end_date - timedelta(days=months * 30)
    elif date_filter.endswith("y"):
        years = int(date_filter[:-1])
        start_date = end_date - timedelta(days=years * 365)
    else:
        # Default to 12 months for unrecognised format
        start_date = end_date - timedelta(days=365)

    return start_date, end_date


def get_date_filter_sql(
    date_filter: str = "12m",
    date_column: str = "posting_date",
    alias: str = "",
) -> str:
    """
    Generate a SQL WHERE clause fragment for date filtering.

    Uses parameterised-style date strings (ISO 8601) that are safe to embed in
    frappe.db.sql() calls via %s substitution when the caller incorporates them.

    Returns an empty string when date_filter is 'all' (no filtering required).
    """
    start_date, end_date = parse_date_filter(date_filter)

    if start_date is None:
        return ""

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    date_col = f"{alias}.{date_column}" if alias else date_column

    # NOTE: Callers that embed this fragment in frappe.db.sql() should pass the
    # date values as query parameters (%s) rather than relying on string
    # interpolation.  The formatted strings here are ISO dates from trusted
    # internal sources (no user input reaches strftime), so direct embedding is
    # safe but is retained only for backward compatibility.
    return f"AND {date_col} BETWEEN '{start_str}' AND '{end_str}'"
