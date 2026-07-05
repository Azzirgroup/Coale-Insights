# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Background runner for heavy ML dashboard endpoints.

The intelligence dashboards aggregate across the whole ERPNext dataset. Running
that synchronously inside a web request is slow and memory-heavy, and on a
resource-limited host (e.g. Frappe Cloud) the gunicorn worker gets killed by the
request timeout / OOM, which the proxy surfaces as a 502 Bad Gateway.

This module runs the computation in a background job instead:
  - if a fresh cached result exists, return it immediately;
  - otherwise enqueue the job (once) and return {status: "queued"};
  - the page polls a *_status endpoint until the result is ready.

Everything is cached in Redis (frappe.cache), which the web and worker
processes share.
"""

import frappe
from insights.api.response import success

RESULT_PREFIX = "insights_ml_result::"
STATUS_PREFIX = "insights_ml_status::"
STARTED_PREFIX = "insights_ml_started::"  # cache_key -> enqueue timestamp
POINTER_PREFIX = "insights_ml_pointer::"  # per user+endpoint -> active cache_key

DEFAULT_TTL_HOURS = 6
JOB_TIMEOUT = 1500  # seconds; runs on the "long" queue
# If a job is still "processing" after this long, assume the worker died / is
# unavailable (OOM, no worker for the queue, etc.) and report a failure so the
# UI stops spinning instead of polling forever.
STALL_SECONDS = 180


def _company():
    return (
        frappe.defaults.get_user_default("Company")
        or frappe.db.get_single_value("Global Defaults", "default_company")
        or "default"
    )


def _cache_key(endpoint: str, **params) -> str:
    parts = [endpoint, _company()]
    for key in sorted(params):
        parts.append(f"{key}={params[key]}")
    return "::".join(str(p) for p in parts)


def get_or_enqueue(endpoint: str, kind: str, kwargs: dict = None, refresh: bool = False):
    """Return cached result, or enqueue a background job and return a queued status."""
    kwargs = kwargs or {}
    cache_key = _cache_key(endpoint, **kwargs)
    result_key = RESULT_PREFIX + cache_key
    status_key = STATUS_PREFIX + cache_key

    # remember the active key for this user+endpoint so the status endpoint
    # (which is called without params) can find it.
    frappe.cache.set_value(
        POINTER_PREFIX + f"{frappe.session.user}::{endpoint}",
        cache_key,
        expires_in_sec=DEFAULT_TTL_HOURS * 3600,
    )

    if not refresh:
        cached = frappe.cache.get_value(result_key)
        if cached is not None:
            return success(cached)

        # A job is already running for this key; don't enqueue a duplicate.
        # (On refresh we fall through and force a fresh job, so a stuck/abandoned
        # "processing" flag can always be cleared by the user hitting Refresh.)
        if frappe.cache.get_value(status_key) == "processing":
            return {"status": "queued", "message": "Analysis is being processed"}

    frappe.cache.set_value(status_key, "processing", expires_in_sec=JOB_TIMEOUT)
    frappe.cache.set_value(
        STARTED_PREFIX + cache_key,
        frappe.utils.now_datetime().isoformat(),
        expires_in_sec=JOB_TIMEOUT,
    )
    frappe.enqueue(
        "insights.api.ml.async_runner.run_job",
        queue="long",
        timeout=JOB_TIMEOUT,
        cache_key=cache_key,
        kind=kind,
        kwargs=kwargs,
    )
    return {"status": "queued", "message": "Analysis started"}


def run_job(cache_key: str, kind: str, kwargs: dict):
    """Executed in a background worker: compute, then cache the result."""
    result_key = RESULT_PREFIX + cache_key
    status_key = STATUS_PREFIX + cache_key
    error_key = result_key + "::error"
    try:
        data = _compute(kind, kwargs or {})
        frappe.cache.set_value(result_key, data, expires_in_sec=DEFAULT_TTL_HOURS * 3600)
        frappe.cache.set_value(status_key, "completed", expires_in_sec=DEFAULT_TTL_HOURS * 3600)
        frappe.cache.delete_value(error_key)
    except Exception:
        tb = frappe.get_traceback()
        frappe.cache.set_value(status_key, "failed", expires_in_sec=600)
        frappe.cache.set_value(error_key, tb, expires_in_sec=600)
        frappe.log_error("Insights ML background job failed", tb)


def _compute(kind: str, kwargs: dict):
    if kind == "customer_intelligence":
        from insights.ml.customer_intelligence import CustomerIntelligence

        return CustomerIntelligence().predict()

    if kind == "sales_intelligence":
        from insights.ml.sales_intelligence import SalesIntelligence

        return SalesIntelligence(date_filter=kwargs.get("date_filter", "12m")).train()

    if kind == "executive_summary":
        from insights.ml.executive_intelligence import ExecutiveIntelligence

        return ExecutiveIntelligence().get_executive_summary(kwargs.get("period", "YTD"))

    raise ValueError(f"Unknown async ML kind: {kind}")


def job_status(endpoint: str):
    """Return the status/result of the current user's active job for an endpoint."""
    cache_key = frappe.cache.get_value(
        POINTER_PREFIX + f"{frappe.session.user}::{endpoint}"
    )
    if not cache_key:
        return {"status": "not_found"}

    result = frappe.cache.get_value(RESULT_PREFIX + cache_key)
    if result is not None:
        return {"status": "completed", "result": result}

    status = frappe.cache.get_value(STATUS_PREFIX + cache_key)
    if status == "failed":
        _clear(cache_key)  # let the next call re-enqueue a fresh job
        return {
            "status": "failed",
            "message": "Analysis failed. Please try again.",
        }
    if status == "processing":
        # If it has been "processing" too long, the worker likely died (OOM) or
        # no worker is servicing the queue. Report a failure so the UI can react,
        # and clear the flags so a retry starts a fresh job.
        started = frappe.cache.get_value(STARTED_PREFIX + cache_key)
        if started:
            try:
                elapsed = frappe.utils.time_diff_in_seconds(
                    frappe.utils.now_datetime(), started
                )
                if elapsed > STALL_SECONDS:
                    _clear(cache_key)
                    return {
                        "status": "failed",
                        "message": (
                            "The analysis did not finish in time. The background "
                            "worker may be unavailable or ran out of memory. "
                            "Please try again."
                        ),
                    }
            except Exception:
                pass
        return {"status": "processing"}
    return {"status": "not_found"}


def _clear(cache_key: str):
    """Drop the status/started flags so the next request enqueues a fresh job."""
    frappe.cache.delete_value(STATUS_PREFIX + cache_key)
    frappe.cache.delete_value(STARTED_PREFIX + cache_key)
