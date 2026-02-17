# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class InsightsAIQuery(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        query: DF.SmallText
        user: DF.Link
        complexity: DF.Literal["", "simple", "medium", "complex"]
        model_used: DF.Data | None
        response: DF.LongText | None
        processing_time: DF.Float | None
        cached: DF.Check
        conversation: DF.Link | None
        tokens_used: DF.Int | None
        source_module: DF.Data | None
    # end: auto-generated types

    def before_insert(self):
        if not self.user:
            self.user = frappe.session.user

    @staticmethod
    def log_query(
        query: str,
        response: str = None,
        model_used: str = None,
        complexity: str = None,
        processing_time: float = None,
        cached: bool = False,
        conversation: str = None,
        tokens_used: int = None,
        source_module: str = None,
    ):
        """Log an AI query for audit and recent insights display"""
        try:
            doc = frappe.get_doc({
                "doctype": "Insights AI Query",
                "query": (query or "")[:2000],
                "user": frappe.session.user,
                "response": (response or "")[:60000],
                "model_used": model_used,
                "complexity": complexity,
                "processing_time": processing_time,
                "cached": 1 if cached else 0,
                "conversation": conversation,
                "tokens_used": tokens_used,
                "source_module": source_module,
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return doc.name
        except Exception as e:
            frappe.log_error(title="AI Query Log Error", message=str(e)[:1000])
            return None

    @staticmethod
    def get_recent_queries(user: str = None, limit: int = 10):
        """Get recent AI queries for a user"""
        if not user:
            user = frappe.session.user

        queries = frappe.get_all(
            "Insights AI Query",
            filters={"user": user},
            fields=["name", "query", "model_used", "complexity", "processing_time", "cached", "creation", "source_module"],
            order_by="creation desc",
            limit=limit,
        )
        return queries
