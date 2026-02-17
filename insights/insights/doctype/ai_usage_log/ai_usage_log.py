# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class AIUsageLog(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        model: DF.Data
        user: DF.Link | None
        query_hash: DF.Data | None
        complexity: DF.Literal["", "simple", "medium", "complex"]
        tokens_used: DF.Int | None
        processing_time: DF.Float | None
        timestamp: DF.Datetime | None
    # end: auto-generated types

    def before_insert(self):
        if not self.user:
            self.user = frappe.session.user
        if not self.timestamp:
            self.timestamp = now_datetime()
