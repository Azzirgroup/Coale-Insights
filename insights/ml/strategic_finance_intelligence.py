# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Backward-compatibility shim.

This module has been refactored into the `strategic_finance` package.
All imports are re-exported here so existing code continues to work:

    from insights.ml.strategic_finance_intelligence import StrategicFinanceIntelligence
    from insights.ml.strategic_finance_intelligence import run_strategic_finance_intelligence
    from insights.ml.strategic_finance_intelligence import sanitize_for_json
"""

from insights.ml.strategic_finance import (  # noqa: F401
    StrategicFinanceIntelligence,
    run_strategic_finance_intelligence,
    sanitize_for_json,
)
