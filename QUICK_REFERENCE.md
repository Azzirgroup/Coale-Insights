# Frappe Insights - Quick Reference Guide

## 🗂️ Supported Databases

| Database | Port | Auth Type | SSL | Special Features |
|----------|------|-----------|-----|------------------|
| MariaDB/MySQL | 3306 | User/Pass | ✅ | UTF8MB4, Pooling |
| PostgreSQL | 5432 | User/Pass | ✅ | Schemas, Advanced types |
| SQLite | - | File | - | Local files |
| DuckDB | - | File/HTTP | ✅ | HTTP sources, Parquet |
| BigQuery | - | Service Account | ✅ | Cloud warehouse |
| ClickHouse | 8123 | User/Pass | ✅ | OLAP, Real-time |
| MS SQL Server | 1433 | User/Pass | ✅ | Windows/Linux |
| Frappe DB | - | Auto | Auto | DocTypes, Replicas |

## 🎯 Intelligence Dashboards

| Dashboard | Route | Key Features |
|-----------|-------|--------------|
| **Financial** | `/financial-intelligence` | P&L, Cash Flow, Tax (KRA), AR/AP, Forex |
| **Sales** | `/sales-intelligence` | Revenue, Growth%, Cash vs Credit, Reps, Forecasts |
| **Inventory** | `/inventory-intelligence` | ABC/XYZ, Turnover, Aging, Dead Stock |
| **Procurement** | `/procurement-intelligence` | Spend, Suppliers, Lead Time, OTD%, Risk Score |
| **Customer** | `/customer-intelligence` | CLV Tiers, RFM, Churn, Cross-sell, Cohorts |
| **Customer 360** | `/customer-360` | Individual deep-dive, Purchase history |
| **Risk** | `/risk-intelligence` | Risk Matrix, Alerts, Prophet Forecasting |
| **Tax (KRA)** | `/tax-intelligence` | Corporate Tax (30%), VAT (16%), iTax |
| **Strategic Finance** | `/strategic-finance-intelligence` | 13-Week Cash, Scenarios, Ratios, Budget |
| **AI Insights** | `/ai-insights` | Natural language queries, Multi-module |

## 🤖 AI Models (Free Tier)

```
Primary Models (OpenRouter):
1. meta-llama/llama-3.3-70b-instruct:free (Default)
2. openai/gpt-oss-120b:free
3. google/gemini-2.0-flash-exp:free
4. qwen/qwen3-235b-a22b:free
5. mistralai/mistral-small-3.1-24b-instruct:free
6. nousresearch/hermes-3-llama-3.1-405b:free
```

## 📊 ML Models

| Model | Purpose | Schedule | Output |
|-------|---------|----------|--------|
| Customer Segmentation | RFM & CLV | Daily | Segments, Tiers, Churn % |
| ABC/XYZ Classification | Inventory classification | Weekly | 9 categories |
| Sales Forecast | Future sales | Daily | 30/60/90-day forecasts |
| Payment Prediction | Payment delays | Daily | Delay probability |
| Demand Forecast | Product demand | Weekly | Item-level demand |
| Product Recommendations | Cross-sell/Upsell | Weekly | Top 10 per customer |

## 📈 Chart Types (13)

```
1. Number (KPI)          8. Scatter
2. Trend                 9. Funnel
3. Line                 10. Progress
4. Bar (Vertical)       11. Mixed Axis
5. Row (Horizontal)     12. Pivot Table
6. Pie                  13. Text
7. Table
```

## 🔧 Key API Endpoints

### Data Sources
```python
# List all
GET /api/method/insights.api.data_sources.get_data_sources

# Test connection
POST /api/method/insights.api.data_sources.test_connection

# Get tables
GET /api/method/insights.api.data_sources.get_table_list?data_source=name

# Get columns
GET /api/method/insights.api.data_sources.get_table_columns?data_source=name&table=table_name
```

### Queries
```python
# Execute query
POST /api/method/insights.api.queries.execute_query

# Export results
GET /api/method/insights.api.queries.export_query?query=name&format=csv
```

### ML APIs
```python
# ML status
GET /api/method/insights.api.ml.get_ml_status

# Customer segments
GET /api/method/insights.api.ml.get_customer_segments

# Sales forecast
GET /api/method/insights.api.ml.get_sales_forecast

# ABC/XYZ
GET /api/method/insights.api.ml.get_abc_xyz_classification

# Supplier risk
GET /api/method/insights.api.ml.calculate_supplier_risk_score
```

### AI Insights
```python
# Get AI insights
POST /api/method/insights.api.ai_insights.get_ai_insights
{
    "query": "What were top customers last month?",
    "module": "selling",
    "complexity": "simple"
}
```

### Data Warehouse
```python
# Import table
POST /api/method/insights.api.data_store.import_table
{
    "data_source": "Site DB",
    "table": "Sales Invoice"
}

# Sync all
POST /api/method/insights.api.data_store.sync_tables
```

## ⚙️ Configuration Cheat Sheet

### Insights Settings

```python
# Performance
query_result_expiry: 10          # Cache in minutes
query_result_limit: 1000         # Max rows
max_execution_time: 300          # Seconds

# Data Warehouse
enable_data_store: 1
max_records_to_sync: 1000000    # 1M rows
max_memory_usage: 512           # MB

# AI
enable_ai_analytics: 1
ai_model: "meta-llama/llama-3.3-70b-instruct:free"
daily_ai_quota: 100
```

### Connection Strings

**PostgreSQL:**
```
postgresql://user:pass@host:5432/dbname?sslmode=require
```

**MariaDB:**
```
mysql+pymysql://user:pass@host:3306/dbname?charset=utf8mb4
```

**DuckDB HTTP:**
```
https://example.com/data.parquet
```

## 🗄️ Data Warehouse

### File Locations
```bash
# Warehouse database
/private/files/insights_data_warehouse/insights.duckdb

# Parquet files
/private/files/insights_data_warehouse/{datasource}.{table}.parquet
```

### Import Configuration

```python
# Per-table settings (Insights Table v3)
row_limit: 1000000              # Max rows to import
before_import_script: ""        # Python transformation script

# Global settings (Insights Settings)
max_records_to_sync: 1000000
max_memory_usage: 512           # MB
```

### Sync Schedule

```python
# Daily (via hooks.py)
"insights.api.data_store.sync_tables"           # All tables
"insights.analytics.ml_engine.refresh_all_dashboards"
"insights.analytics.ml_engine.reset_ai_quota"

# Hourly
"insights.api.data_store.update_failed_sync_status"

# Weekly
"insights.ml.scheduler.train_abc_xyz_classification"
```

## 🔐 User Roles

| Role | Permissions |
|------|-------------|
| **Insights Admin** | Full access: create/edit/delete all |
| **Insights User** | Create own, view shared, read-only to others |
| **System Manager** | All + system config |

## 🎨 Query Types

### 1. Visual Query Builder
```
Select Data Source → Add Tables → Join → Select Columns →
Filter → Group By → Sort → Limit → Run
```

### 2. Native SQL
```sql
SELECT customer_name, SUM(grand_total)
FROM `tabSales Invoice`
WHERE posting_date >= '2024-01-01'
GROUP BY customer_name
ORDER BY 2 DESC
LIMIT 10;
```

### 3. Script Query (Python/Ibis)
```python
from ibis import _

invoices = table('Sales Invoice')
result = (
    invoices
    .group_by('customer_name')
    .aggregate(total=_.grand_total.sum())
    .order_by(_.total.desc())
    .limit(10)
)
return result
```

### 4. AI-Assisted
```
Natural language: "Show me top 10 customers by revenue in 2024"
→ Generates SQL automatically
```

## 🔍 Filter Operators

```
=, !=, >, <, >=, <=
IN, NOT IN
LIKE, NOT LIKE
BETWEEN
IS NULL, IS NOT NULL
```

## 📦 Installation

```bash
# Get app
bench get-app insights https://github.com/frappe/insights

# Install
bench --site site.local install-app insights

# Build
bench build --app insights

# Restart
bench restart
```

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run Query | `Cmd/Ctrl + Enter` |
| Format SQL | `Cmd/Ctrl + Shift + F` |
| Toggle Sidebar | `Cmd/Ctrl + B` |
| New Query | `Cmd/Ctrl + N` |
| Save | `Cmd/Ctrl + S` |
| Search | `Cmd/Ctrl + K` |

## 🐛 Quick Troubleshooting

### Connection Issues
```bash
# Test from terminal
mysql -h host -u user -p database
psql -h host -U user database
```

### Out of Memory
```python
# Reduce in Settings
max_memory_usage: 256  # Lower from 512
row_limit: 500000      # Lower from 1M
```

### Slow Queries
```python
# Use warehouse instead of direct query
# Add indexes on source DB
# Enable caching: query_result_expiry: 60
# Limit rows: query_result_limit: 1000
```

### AI Quota Exceeded
```python
# Increase quota
daily_ai_quota: 200  # Up from 100

# Or wait for daily reset (midnight)
```

## 🌐 Embedding Dashboards

```html
<!-- Add domain to Settings > Allowed Origins -->
<iframe
    src="https://your-site.local/insights/dashboard/dashboard-name"
    width="100%"
    height="600"
    frameborder="0">
</iframe>
```

## 📊 ERPNext Module Mapping

| Module | Key DocTypes |
|--------|--------------|
| **Accounts** | GL Entry, Journal Entry, Payment Entry, Sales/Purchase Invoice |
| **Selling** | Sales Order, Sales Invoice, Customer, Quotation, Delivery Note |
| **Buying** | Purchase Order, Purchase Invoice, Supplier, Purchase Receipt |
| **Stock** | Item, Warehouse, Stock Entry, Stock Ledger Entry, Serial No |
| **Manufacturing** | BOM, Work Order, Production Plan, Job Card |
| **Projects** | Project, Task, Timesheet, Issue |
| **CRM** | Lead, Opportunity, Campaign, Email Campaign |
| **HR** | Employee, Attendance, Salary Slip, Leave Application |
| **Assets** | Asset, Asset Movement, Asset Depreciation Schedule |
| **Support** | Issue, Service Level Agreement, Warranty Claim |

## 🎯 Customer Segmentation

### CLV Tiers
```
💎 Diamond: Top 1%
🏆 Platinum: Top 5%
🥇 Gold: Top 20%
🥈 Silver: Top 50%
🥉 Bronze: Rest
```

### RFM Segments
```
- Champions (High R, F, M)
- Loyal Customers
- Potential Loyalists
- At Risk
- Can't Lose Them
- Hibernating
- Lost
```

## 📈 Financial Ratios (Strategic Finance)

```python
# Liquidity
Current Ratio = Current Assets / Current Liabilities
Quick Ratio = (Current Assets - Inventory) / Current Liabilities

# Profitability
Gross Margin = (Revenue - COGS) / Revenue
Net Margin = Net Income / Revenue
ROA = Net Income / Total Assets
ROE = Net Income / Shareholders' Equity

# Efficiency
DSO = (AR / Revenue) × Days
DPO = (AP / COGS) × Days
Inventory Turnover = COGS / Avg Inventory
```

## 🚀 Performance Tips

1. **Use Data Warehouse** for large tables (>100K rows)
2. **Index source databases** on filter/join columns
3. **Enable caching** for frequently-run queries
4. **Limit result rows** to what you need
5. **Use aggregations** instead of row-level data
6. **Schedule heavy queries** during off-peak hours
7. **Use database replicas** for analytics

## 📞 Support

- 🐛 Issues: https://github.com/frappe/insights/issues
- 💬 Forum: https://discuss.frappe.io
- 📖 Docs: https://docs.frappe.io/insights
- 📧 Email: hello@frappe.io

---

**Version:** 3.0 | **License:** GPLv3 | **Last Updated:** January 2025
