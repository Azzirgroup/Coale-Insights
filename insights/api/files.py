# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
File Upload API endpoints
Handles CSV/XLSX file previewing and importing into DuckDB.
"""

import frappe

from insights.decorators import insights_whitelist, validate_type
from insights.api.response import success, error
from insights.insights.doctype.insights_team.insights_team import check_data_source_permission

# Optional imports — gracefully degraded if not installed
try:
    import ibis
    IBIS_AVAILABLE = True
except ImportError:
    ibis = None
    IBIS_AVAILABLE = False

try:
    from insights.insights.doctype.insights_data_source_v3.connectors.duckdb import (
        get_duckdb_connection,
    )
    from insights.insights.doctype.insights_data_source_v3.ibis_utils import (
        get_columns_from_schema,
    )
    from insights.insights.doctype.insights_table_v3.insights_table_v3 import (
        InsightsTablev3,
    )
    V3_AVAILABLE = True
except ImportError:
    get_duckdb_connection = None
    get_columns_from_schema = None
    InsightsTablev3 = None
    V3_AVAILABLE = False


def get_csv_file(filename: str):
    """Return the File doc and detected extension for a given filename."""
    file = frappe.get_doc("File", filename)
    file_name = file.file_name or ""
    parts = file.get_extension()
    extension = parts[-1] if parts else ""
    extension = extension.lstrip(".")

    if not extension or extension not in ["csv", "xlsx"]:
        frappe.throw(
            f"Only CSV and XLSX files are supported. Detected extension: '{extension}' from filename: '{file_name}'"
        )
    return file, extension


@insights_whitelist()
@validate_type
def get_file_data(filename: str):
    check_data_source_permission("uploads")

    if not IBIS_AVAILABLE:
        return error("Ibis library is not available. Please install ibis to use file upload features.")

    file, ext = get_csv_file(filename)
    file_path = file.get_full_path()
    file_name = file.file_name.split(".")[0]
    file_name = frappe.scrub(file_name)

    con = ibis.duckdb.connect()
    if ext in ["xlsx"]:
        table = con.read_xlsx(file_path)
    else:
        table = con.read_csv(file_path, table_name=file_name)

    count = table.count().execute()
    columns = get_columns_from_schema(table.schema())
    rows = table.head(50).execute().fillna("").to_dict(orient="records")

    return success({
        "tablename": file_name,
        "rows": rows,
        "columns": columns,
        "total_rows": count,
    })


@insights_whitelist()
@validate_type
def import_csv_data(filename: str):
    check_data_source_permission("uploads")

    if not IBIS_AVAILABLE or not V3_AVAILABLE:
        return error(
            "Required libraries (ibis or v3 components) are not available. "
            "Please install the required dependencies."
        )

    file, ext = get_csv_file(filename)
    file_path = file.get_full_path()
    table_name = file.file_name.split(".")[0]
    table_name = frappe.scrub(table_name)

    if not frappe.db.exists("Insights Data Source v3", "uploads"):
        uploads = frappe.new_doc("Insights Data Source v3")
        uploads.name = "uploads"
        uploads.title = "Uploads"
        uploads.database_type = "DuckDB"
        uploads.database_name = "insights_file_uploads"
        uploads.owner = "Administrator"
        uploads.status = "Active"
        uploads.db_insert()

    ds = frappe.get_doc("Insights Data Source v3", "uploads")
    db = get_duckdb_connection(ds, read_only=False)

    try:
        if ext in ["xlsx"]:
            table = db.read_xlsx(file_path)
            db.create_table(table_name, table, overwrite=True)
        else:
            table = db.read_csv(file_path, table_name=table_name)
            db.create_table(table_name, table, overwrite=True)
    except Exception as e:
        frappe.log_error(e)
        if ext in ["xlsx"]:
            frappe.throw(
                "Failed to read Excel data from uploaded file. "
                "Please ensure the file is a valid Excel format and try again."
            )
        else:
            frappe.throw("Failed to read CSV data from uploaded file. Please try again.")
    finally:
        db.disconnect()

    InsightsTablev3.bulk_create(ds.name, [table_name])
