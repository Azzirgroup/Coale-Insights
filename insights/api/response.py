import frappe
from datetime import datetime


# ---------------------------------------------------------------------------
# numpy-safe JSON serialization
#
# The ML dashboards compute values with numpy/pandas, which produce numpy
# scalar types (numpy.float64, numpy.int64, numpy.bool_) and numpy arrays.
# frappe's JSON encoder does not know these types and raises
#   "Type is not JSON serializable: numpy.float64"
# The resulting 500 is served as a Werkzeug HTML page (non-JSON), which in turn
# crashes the SPA with "Cannot read properties of undefined (reading 'exc_type')".
#
# We extend frappe's json_handler once, additively: numpy types are converted to
# native Python, everything else falls through to the original handler. This is
# safe (it only handles types that previously errored) and covers every insights
# API response, since this module is imported by all insights.api.ml endpoints.
# ---------------------------------------------------------------------------
def _install_numpy_json_handler():
    from frappe.utils import response as _response

    if getattr(_response.json_handler, "_insights_numpy_patched", False):
        return

    _original_handler = _response.json_handler

    def json_handler(obj):
        if type(obj).__module__ == "numpy":
            import numpy as np

            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                value = float(obj)
                # nan / inf are not valid JSON numbers
                if value != value or value in (float("inf"), float("-inf")):
                    return None
                return value
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        return _original_handler(obj)

    json_handler._insights_numpy_patched = True
    _response.json_handler = json_handler


_install_numpy_json_handler()


def success(data=None, message=None):
    result = {"status": "success"}
    if data is not None:
        result["data"] = data
    if message:
        result["message"] = message
    return result


def error(message, exc=None):
    if exc:
        frappe.log_error(str(exc), "Insights API Error")
    return {
        "status": "error",
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
