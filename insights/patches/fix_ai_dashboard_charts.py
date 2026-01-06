"""
Fix AI Analytics Dashboard Charts with proper config format
"""
import frappe
import json

def execute():
    """Fix chart configurations for AI Analytics dashboards"""
    
    # Get all charts in workbook 2 (AI Analytics)
    charts = frappe.get_all('Insights Chart v3', 
        filters={'workbook': '2'},
        fields=['name', 'title', 'chart_type', 'query', 'config'])
    
    print(f"Found {len(charts)} charts to fix")
    
    for chart_data in charts:
        chart = frappe.get_doc('Insights Chart v3', chart_data['name'])
        old_config = frappe.parse_json(chart.config) if chart.config else {}
        
        # Get the query to understand the columns
        query = frappe.get_doc('Insights Query v3', chart.query) if chart.query else None
        if not query:
            print(f"  Skipping {chart.title} - no query")
            continue
        
        x_axis = old_config.get('xAxis', '')
        y_axis_cols = old_config.get('yAxis', [])
        if isinstance(y_axis_cols, str):
            y_axis_cols = [y_axis_cols]
        
        chart_type = chart.chart_type
        
        # Build proper config based on chart type
        if chart_type in ['bar', 'Bar', 'line', 'Line', 'Row']:
            # Axis chart config
            new_config = {
                'x_axis': {
                    'dimension': {
                        'dimension_name': x_axis,
                        'column_name': x_axis,
                        'data_type': 'String'
                    }
                },
                'y_axis': {
                    'series': []
                }
            }
            
            for y_col in y_axis_cols:
                if y_col:
                    new_config['y_axis']['series'].append({
                        'measure': {
                            'measure_name': y_col,
                            'column_name': y_col,
                            'data_type': 'Decimal',
                            'aggregation': 'sum'
                        },
                        'type': 'bar' if chart_type.lower() == 'bar' else 'line'
                    })
            
            # Normalize chart type
            chart.chart_type = 'Bar' if chart_type.lower() == 'bar' else 'Line'
            
        elif chart_type in ['pie', 'Pie', 'Donut']:
            # Donut/Pie chart config
            new_config = {
                'label_column': {
                    'dimension_name': x_axis,
                    'column_name': x_axis,
                    'data_type': 'String'
                },
                'value_column': {
                    'measure_name': y_axis_cols[0] if y_axis_cols else '',
                    'column_name': y_axis_cols[0] if y_axis_cols else '',
                    'data_type': 'Decimal',
                    'aggregation': 'sum'
                }
            }
            chart.chart_type = 'Donut'
            
        elif chart_type in ['table', 'Table']:
            # Table chart config
            new_config = {
                'rows': [
                    {
                        'column_name': x_axis,
                        'data_type': 'String'
                    }
                ]
            }
            for y_col in y_axis_cols:
                if y_col:
                    new_config['rows'].append({
                        'column_name': y_col,
                        'data_type': 'Decimal'
                    })
            chart.chart_type = 'Table'
        else:
            print(f"  Unknown chart type: {chart_type} for {chart.title}")
            continue
        
        chart.config = json.dumps(new_config)
        chart.save(ignore_permissions=True)
        print(f"  Fixed: {chart.title} ({chart.chart_type})")
    
    frappe.db.commit()
    print("\n✅ Chart configurations fixed!")


if __name__ == "__main__":
    execute()
