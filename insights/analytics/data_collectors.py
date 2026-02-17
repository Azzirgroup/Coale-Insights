# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Backward-compatibility shim.

The data collector classes have been moved to the ``insights.analytics.collectors``
package.  This module re-exports every public name so that existing import
paths continue to work unchanged:

    from insights.analytics.data_collectors import FinancialDataCollector
    from insights.analytics.data_collectors import get_collector
"""

from insights.analytics.collectors import (  # noqa: F401
    BaseCollector,
    FinancialDataCollector,
    SalesDataCollector,
    ProcurementDataCollector,
    InventoryDataCollector,
    ProductionDataCollector,
    CustomerDataCollector,
    HRDataCollector,
    get_collector,
    get_analytics_data,
    get_all_analytics_data,
)
