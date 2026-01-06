# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Data Collectors for ERPNext Modules
Aggregates data from various ERPNext modules for AI analysis
"""

import frappe
from frappe import _
from frappe.utils import (
    nowdate, add_days, add_months, getdate, flt, cint,
    get_first_day, get_last_day, date_diff
)
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class BaseCollector:
    """Base class for data collectors"""
    
    def __init__(self, filters: Optional[Dict] = None):
        self.filters = filters or {}
        self.company = filters.get("company") if filters else frappe.defaults.get_user_default("Company")
        self.from_date = filters.get("from_date") if filters else add_months(nowdate(), -12)
        self.to_date = filters.get("to_date") if filters else nowdate()
    
    def collect(self) -> Dict[str, Any]:
        """Override in subclass"""
        raise NotImplementedError


class FinancialDataCollector(BaseCollector):
    """Collect financial data from Accounts module"""
    
    def collect(self) -> Dict[str, Any]:
        return {
            "revenue": self._get_revenue(),
            "expenses": self._get_expenses(),
            "profit_loss": self._get_profit_loss(),
            "cash_flow": self._get_cash_flow(),
            "receivables": self._get_receivables(),
            "payables": self._get_payables(),
            "bank_balance": self._get_bank_balance(),
            "monthly_trend": self._get_monthly_trend()
        }
    
    def _get_revenue(self) -> Dict[str, Any]:
        """Get revenue summary"""
        result = frappe.db.sql("""
            SELECT 
                SUM(debit - credit) as total_revenue
            FROM `tabGL Entry`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND account IN (
                SELECT name FROM `tabAccount` 
                WHERE root_type = 'Income' AND company = %s
            )
            AND is_cancelled = 0
        """, (self.from_date, self.to_date, self.company, self.company), as_dict=True)
        
        total = abs(flt(result[0].get("total_revenue"))) if result else 0
        
        # Get previous period for comparison
        prev_from = add_months(self.from_date, -12)
        prev_to = add_months(self.to_date, -12)
        
        prev_result = frappe.db.sql("""
            SELECT SUM(debit - credit) as total_revenue
            FROM `tabGL Entry`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND account IN (
                SELECT name FROM `tabAccount` 
                WHERE root_type = 'Income' AND company = %s
            )
            AND is_cancelled = 0
        """, (prev_from, prev_to, self.company, self.company), as_dict=True)
        
        prev_total = abs(flt(prev_result[0].get("total_revenue"))) if prev_result else 0
        growth = ((total - prev_total) / prev_total * 100) if prev_total else 0
        
        return {
            "total": total,
            "previous_period": prev_total,
            "growth_percent": round(growth, 2)
        }
    
    def _get_expenses(self) -> Dict[str, Any]:
        """Get expense summary"""
        result = frappe.db.sql("""
            SELECT 
                SUM(debit - credit) as total_expense
            FROM `tabGL Entry`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND account IN (
                SELECT name FROM `tabAccount` 
                WHERE root_type = 'Expense' AND company = %s
            )
            AND is_cancelled = 0
        """, (self.from_date, self.to_date, self.company, self.company), as_dict=True)
        
        total = flt(result[0].get("total_expense")) if result else 0
        
        # Top expense categories
        top_expenses = frappe.db.sql("""
            SELECT 
                parent_account as category,
                SUM(debit - credit) as amount
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.posting_date BETWEEN %s AND %s
            AND gle.company = %s
            AND acc.root_type = 'Expense'
            AND gle.is_cancelled = 0
            GROUP BY parent_account
            ORDER BY amount DESC
            LIMIT 10
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        return {
            "total": total,
            "top_categories": top_expenses
        }
    
    def _get_profit_loss(self) -> Dict[str, Any]:
        """Calculate profit/loss"""
        revenue = self._get_revenue()
        expenses = self._get_expenses()
        
        net_profit = revenue["total"] - expenses["total"]
        margin = (net_profit / revenue["total"] * 100) if revenue["total"] else 0
        
        return {
            "revenue": revenue["total"],
            "expenses": expenses["total"],
            "net_profit": net_profit,
            "profit_margin": round(margin, 2)
        }
    
    def _get_cash_flow(self) -> Dict[str, Any]:
        """Get cash flow data"""
        # Cash inflows (receipts)
        inflows = frappe.db.sql("""
            SELECT SUM(paid_amount) as total
            FROM `tabPayment Entry`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND payment_type = 'Receive'
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        # Cash outflows (payments)
        outflows = frappe.db.sql("""
            SELECT SUM(paid_amount) as total
            FROM `tabPayment Entry`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND payment_type = 'Pay'
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        total_in = flt(inflows[0].get("total")) if inflows else 0
        total_out = flt(outflows[0].get("total")) if outflows else 0
        
        return {
            "inflows": total_in,
            "outflows": total_out,
            "net_cash_flow": total_in - total_out
        }
    
    def _get_receivables(self) -> Dict[str, Any]:
        """Get accounts receivable summary"""
        result = frappe.db.sql("""
            SELECT 
                SUM(outstanding_amount) as total_outstanding,
                COUNT(*) as invoice_count
            FROM `tabSales Invoice`
            WHERE outstanding_amount > 0
            AND company = %s
            AND docstatus = 1
        """, (self.company,), as_dict=True)
        
        # Aging analysis
        aging = frappe.db.sql("""
            SELECT 
                CASE 
                    WHEN DATEDIFF(CURDATE(), due_date) <= 0 THEN 'Not Due'
                    WHEN DATEDIFF(CURDATE(), due_date) BETWEEN 1 AND 30 THEN '0-30 Days'
                    WHEN DATEDIFF(CURDATE(), due_date) BETWEEN 31 AND 60 THEN '31-60 Days'
                    WHEN DATEDIFF(CURDATE(), due_date) BETWEEN 61 AND 90 THEN '61-90 Days'
                    ELSE '90+ Days'
                END as aging_bucket,
                SUM(outstanding_amount) as amount,
                COUNT(*) as count
            FROM `tabSales Invoice`
            WHERE outstanding_amount > 0
            AND company = %s
            AND docstatus = 1
            GROUP BY aging_bucket
            ORDER BY FIELD(aging_bucket, 'Not Due', '0-30 Days', '31-60 Days', '61-90 Days', '90+ Days')
        """, (self.company,), as_dict=True)
        
        return {
            "total_outstanding": flt(result[0].get("total_outstanding")) if result else 0,
            "invoice_count": cint(result[0].get("invoice_count")) if result else 0,
            "aging": aging
        }
    
    def _get_payables(self) -> Dict[str, Any]:
        """Get accounts payable summary"""
        result = frappe.db.sql("""
            SELECT 
                SUM(outstanding_amount) as total_outstanding,
                COUNT(*) as invoice_count
            FROM `tabPurchase Invoice`
            WHERE outstanding_amount > 0
            AND company = %s
            AND docstatus = 1
        """, (self.company,), as_dict=True)
        
        return {
            "total_outstanding": flt(result[0].get("total_outstanding")) if result else 0,
            "invoice_count": cint(result[0].get("invoice_count")) if result else 0
        }
    
    def _get_bank_balance(self) -> Dict[str, Any]:
        """Get bank balance"""
        result = frappe.db.sql("""
            SELECT 
                account,
                SUM(debit - credit) as balance
            FROM `tabGL Entry`
            WHERE company = %s
            AND account IN (
                SELECT name FROM `tabAccount` 
                WHERE account_type = 'Bank' AND company = %s
            )
            AND is_cancelled = 0
            GROUP BY account
        """, (self.company, self.company), as_dict=True)
        
        total = sum(flt(r.get("balance")) for r in result)
        
        return {
            "total": total,
            "accounts": result
        }
    
    def _get_monthly_trend(self) -> List[Dict]:
        """Get monthly revenue/expense trend"""
        result = frappe.db.sql("""
            SELECT 
                DATE_FORMAT(posting_date, '%%Y-%%m') as month,
                SUM(CASE WHEN acc.root_type = 'Income' THEN ABS(gle.debit - gle.credit) ELSE 0 END) as revenue,
                SUM(CASE WHEN acc.root_type = 'Expense' THEN gle.debit - gle.credit ELSE 0 END) as expense
            FROM `tabGL Entry` gle
            JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE gle.posting_date BETWEEN %s AND %s
            AND gle.company = %s
            AND acc.root_type IN ('Income', 'Expense')
            AND gle.is_cancelled = 0
            GROUP BY month
            ORDER BY month
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        return result


class SalesDataCollector(BaseCollector):
    """Collect sales data from Selling module"""
    
    def collect(self) -> Dict[str, Any]:
        return {
            "summary": self._get_sales_summary(),
            "top_customers": self._get_top_customers(),
            "top_items": self._get_top_items(),
            "sales_by_territory": self._get_sales_by_territory(),
            "monthly_trend": self._get_monthly_trend(),
            "conversion_rate": self._get_conversion_rate(),
            "average_order_value": self._get_aov()
        }
    
    def _get_sales_summary(self) -> Dict[str, Any]:
        """Get overall sales summary"""
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(grand_total) as total_revenue,
                SUM(net_total) as net_revenue,
                AVG(grand_total) as avg_order_value
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        return result[0] if result else {}
    
    def _get_top_customers(self, limit: int = 10) -> List[Dict]:
        """Get top customers by revenue"""
        return frappe.db.sql("""
            SELECT 
                customer,
                customer_name,
                SUM(grand_total) as total_revenue,
                COUNT(*) as order_count
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            GROUP BY customer, customer_name
            ORDER BY total_revenue DESC
            LIMIT %s
        """, (self.from_date, self.to_date, self.company, limit), as_dict=True)
    
    def _get_top_items(self, limit: int = 10) -> List[Dict]:
        """Get top selling items"""
        return frappe.db.sql("""
            SELECT 
                sii.item_code,
                sii.item_name,
                SUM(sii.qty) as total_qty,
                SUM(sii.amount) as total_revenue
            FROM `tabSales Invoice Item` sii
            JOIN `tabSales Invoice` si ON sii.parent = si.name
            WHERE si.posting_date BETWEEN %s AND %s
            AND si.company = %s
            AND si.docstatus = 1
            GROUP BY sii.item_code, sii.item_name
            ORDER BY total_revenue DESC
            LIMIT %s
        """, (self.from_date, self.to_date, self.company, limit), as_dict=True)
    
    def _get_sales_by_territory(self) -> List[Dict]:
        """Get sales by territory"""
        return frappe.db.sql("""
            SELECT 
                territory,
                SUM(grand_total) as total_revenue,
                COUNT(*) as order_count
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            AND territory IS NOT NULL
            GROUP BY territory
            ORDER BY total_revenue DESC
        """, (self.from_date, self.to_date, self.company), as_dict=True)
    
    def _get_monthly_trend(self) -> List[Dict]:
        """Get monthly sales trend"""
        return frappe.db.sql("""
            SELECT 
                DATE_FORMAT(posting_date, '%%Y-%%m') as month,
                SUM(grand_total) as revenue,
                COUNT(*) as orders
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            GROUP BY month
            ORDER BY month
        """, (self.from_date, self.to_date, self.company), as_dict=True)
    
    def _get_conversion_rate(self) -> Dict[str, Any]:
        """Get quotation to order conversion rate"""
        quotations = frappe.db.count("Quotation", {
            "transaction_date": ["between", [self.from_date, self.to_date]],
            "company": self.company,
            "docstatus": 1
        })
        
        converted = frappe.db.count("Quotation", {
            "transaction_date": ["between", [self.from_date, self.to_date]],
            "company": self.company,
            "docstatus": 1,
            "status": "Ordered"
        })
        
        rate = (converted / quotations * 100) if quotations else 0
        
        return {
            "total_quotations": quotations,
            "converted": converted,
            "conversion_rate": round(rate, 2)
        }
    
    def _get_aov(self) -> float:
        """Get average order value"""
        result = frappe.db.sql("""
            SELECT AVG(grand_total) as aov
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        return flt(result[0].get("aov")) if result else 0


class ProcurementDataCollector(BaseCollector):
    """Collect procurement data from Buying module"""
    
    def collect(self) -> Dict[str, Any]:
        return {
            "summary": self._get_procurement_summary(),
            "top_suppliers": self._get_top_suppliers(),
            "top_items": self._get_top_items(),
            "monthly_trend": self._get_monthly_trend(),
            "supplier_performance": self._get_supplier_performance(),
            "pending_orders": self._get_pending_orders()
        }
    
    def _get_procurement_summary(self) -> Dict[str, Any]:
        """Get procurement summary"""
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(grand_total) as total_spend,
                AVG(grand_total) as avg_order_value
            FROM `tabPurchase Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        return result[0] if result else {}
    
    def _get_top_suppliers(self, limit: int = 10) -> List[Dict]:
        """Get top suppliers by spend"""
        return frappe.db.sql("""
            SELECT 
                supplier,
                supplier_name,
                SUM(grand_total) as total_spend,
                COUNT(*) as order_count
            FROM `tabPurchase Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            GROUP BY supplier, supplier_name
            ORDER BY total_spend DESC
            LIMIT %s
        """, (self.from_date, self.to_date, self.company, limit), as_dict=True)
    
    def _get_top_items(self, limit: int = 10) -> List[Dict]:
        """Get top purchased items"""
        return frappe.db.sql("""
            SELECT 
                pii.item_code,
                pii.item_name,
                SUM(pii.qty) as total_qty,
                SUM(pii.amount) as total_spend
            FROM `tabPurchase Invoice Item` pii
            JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pi.posting_date BETWEEN %s AND %s
            AND pi.company = %s
            AND pi.docstatus = 1
            GROUP BY pii.item_code, pii.item_name
            ORDER BY total_spend DESC
            LIMIT %s
        """, (self.from_date, self.to_date, self.company, limit), as_dict=True)
    
    def _get_monthly_trend(self) -> List[Dict]:
        """Get monthly procurement trend"""
        return frappe.db.sql("""
            SELECT 
                DATE_FORMAT(posting_date, '%%Y-%%m') as month,
                SUM(grand_total) as spend,
                COUNT(*) as orders
            FROM `tabPurchase Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            GROUP BY month
            ORDER BY month
        """, (self.from_date, self.to_date, self.company), as_dict=True)
    
    def _get_supplier_performance(self) -> List[Dict]:
        """Get supplier delivery performance"""
        return frappe.db.sql("""
            SELECT 
                supplier,
                supplier_name,
                COUNT(*) as total_receipts,
                SUM(CASE WHEN pr.posting_date <= po.schedule_date THEN 1 ELSE 0 END) as on_time,
                ROUND(SUM(CASE WHEN pr.posting_date <= po.schedule_date THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as on_time_percent
            FROM `tabPurchase Receipt` pr
            JOIN `tabPurchase Order` po ON pr.purchase_order = po.name
            WHERE pr.posting_date BETWEEN %s AND %s
            AND pr.company = %s
            AND pr.docstatus = 1
            GROUP BY supplier, supplier_name
            HAVING total_receipts >= 3
            ORDER BY on_time_percent DESC
            LIMIT 10
        """, (self.from_date, self.to_date, self.company), as_dict=True)
    
    def _get_pending_orders(self) -> Dict[str, Any]:
        """Get pending purchase orders"""
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as count,
                SUM(grand_total) as total_value
            FROM `tabPurchase Order`
            WHERE company = %s
            AND docstatus = 1
            AND status NOT IN ('Completed', 'Closed', 'Cancelled')
        """, (self.company,), as_dict=True)
        
        return result[0] if result else {}


class InventoryDataCollector(BaseCollector):
    """Collect inventory data from Stock module"""
    
    def collect(self) -> Dict[str, Any]:
        return {
            "summary": self._get_inventory_summary(),
            "stock_value": self._get_stock_value(),
            "low_stock": self._get_low_stock_items(),
            "slow_moving": self._get_slow_moving_items(),
            "dead_stock": self._get_dead_stock(),
            "warehouse_wise": self._get_warehouse_distribution(),
            "turnover": self._get_inventory_turnover()
        }
    
    def _get_inventory_summary(self) -> Dict[str, Any]:
        """Get inventory summary"""
        total_items = frappe.db.count("Item", {"disabled": 0, "is_stock_item": 1})
        
        result = frappe.db.sql("""
            SELECT 
                COUNT(DISTINCT item_code) as items_in_stock,
                SUM(actual_qty) as total_qty
            FROM `tabBin`
            WHERE actual_qty > 0
        """, as_dict=True)
        
        return {
            "total_items": total_items,
            "items_in_stock": cint(result[0].get("items_in_stock")) if result else 0,
            "total_qty": flt(result[0].get("total_qty")) if result else 0
        }
    
    def _get_stock_value(self) -> Dict[str, Any]:
        """Get total stock value"""
        result = frappe.db.sql("""
            SELECT 
                SUM(stock_value) as total_value
            FROM `tabBin`
            WHERE actual_qty > 0
        """, as_dict=True)
        
        return {
            "total_value": flt(result[0].get("total_value")) if result else 0
        }
    
    def _get_low_stock_items(self, limit: int = 20) -> List[Dict]:
        """Get items below reorder level"""
        return frappe.db.sql("""
            SELECT 
                b.item_code,
                i.item_name,
                b.actual_qty,
                i.safety_stock,
                ir.warehouse_reorder_level as reorder_level
            FROM `tabBin` b
            JOIN `tabItem` i ON b.item_code = i.name
            LEFT JOIN `tabItem Reorder` ir ON i.name = ir.parent AND b.warehouse = ir.warehouse
            WHERE b.actual_qty <= COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0)
            AND COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) > 0
            ORDER BY (COALESCE(ir.warehouse_reorder_level, i.safety_stock, 0) - b.actual_qty) DESC
            LIMIT %s
        """, (limit,), as_dict=True)
    
    def _get_slow_moving_items(self, days: int = 90, limit: int = 20) -> List[Dict]:
        """Get slow moving items (no movement in X days)"""
        cutoff_date = add_days(nowdate(), -days)
        
        return frappe.db.sql("""
            SELECT 
                b.item_code,
                i.item_name,
                b.actual_qty,
                b.stock_value,
                MAX(sle.posting_date) as last_movement
            FROM `tabBin` b
            JOIN `tabItem` i ON b.item_code = i.name
            LEFT JOIN `tabStock Ledger Entry` sle ON b.item_code = sle.item_code AND b.warehouse = sle.warehouse
            WHERE b.actual_qty > 0
            GROUP BY b.item_code, i.item_name, b.actual_qty, b.stock_value
            HAVING last_movement < %s OR last_movement IS NULL
            ORDER BY b.stock_value DESC
            LIMIT %s
        """, (cutoff_date, limit), as_dict=True)
    
    def _get_dead_stock(self, days: int = 180, limit: int = 20) -> List[Dict]:
        """Get dead stock (no movement in 6+ months)"""
        return self._get_slow_moving_items(days=days, limit=limit)
    
    def _get_warehouse_distribution(self) -> List[Dict]:
        """Get stock distribution by warehouse"""
        return frappe.db.sql("""
            SELECT 
                warehouse,
                COUNT(DISTINCT item_code) as item_count,
                SUM(actual_qty) as total_qty,
                SUM(stock_value) as total_value
            FROM `tabBin`
            WHERE actual_qty > 0
            GROUP BY warehouse
            ORDER BY total_value DESC
        """, as_dict=True)
    
    def _get_inventory_turnover(self) -> Dict[str, Any]:
        """Calculate inventory turnover ratio"""
        # Cost of goods sold (approximation using delivery notes)
        cogs = frappe.db.sql("""
            SELECT SUM(dni.amount) as total
            FROM `tabDelivery Note Item` dni
            JOIN `tabDelivery Note` dn ON dni.parent = dn.name
            WHERE dn.posting_date BETWEEN %s AND %s
            AND dn.company = %s
            AND dn.docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        cogs_value = flt(cogs[0].get("total")) if cogs else 0
        
        # Average inventory
        stock_value = self._get_stock_value()
        avg_inventory = stock_value.get("total_value", 0)
        
        turnover = (cogs_value / avg_inventory) if avg_inventory else 0
        days_to_sell = (365 / turnover) if turnover else 0
        
        return {
            "cogs": cogs_value,
            "avg_inventory": avg_inventory,
            "turnover_ratio": round(turnover, 2),
            "days_to_sell": round(days_to_sell, 0)
        }


class ProductionDataCollector(BaseCollector):
    """Collect production data from Manufacturing module"""
    
    def collect(self) -> Dict[str, Any]:
        return {
            "summary": self._get_production_summary(),
            "work_orders": self._get_work_order_status(),
            "efficiency": self._get_production_efficiency(),
            "top_items": self._get_top_produced_items(),
            "monthly_trend": self._get_monthly_trend(),
            "workstation_utilization": self._get_workstation_utilization()
        }
    
    def _get_production_summary(self) -> Dict[str, Any]:
        """Get production summary"""
        result = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(qty) as planned_qty,
                SUM(produced_qty) as produced_qty
            FROM `tabWork Order`
            WHERE planned_start_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        return result[0] if result else {}
    
    def _get_work_order_status(self) -> List[Dict]:
        """Get work order status breakdown"""
        return frappe.db.sql("""
            SELECT 
                status,
                COUNT(*) as count,
                SUM(qty) as total_qty
            FROM `tabWork Order`
            WHERE company = %s
            AND docstatus = 1
            GROUP BY status
        """, (self.company,), as_dict=True)
    
    def _get_production_efficiency(self) -> Dict[str, Any]:
        """Calculate production efficiency"""
        result = frappe.db.sql("""
            SELECT 
                SUM(produced_qty) as produced,
                SUM(qty) as planned
            FROM `tabWork Order`
            WHERE planned_start_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            AND status = 'Completed'
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        produced = flt(result[0].get("produced")) if result else 0
        planned = flt(result[0].get("planned")) if result else 0
        efficiency = (produced / planned * 100) if planned else 0
        
        return {
            "produced_qty": produced,
            "planned_qty": planned,
            "efficiency_percent": round(efficiency, 2)
        }
    
    def _get_top_produced_items(self, limit: int = 10) -> List[Dict]:
        """Get top produced items"""
        return frappe.db.sql("""
            SELECT 
                production_item as item_code,
                item_name,
                SUM(produced_qty) as total_produced
            FROM `tabWork Order`
            WHERE planned_start_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            GROUP BY production_item, item_name
            ORDER BY total_produced DESC
            LIMIT %s
        """, (self.from_date, self.to_date, self.company, limit), as_dict=True)
    
    def _get_monthly_trend(self) -> List[Dict]:
        """Get monthly production trend"""
        return frappe.db.sql("""
            SELECT 
                DATE_FORMAT(planned_start_date, '%%Y-%%m') as month,
                SUM(qty) as planned_qty,
                SUM(produced_qty) as produced_qty
            FROM `tabWork Order`
            WHERE planned_start_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            GROUP BY month
            ORDER BY month
        """, (self.from_date, self.to_date, self.company), as_dict=True)
    
    def _get_workstation_utilization(self) -> List[Dict]:
        """Get workstation utilization"""
        return frappe.db.sql("""
            SELECT 
                workstation,
                COUNT(*) as job_count,
                SUM(time_in_mins) as total_minutes
            FROM `tabJob Card`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
            GROUP BY workstation
            ORDER BY total_minutes DESC
        """, (self.from_date, self.to_date, self.company), as_dict=True)


class CustomerDataCollector(BaseCollector):
    """Collect customer data from CRM module"""
    
    def collect(self) -> Dict[str, Any]:
        return {
            "summary": self._get_customer_summary(),
            "new_customers": self._get_new_customers(),
            "customer_segments": self._get_customer_segments(),
            "retention": self._get_retention_metrics(),
            "lifetime_value": self._get_top_ltv_customers(),
            "leads": self._get_lead_metrics()
        }
    
    def _get_customer_summary(self) -> Dict[str, Any]:
        """Get customer summary"""
        total_customers = frappe.db.count("Customer", {"disabled": 0})
        
        active_customers = frappe.db.sql("""
            SELECT COUNT(DISTINCT customer) as count
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company), as_dict=True)
        
        return {
            "total_customers": total_customers,
            "active_customers": cint(active_customers[0].get("count")) if active_customers else 0
        }
    
    def _get_new_customers(self) -> Dict[str, Any]:
        """Get new customers in period"""
        result = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabCustomer`
            WHERE creation BETWEEN %s AND %s
            AND disabled = 0
        """, (self.from_date, self.to_date), as_dict=True)
        
        # Monthly trend
        trend = frappe.db.sql("""
            SELECT 
                DATE_FORMAT(creation, '%%Y-%%m') as month,
                COUNT(*) as new_customers
            FROM `tabCustomer`
            WHERE creation BETWEEN %s AND %s
            AND disabled = 0
            GROUP BY month
            ORDER BY month
        """, (self.from_date, self.to_date), as_dict=True)
        
        return {
            "total_new": cint(result[0].get("count")) if result else 0,
            "monthly_trend": trend
        }
    
    def _get_customer_segments(self) -> List[Dict]:
        """Get customer segments by revenue"""
        return frappe.db.sql("""
            SELECT 
                c.customer_group as segment,
                COUNT(DISTINCT c.name) as customer_count,
                COALESCE(SUM(si.grand_total), 0) as total_revenue
            FROM `tabCustomer` c
            LEFT JOIN `tabSales Invoice` si ON c.name = si.customer 
                AND si.posting_date BETWEEN %s AND %s
                AND si.company = %s
                AND si.docstatus = 1
            WHERE c.disabled = 0
            GROUP BY c.customer_group
            ORDER BY total_revenue DESC
        """, (self.from_date, self.to_date, self.company), as_dict=True)
    
    def _get_retention_metrics(self) -> Dict[str, Any]:
        """Calculate customer retention metrics"""
        # Customers who purchased in both current and previous period
        prev_from = add_months(self.from_date, -12)
        prev_to = add_months(self.to_date, -12)
        
        prev_customers = frappe.db.sql("""
            SELECT DISTINCT customer
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
        """, (prev_from, prev_to, self.company))
        prev_set = set(c[0] for c in prev_customers)
        
        current_customers = frappe.db.sql("""
            SELECT DISTINCT customer
            FROM `tabSales Invoice`
            WHERE posting_date BETWEEN %s AND %s
            AND company = %s
            AND docstatus = 1
        """, (self.from_date, self.to_date, self.company))
        current_set = set(c[0] for c in current_customers)
        
        retained = prev_set.intersection(current_set)
        churned = prev_set - current_set
        
        retention_rate = (len(retained) / len(prev_set) * 100) if prev_set else 0
        churn_rate = (len(churned) / len(prev_set) * 100) if prev_set else 0
        
        return {
            "previous_period_customers": len(prev_set),
            "retained_customers": len(retained),
            "churned_customers": len(churned),
            "retention_rate": round(retention_rate, 2),
            "churn_rate": round(churn_rate, 2)
        }
    
    def _get_top_ltv_customers(self, limit: int = 10) -> List[Dict]:
        """Get top customers by lifetime value"""
        return frappe.db.sql("""
            SELECT 
                customer,
                customer_name,
                SUM(grand_total) as lifetime_value,
                COUNT(*) as total_orders,
                MIN(posting_date) as first_order,
                MAX(posting_date) as last_order
            FROM `tabSales Invoice`
            WHERE company = %s
            AND docstatus = 1
            GROUP BY customer, customer_name
            ORDER BY lifetime_value DESC
            LIMIT %s
        """, (self.company, limit), as_dict=True)
    
    def _get_lead_metrics(self) -> Dict[str, Any]:
        """Get lead metrics from CRM"""
        total_leads = frappe.db.count("Lead", {
            "creation": ["between", [self.from_date, self.to_date]]
        })
        
        converted = frappe.db.count("Lead", {
            "creation": ["between", [self.from_date, self.to_date]],
            "status": "Converted"
        })
        
        conversion_rate = (converted / total_leads * 100) if total_leads else 0
        
        # Lead sources
        sources = frappe.db.sql("""
            SELECT 
                source,
                COUNT(*) as count
            FROM `tabLead`
            WHERE creation BETWEEN %s AND %s
            GROUP BY source
            ORDER BY count DESC
            LIMIT 10
        """, (self.from_date, self.to_date), as_dict=True)
        
        return {
            "total_leads": total_leads,
            "converted_leads": converted,
            "conversion_rate": round(conversion_rate, 2),
            "lead_sources": sources
        }


# Factory function to get collector
def get_collector(collector_type: str, filters: Optional[Dict] = None) -> BaseCollector:
    """Get data collector by type"""
    collectors = {
        "financial": FinancialDataCollector,
        "sales": SalesDataCollector,
        "procurement": ProcurementDataCollector,
        "inventory": InventoryDataCollector,
        "production": ProductionDataCollector,
        "customer": CustomerDataCollector
    }
    
    collector_class = collectors.get(collector_type)
    if not collector_class:
        raise ValueError(f"Unknown collector type: {collector_type}")
    
    return collector_class(filters)


# API endpoints
@frappe.whitelist()
def get_analytics_data(analytics_type: str, filters: str = None) -> Dict[str, Any]:
    """
    Get analytics data for a specific type
    
    Args:
        analytics_type: Type of analytics (financial, sales, etc.)
        filters: JSON string of filters
        
    Returns:
        Collected data
    """
    filter_dict = {}
    if filters:
        try:
            filter_dict = frappe.parse_json(filters)
        except:
            pass
    
    collector = get_collector(analytics_type, filter_dict)
    return collector.collect()


@frappe.whitelist()
def get_all_analytics_data(filters: str = None) -> Dict[str, Any]:
    """
    Get all analytics data for all types
    
    Args:
        filters: JSON string of filters
        
    Returns:
        All collected data by type
    """
    filter_dict = {}
    if filters:
        try:
            filter_dict = frappe.parse_json(filters)
        except:
            pass
    
    result = {}
    for analytics_type in ["financial", "sales", "procurement", "inventory", "production", "customer"]:
        try:
            collector = get_collector(analytics_type, filter_dict)
            result[analytics_type] = collector.collect()
        except Exception as e:
            frappe.log_error(f"Error collecting {analytics_type} data: {str(e)}", "Analytics Collector")
            result[analytics_type] = {"error": str(e)}
    
    return result
