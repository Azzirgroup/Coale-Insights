"""
Populate AI Analytics Dashboards with actual ERPNext queries and charts (v3)
"""
import frappe
import json

def execute():
    """Create queries and charts for AI Analytics dashboards using v3 DocTypes"""
    
    # Get data source
    data_source = frappe.db.get_value('Insights Data Source v3', {'is_site_db': 1}, 'name')
    if not data_source:
        print("No site database found")
        return
    
    print(f"Using data source: {data_source}")
    
    # Get AI Analytics Workbook
    workbooks = frappe.get_all('Insights Workbook', filters={'title': 'AI Analytics Workbook'}, limit=1)
    if not workbooks:
        # Create workbook
        workbook = frappe.get_doc({
            'doctype': 'Insights Workbook',
            'title': 'AI Analytics Workbook'
        })
        workbook.insert(ignore_permissions=True)
        workbook_name = workbook.name
    else:
        workbook_name = workbooks[0].name
    
    print(f"Using workbook: {workbook_name}")
    
    # Dashboard configurations with v3-compatible operations
    dashboard_configs = {
        'Financial Analytics': {
            'queries': [
                {
                    'title': 'Monthly Revenue Trend',
                    'sql': '''
                        SELECT 
                            DATE_FORMAT(posting_date, '%Y-%m') as month,
                            ROUND(SUM(grand_total), 2) as revenue,
                            COUNT(*) as invoices
                        FROM `tabSales Invoice`
                        WHERE docstatus = 1
                        GROUP BY DATE_FORMAT(posting_date, '%Y-%m')
                        ORDER BY month DESC
                        LIMIT 12
                    ''',
                    'chart_type': 'bar',
                    'x_axis': 'month',
                    'y_axis': 'revenue'
                },
                {
                    'title': 'Payment Collections',
                    'sql': '''
                        SELECT 
                            DATE_FORMAT(posting_date, '%Y-%m') as month,
                            ROUND(SUM(paid_amount), 2) as collected
                        FROM `tabPayment Entry`
                        WHERE docstatus = 1 AND payment_type = 'Receive'
                        GROUP BY DATE_FORMAT(posting_date, '%Y-%m')
                        ORDER BY month DESC
                        LIMIT 12
                    ''',
                    'chart_type': 'line',
                    'x_axis': 'month',
                    'y_axis': 'collected'
                },
                {
                    'title': 'Outstanding Receivables',
                    'sql': '''
                        SELECT 
                            customer_name,
                            ROUND(SUM(outstanding_amount), 2) as outstanding
                        FROM `tabSales Invoice`
                        WHERE docstatus = 1 AND outstanding_amount > 0
                        GROUP BY customer_name
                        ORDER BY outstanding DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'bar',
                    'x_axis': 'customer_name',
                    'y_axis': 'outstanding'
                }
            ]
        },
        'Sales Intelligence': {
            'queries': [
                {
                    'title': 'Top Selling Items',
                    'sql': '''
                        SELECT 
                            item_name,
                            ROUND(SUM(amount), 2) as total_sales,
                            SUM(qty) as qty_sold
                        FROM `tabSales Invoice Item`
                        WHERE docstatus = 1
                        GROUP BY item_name
                        ORDER BY total_sales DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'bar',
                    'x_axis': 'item_name',
                    'y_axis': 'total_sales'
                },
                {
                    'title': 'Sales by Customer',
                    'sql': '''
                        SELECT 
                            customer_name,
                            ROUND(SUM(grand_total), 2) as total_sales,
                            COUNT(*) as orders
                        FROM `tabSales Invoice`
                        WHERE docstatus = 1
                        GROUP BY customer_name
                        ORDER BY total_sales DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'pie',
                    'x_axis': 'customer_name',
                    'y_axis': 'total_sales'
                },
                {
                    'title': 'Monthly Sales Growth',
                    'sql': '''
                        SELECT 
                            DATE_FORMAT(posting_date, '%Y-%m') as month,
                            ROUND(SUM(grand_total), 2) as sales,
                            COUNT(DISTINCT customer) as customers
                        FROM `tabSales Invoice`
                        WHERE docstatus = 1
                        GROUP BY DATE_FORMAT(posting_date, '%Y-%m')
                        ORDER BY month DESC
                        LIMIT 12
                    ''',
                    'chart_type': 'line',
                    'x_axis': 'month',
                    'y_axis': 'sales'
                }
            ]
        },
        'Procurement Analytics': {
            'queries': [
                {
                    'title': 'Purchase by Supplier',
                    'sql': '''
                        SELECT 
                            supplier_name,
                            ROUND(SUM(grand_total), 2) as total_purchase
                        FROM `tabPurchase Invoice`
                        WHERE docstatus = 1
                        GROUP BY supplier_name
                        ORDER BY total_purchase DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'bar',
                    'x_axis': 'supplier_name',
                    'y_axis': 'total_purchase'
                },
                {
                    'title': 'Monthly Purchase Trend',
                    'sql': '''
                        SELECT 
                            DATE_FORMAT(posting_date, '%Y-%m') as month,
                            ROUND(SUM(grand_total), 2) as purchases
                        FROM `tabPurchase Invoice`
                        WHERE docstatus = 1
                        GROUP BY DATE_FORMAT(posting_date, '%Y-%m')
                        ORDER BY month DESC
                        LIMIT 12
                    ''',
                    'chart_type': 'line',
                    'x_axis': 'month',
                    'y_axis': 'purchases'
                },
                {
                    'title': 'Pending Purchase Orders',
                    'sql': '''
                        SELECT 
                            supplier_name,
                            COUNT(*) as pending_orders,
                            ROUND(SUM(grand_total), 2) as pending_value
                        FROM `tabPurchase Order`
                        WHERE docstatus = 1 AND status NOT IN ('Completed', 'Closed')
                        GROUP BY supplier_name
                        ORDER BY pending_value DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'bar',
                    'x_axis': 'supplier_name',
                    'y_axis': 'pending_value'
                }
            ]
        },
        'Inventory Insights': {
            'queries': [
                {
                    'title': 'Stock Value by Warehouse',
                    'sql': '''
                        SELECT 
                            warehouse,
                            ROUND(SUM(actual_qty * valuation_rate), 2) as stock_value,
                            SUM(actual_qty) as total_qty
                        FROM `tabBin`
                        WHERE actual_qty > 0
                        GROUP BY warehouse
                        ORDER BY stock_value DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'pie',
                    'x_axis': 'warehouse',
                    'y_axis': 'stock_value'
                },
                {
                    'title': 'Low Stock Items',
                    'sql': '''
                        SELECT 
                            i.item_name,
                            b.actual_qty as current_stock,
                            b.warehouse
                        FROM `tabBin` b
                        JOIN `tabItem` i ON b.item_code = i.name
                        WHERE b.actual_qty > 0 AND b.actual_qty < 10
                        ORDER BY b.actual_qty ASC
                        LIMIT 20
                    ''',
                    'chart_type': 'table',
                    'x_axis': 'item_name',
                    'y_axis': 'current_stock'
                },
                {
                    'title': 'Stock Movement Trend',
                    'sql': '''
                        SELECT 
                            DATE_FORMAT(posting_date, '%Y-%m') as month,
                            SUM(CASE WHEN actual_qty > 0 THEN actual_qty ELSE 0 END) as stock_in,
                            SUM(CASE WHEN actual_qty < 0 THEN ABS(actual_qty) ELSE 0 END) as stock_out
                        FROM `tabStock Ledger Entry`
                        WHERE is_cancelled = 0
                        GROUP BY DATE_FORMAT(posting_date, '%Y-%m')
                        ORDER BY month DESC
                        LIMIT 12
                    ''',
                    'chart_type': 'line',
                    'x_axis': 'month',
                    'y_axis': 'stock_in'
                }
            ]
        },
        'Customer Intelligence': {
            'queries': [
                {
                    'title': 'Customer Lifetime Value',
                    'sql': '''
                        SELECT 
                            customer_name,
                            ROUND(SUM(grand_total), 2) as lifetime_value,
                            COUNT(*) as total_orders,
                            MIN(posting_date) as first_order,
                            MAX(posting_date) as last_order
                        FROM `tabSales Invoice`
                        WHERE docstatus = 1
                        GROUP BY customer_name
                        ORDER BY lifetime_value DESC
                        LIMIT 15
                    ''',
                    'chart_type': 'bar',
                    'x_axis': 'customer_name',
                    'y_axis': 'lifetime_value'
                },
                {
                    'title': 'Customer by Territory',
                    'sql': '''
                        SELECT 
                            territory,
                            COUNT(*) as customer_count
                        FROM `tabCustomer`
                        WHERE disabled = 0
                        GROUP BY territory
                        ORDER BY customer_count DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'pie',
                    'x_axis': 'territory',
                    'y_axis': 'customer_count'
                },
                {
                    'title': 'New Customers by Month',
                    'sql': '''
                        SELECT 
                            DATE_FORMAT(creation, '%Y-%m') as month,
                            COUNT(*) as new_customers
                        FROM `tabCustomer`
                        GROUP BY DATE_FORMAT(creation, '%Y-%m')
                        ORDER BY month DESC
                        LIMIT 12
                    ''',
                    'chart_type': 'line',
                    'x_axis': 'month',
                    'y_axis': 'new_customers'
                }
            ]
        },
        'Production Analytics': {
            'queries': [
                {
                    'title': 'Items by Category',
                    'sql': '''
                        SELECT 
                            item_group,
                            COUNT(*) as item_count
                        FROM `tabItem`
                        WHERE disabled = 0
                        GROUP BY item_group
                        ORDER BY item_count DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'pie',
                    'x_axis': 'item_group',
                    'y_axis': 'item_count'
                },
                {
                    'title': 'BOM Cost Analysis',
                    'sql': '''
                        SELECT 
                            item,
                            ROUND(total_cost, 2) as bom_cost,
                            quantity
                        FROM `tabBOM`
                        WHERE is_active = 1 AND is_default = 1
                        ORDER BY total_cost DESC
                        LIMIT 10
                    ''',
                    'chart_type': 'bar',
                    'x_axis': 'item',
                    'y_axis': 'bom_cost'
                },
                {
                    'title': 'Stock Items Overview',
                    'sql': '''
                        SELECT 
                            CASE WHEN is_stock_item = 1 THEN 'Stock Item' ELSE 'Non-Stock' END as item_type,
                            COUNT(*) as count
                        FROM `tabItem`
                        WHERE disabled = 0
                        GROUP BY is_stock_item
                    ''',
                    'chart_type': 'pie',
                    'x_axis': 'item_type',
                    'y_axis': 'count'
                }
            ]
        }
    }
    
    # Get existing dashboards
    dashboards = frappe.get_all(
        'Insights Dashboard v3',
        filters={'workbook': workbook_name},
        fields=['name', 'title']
    )
    dashboard_map = {d['title']: d['name'] for d in dashboards}
    
    # Create queries and charts for each dashboard
    for dashboard_title, config in dashboard_configs.items():
        if dashboard_title not in dashboard_map:
            print(f"Dashboard '{dashboard_title}' not found, skipping...")
            continue
        
        dashboard_name = dashboard_map[dashboard_title]
        print(f"\nProcessing: {dashboard_title}")
        
        chart_items = []
        
        for i, query_config in enumerate(config['queries']):
            try:
                # Get max sort order
                max_sort_order = frappe.db.get_value(
                    "Insights Query v3",
                    filters={"workbook": workbook_name},
                    fieldname="max(sort_order)",
                ) or -1
                
                # Create operations for the SQL query
                operations = [
                    {
                        "type": "sql",
                        "data_source": data_source,
                        "raw_sql": query_config['sql'].strip()
                    }
                ]
                
                # Create v3 Query
                query = frappe.get_doc({
                    'doctype': 'Insights Query v3',
                    'title': query_config['title'],
                    'workbook': workbook_name,
                    'is_native_query': 1,
                    'operations': json.dumps(operations),
                    'sort_order': max_sort_order + 1
                })
                query.insert(ignore_permissions=True)
                frappe.db.commit()
                print(f"  Created query: {query_config['title']} ({query.name})")
                
                # Get max chart sort order
                max_chart_sort = frappe.db.get_value(
                    "Insights Chart v3",
                    filters={"workbook": workbook_name},
                    fieldname="max(sort_order)",
                ) or -1
                
                # Chart config
                chart_config = {
                    'chartType': query_config['chart_type'],
                    'title': query_config['title'],
                    'query': query.name,
                    'xAxis': query_config.get('x_axis', ''),
                    'yAxis': [query_config.get('y_axis', '')]
                }
                
                # Create v3 Chart
                chart = frappe.get_doc({
                    'doctype': 'Insights Chart v3',
                    'title': query_config['title'],
                    'workbook': workbook_name,
                    'query': query.name,
                    'chart_type': query_config['chart_type'],
                    'config': json.dumps(chart_config),
                    'sort_order': max_chart_sort + 1
                })
                chart.insert(ignore_permissions=True)
                frappe.db.commit()
                print(f"  Created chart: {query_config['title']} ({chart.name})")
                
                # Calculate layout position (2 charts per row)
                width = 10
                height = 8
                x = (i % 2) * 10
                y = (i // 2) * 8
                
                chart_items.append({
                    'type': 'chart',
                    'chart': chart.name,
                    'layout': {
                        'i': str(i),
                        'x': x,
                        'y': y,
                        'w': width,
                        'h': height
                    }
                })
                
            except Exception as e:
                print(f"  Error creating {query_config['title']}: {str(e)[:150]}")
                import traceback
                traceback.print_exc()
        
        # Update dashboard with chart items
        if chart_items:
            try:
                dashboard = frappe.get_doc('Insights Dashboard v3', dashboard_name)
                dashboard.items = json.dumps(chart_items)
                dashboard.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"  Updated dashboard with {len(chart_items)} charts")
            except Exception as e:
                print(f"  Error updating dashboard: {str(e)[:100]}")
    
    frappe.db.commit()
    print("\n✅ AI Analytics dashboards populated successfully!")


if __name__ == "__main__":
    execute()
