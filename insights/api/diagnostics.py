# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Lightweight environment diagnostics for the Insights dashboards.

This module intentionally imports nothing heavy (no pandas / ibis / ml) so it
still works even when the ML stack is broken. Hit it to find out why the
dashboards won't load:

    /api/method/insights.api.diagnostics.env_check

or from the browser console on the Insights site:

    frappe.call('insights.api.diagnostics.env_check').then(r => console.log(r.message))
"""

import sys
import platform
import subprocess

import frappe


@frappe.whitelist(methods=["GET", "POST"])
def env_check():
    info = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }

    for mod in ("pandas", "numpy", "ibis", "sklearn", "posthog"):
        try:
            m = __import__(mod)
            info[mod] = getattr(m, "__version__", "installed")
        except Exception as e:  # noqa: BLE001
            info[mod] = f"MISSING/ERROR: {str(e)[:120]}"

    # The dashboards crash if pandas' datetime code is unstable on this Python
    # (it segfaults on some bleeding-edge Python builds). Run the check in a
    # SUBPROCESS so a hard crash can't take down this web worker — we just read
    # the exit code (a negative return code means the process was killed by a
    # signal, i.e. a segfault).
    try:
        code = (
            "import pandas as pd; "
            "pd.to_datetime(pd.Series(['2026-01-01', '2026-02-15'])); "
            "df = pd.DataFrame([{'d': __import__('datetime').date(2026,1,1), 'n': 1}]); "
            "print('OK', df.shape)"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            timeout=60,
        )
        info["pandas_datetime_returncode"] = proc.returncode
        info["pandas_datetime_ok"] = proc.returncode == 0
        if proc.returncode != 0:
            info["pandas_datetime_stderr"] = (
                proc.stderr.decode(errors="replace")[-500:] if proc.stderr else ""
            )
            info["diagnosis"] = (
                "pandas datetime CRASHES on this Python build. The background "
                "worker dies silently while computing a dashboard, so the page "
                "never gets a result. Fix: run this bench on Python 3.11/3.12, "
                "or install a pandas build compatible with this Python."
            )
        else:
            info["diagnosis"] = (
                "pandas is healthy here. If dashboards still hang, the "
                "background worker is likely out of memory or not running for "
                "the 'long' queue — check the site's Background Jobs / Error Log."
            )
    except subprocess.TimeoutExpired:
        info["pandas_datetime_ok"] = False
        info["diagnosis"] = "pandas datetime check timed out (very slow CPU/instance)."
    except Exception as e:  # noqa: BLE001
        info["pandas_datetime_check_error"] = str(e)[:200]

    # Is a worker actually servicing the queues?
    try:
        from frappe.utils.background_jobs import get_workers

        info["active_workers"] = len(get_workers())
    except Exception as e:  # noqa: BLE001
        info["active_workers"] = f"unknown: {str(e)[:100]}"

    return info
