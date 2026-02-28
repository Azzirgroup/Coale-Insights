# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from insights.analytics.collectors.base import BaseCollector  # noqa: F401
from insights.analytics.collectors.financial import FinancialDataCollector  # noqa: F401
from insights.analytics.collectors.sales import SalesDataCollector  # noqa: F401
from insights.analytics.collectors.customer import CustomerDataCollector  # noqa: F401
from insights.analytics.collectors.inventory import InventoryDataCollector  # noqa: F401
from insights.analytics.collectors.procurement import ProcurementDataCollector  # noqa: F401
from insights.analytics.collectors.production import ProductionDataCollector  # noqa: F401
from insights.analytics.collectors.hr import HRDataCollector  # noqa: F401
from insights.analytics.collectors.api import (  # noqa: F401
    get_collector,
    get_analytics_data,
    get_all_analytics_data,
)
