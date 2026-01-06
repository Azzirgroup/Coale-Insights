# Frappe Insights - Complete Documentation

![Frappe Insights](frontend/insights-logo.png)

**Version:** 3.0
**Developer:** Frappe Technologies Pvt. Ltd.
**License:** GNU GPLv3
**Website:** https://frappe.io/insights

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Database Integration Capabilities](#database-integration-capabilities)
5. [Intelligence Dashboards](#intelligence-dashboards)
6. [AI & Machine Learning Features](#ai--machine-learning-features)
7. [Query System](#query-system)
8. [Data Warehouse](#data-warehouse)
9. [API Endpoints](#api-endpoints)
10. [Configuration & Settings](#configuration--settings)
11. [User Roles & Permissions](#user-roles--permissions)
12. [Getting Started](#getting-started)
13. [FAQ](#faq)
14. [Troubleshooting](#troubleshooting)
15. [Roadmap](#roadmap)

---

## Overview

**Frappe Insights** is a powerful, self-hosted business intelligence and analytics platform built on the Frappe Framework. It enables organizations to connect to multiple data sources, create sophisticated queries, build interactive dashboards, and leverage AI-powered analytics—all without writing code.

### What Makes Insights Unique?

- 🔌 **Multi-Database Connectivity**: Connect to 8+ database types
- 🤖 **AI-Powered Analytics**: Built-in ML models and conversational AI assistant
- 📊 **No-Code Query Builder**: Visual query building with SQL support
- 🏢 **ERPNext Deep Integration**: Native integration with all ERPNext modules
- 🎨 **Customizable Dashboards**: Drag-and-drop dashboard builder with 13+ widget types
- 🔐 **Enterprise-Grade Security**: Row-level permissions and role-based access control
- 📦 **Data Warehouse**: Built-in DuckDB-based data warehouse with Parquet storage
- 🌐 **Embeddable**: Embed charts and dashboards in any website
- 💰 **Open Source**: Fully open-source under GPLv3

---

## Key Features

### 1. **Data Source Management**

Connect and query data from multiple sources simultaneously:

- **Supported Databases** (8 types):
  - MariaDB / MySQL
  - PostgreSQL
  - SQLite
  - DuckDB (including HTTP data sources)
  - Google BigQuery
  - ClickHouse (OLAP)
  - Microsoft SQL Server
  - Frappe DB (native with replica support)

- **Connection Features**:
  - SSL/TLS encryption support
  - Connection pooling for performance
  - Automatic schema discovery
  - Table and column metadata caching
  - Test connection before saving
  - Multiple data sources per installation

### 2. **Query Builder**

Four powerful query modes:

#### Visual Query Builder
- Drag-and-drop interface
- Table joins with visual relationship mapping
- Aggregations (SUM, AVG, COUNT, MIN, MAX, etc.)
- Grouping and sorting
- Calculated columns with expressions
- Filter builder with AND/OR logic
- Preview results in real-time

#### Native SQL Editor
- Full SQL support for power users
- Syntax highlighting
- Query formatting
- Auto-completion
- Query history
- Parameter binding for dynamic queries

#### Script Query (Python)
- Write Python scripts using Ibis framework
- Access to full Python ecosystem
- Complex data transformations
- Custom business logic

#### AI-Assisted Query
- Natural language to SQL conversion
- Query optimization suggestions
- Automatic query generation from descriptions

### 3. **Dashboard System**

Build interactive, real-time dashboards:

#### Dashboard Features
- **Drag-and-Drop Builder**: Grid-based layout with responsive design
- **13+ Widget Types**:
  - Number (KPI cards)
  - Trend indicators
  - Line charts
  - Bar charts (vertical & horizontal)
  - Pie charts
  - Scatter plots
  - Funnel charts
  - Progress bars
  - Mixed axis charts
  - Pivot tables
  - Data tables
  - Filter controls
  - Text widgets
- **Cross-Widget Filtering**: Click on any chart to filter entire dashboard
- **Auto-Refresh**: Configure refresh intervals
- **Sharing**: Public/private dashboards with access control
- **Embedding**: Embed in external websites with CORS support
- **Export**: Download as images or PDFs
- **Themes**: Light/dark mode support

### 4. **Data Warehouse**

Integrated data warehouse for performance and offline analytics:

#### Warehouse Features
- **Storage Engine**: DuckDB with Parquet compression
- **Import Modes**:
  - Full sync: Complete table import
  - Incremental sync: FIFO-based updates using primary keys
  - Scheduled sync: Daily/hourly automated imports
- **Performance**:
  - Batch processing with configurable batch sizes
  - Memory-aware import (default 512 MB limit)
  - Automatic row limit (default 1M records per table)
  - Query result caching
- **Transformations**:
  - Pre-import Python scripts for data cleaning
  - Column renaming and type conversion
  - Calculated columns
- **Storage Location**: `/private/files/insights_data_warehouse/`
- **File Format**: Snappy-compressed Parquet files

### 5. **Notebook / Workbook System**

Interactive notebooks for analysis and documentation:

- **Block-Based Editor**: TipTap rich text editor
- **Embed Queries**: Inline query execution
- **Embed Charts**: Live chart rendering
- **Markdown Support**: Full markdown formatting
- **Collaboration**: Share notebooks with teams
- **Export**: Export as PDF or HTML

### 6. **Alerts & Notifications**

Automated alerting system:

- **Alert Types**:
  - Threshold alerts (value crosses threshold)
  - Anomaly detection
  - Data freshness alerts
  - Custom conditions
- **Notification Channels**:
  - Email notifications
  - Telegram integration (via API token)
  - In-app notifications
- **Scheduling**: Hourly, daily, weekly, monthly checks
- **Alert History**: Track all alert triggers

---

## Database Integration Capabilities

### Supported Database Systems

| Database | Version | Authentication | SSL/TLS | Special Features |
|----------|---------|----------------|---------|------------------|
| **MariaDB** | 10.3+ | User/Pass | ✅ | Charset UTF8MB4, Connection pooling |
| **MySQL** | 5.7+ | User/Pass | ✅ | Same as MariaDB |
| **PostgreSQL** | 10+ | User/Pass, Connection String | ✅ | Schema support, Advanced types |
| **SQLite** | 3.x | File path | N/A | Local file databases |
| **DuckDB** | 0.8+ | File path, HTTP | ✅ | HTTP data sources, Parquet/CSV reading |
| **BigQuery** | - | Service Account JSON | ✅ | Cloud data warehouse, Massive scale |
| **ClickHouse** | 21+ | User/Pass | ✅ | OLAP, Real-time analytics |
| **MS SQL Server** | 2017+ | User/Pass | ✅ | Windows/Linux support |
| **Frappe DB** | Native | Auto (site DB) | Auto | DocType relationships, Replica support |

### Connection Configuration

#### Example: PostgreSQL Connection
```json
{
  "title": "Production PostgreSQL",
  "database_type": "PostgreSQL",
  "host": "db.example.com",
  "port": 5432,
  "database_name": "production_db",
  "schema": "public",
  "username": "insights_user",
  "password": "********",
  "use_ssl": true,
  "connection_string": "postgresql://user:pass@host:5432/dbname?sslmode=require"
}
```

#### Example: BigQuery Connection
```json
{
  "title": "Analytics BigQuery",
  "database_type": "BigQuery",
  "bigquery_project_id": "my-project-12345",
  "bigquery_dataset_id": "analytics_dataset",
  "bigquery_service_account_key": {
    "type": "service_account",
    "project_id": "my-project-12345",
    "private_key_id": "key123",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...",
    "client_email": "insights@my-project.iam.gserviceaccount.com"
  }
}
```

#### Example: DuckDB HTTP Data Source
```json
{
  "title": "Public CSV Dataset",
  "database_type": "DuckDB",
  "database_name": "https://example.com/data.csv",
  "http_headers": {
    "Authorization": "Bearer token123",
    "Custom-Header": "value"
  }
}
```

### ERPNext Integration

**Native Frappe DB Integration** provides deep access to ERPNext data:

- **10 Integrated Modules**:
  1. **Accounts**: GL, Journal Entries, Invoices, Payments
  2. **Selling**: Sales Orders, Sales Invoices, Customers, Quotations
  3. **Buying**: Purchase Orders, Purchase Invoices, Suppliers
  4. **Stock**: Items, Warehouses, Stock Entries, Stock Ledger
  5. **Manufacturing**: BOMs, Work Orders, Production Plans
  6. **Projects**: Projects, Tasks, Timesheets, Issues
  7. **CRM**: Leads, Opportunities, Campaigns
  8. **HR**: Employees, Attendance, Payroll, Leave
  9. **Assets**: Asset Management, Depreciation
  10. **Support**: Issues, Tickets, SLA tracking

- **Features**:
  - Automatic DocType discovery
  - DocType link relationship mapping
  - Permission-aware queries
  - Child table support
  - Virtual fields and computed columns
  - Direct SQL access to all tables

---

## Intelligence Dashboards

Pre-built, domain-specific intelligence dashboards:

### 1. **Financial Intelligence**
*Route: `/financial-intelligence`*

#### Summary Cards
- Net Profit (YTD)
- Cash Position
- Outstanding AR (Accounts Receivable)
- Outstanding AP (Accounts Payable)
- Net VAT Payable
- Forex Exposure

#### Tabs & Features
- **Overview**: P&L Summary, Revenue, Expenses, Net Profit, Margin %
- **Cash Flow**: Cash flow analysis with inflows/outflows
- **Tax Compliance**: KRA iTax integration (Kenya-specific), 16% VAT tracking
- **Receivables**: DSO (Days Sales Outstanding) analysis, aging reports
- **Payables**: DPO (Days Payable Outstanding) tracking
- **KRA iTax**: Tax liability, installments, effective tax rate
- **Forex**: Multi-currency exposure tracking

### 2. **Sales Intelligence**
*Route: `/sales-intelligence`*

#### Summary Cards
- Total Revenue
- Growth % (YoY, MoM)
- Transaction Count
- Average Order Value

#### Tabs & Features
- **Revenue Overview**: Revenue metrics with date range filters (7d, 30d, 90d, 12m, 24m)
- **Cash vs Credit**: Payment mix analysis
- **Sales Reps**: Performance tracking by sales representative
- **Breakdown**: Revenue by customer, product, territory, channel
- **Margins**: Gross margin, contribution margin analysis
- **Forecasts**: ML-powered dimensional forecasting by product groups/territories

### 3. **Inventory Intelligence**
*Route: `/inventory-intelligence`*

#### Tabs & Features
- **Stock Overview**: SKU analysis across warehouses, stock value
- **Turnover**: Inventory turnover metrics, slow-moving items
- **ABC/XYZ Classification**: ML-based classification
  - ABC: Based on value (A = high value, B = medium, C = low)
  - XYZ: Based on demand variability (X = stable, Y = variable, Z = erratic)
- **Aging (FIFO)**: Stock aging analysis, dead stock identification
- **Warehouses & Transfers**: Inter-warehouse movement, transfer recommendations
- **Procurement**: Demand planning, reorder point suggestions

### 4. **Procurement Intelligence**
*Route: `/procurement-intelligence`*

#### Summary Cards
- Total Spend (12M rolling)
- Active Suppliers
- Average Lead Time
- On-Time Delivery %
- Pending POs
- Supplier Risk Score

#### Tabs & Features
- **Spend Overview**: Monthly spend trend, spend by category
- **Supplier Performance**: Top suppliers by spend, delivery performance, quality metrics, risk scoring (0-100)

### 5. **Customer Intelligence**
*Route: `/customer-intelligence`*

#### Tabs & Features
- **Overview**: Customer base summary, segmentation distribution
- **Customers**: Individual customer metrics
- **Geography**: Geographic revenue distribution
- **Actions**: Next best action recommendations
- **Cohorts**: Cohort retention analysis
- **Cross-sell**: Cross-sell opportunity identification
- **Patterns**: Purchase pattern analysis

#### Customer Segmentation
- **CLV Tiering** (Customer Lifetime Value):
  - 💎 Diamond: Top 1% customers
  - 🏆 Platinum: Top 5% customers
  - 🥇 Gold: Top 20% customers
  - 🥈 Silver: Top 50% customers
  - 🥉 Bronze: Remaining customers

- **RFM Segmentation** (Recency, Frequency, Monetary):
  - Champions: High RFM scores
  - Loyal Customers: Frequent buyers
  - Potential Loyalists: Recent, moderate spenders
  - At Risk: Low recency, high historic value
  - Can't Lose Them: Churning high-value customers
  - Hibernating: Long time since purchase
  - Lost: Inactive customers

### 6. **Customer 360 View**
*Route: `/customer-360` & `/customer/:customerId`*

Individual customer deep-dive:
- **Profile Information**: Contact, location, tier, segment
- **Purchase History**: Timeline of all transactions
- **CLV Analysis**: Lifetime value breakdown
- **Cross-sell Recommendations**: ML-powered product suggestions
- **Risk Assessment**: Churn probability, payment risk
- **Interaction History**: Support tickets, communications

### 7. **Risk Intelligence**
*Route: `/risk-intelligence`*

#### Summary Cards
- Overall Risk Score (0-100)
- Credit Risk
- Cash Flow Risk
- Operational Risk
- Compliance Risk
- Active Alerts

#### Features
- **Risk Assessment Matrix**: Impact vs Probability visualization
- **Active Alerts**: Real-time risk alerts with severity levels
- **Prophet Forecasting**: Time-series forecasting for early warnings
- **Key Metrics**: Business metrics with threshold monitoring

### 8. **Tax Intelligence** (Kenya KRA-Focused)
*Route: `/tax-intelligence`*

Kenya-specific tax compliance features:

- **Taxable Income & Tax Liability**: Corporate tax computation (30% rate)
- **Effective Tax Rate**: Actual tax rate vs statutory rate
- **Quarterly Installments**: Quarterly corporate tax payment tracking
- **Capital Allowances**: Depreciation and capital allowances
- **Expense Classification**:
  - Allowable expenses (deductible)
  - Non-allowable expenses (non-deductible)
- **VAT Tracking**: 16% VAT on sales/purchases
- **iTax Integration**: KRA iTax portal compliance

### 9. **Strategic Finance Intelligence**
*Route: `/strategic-finance-intelligence`*

Executive-level financial planning:

#### Tabs
1. **Executive Summary**: YTD Revenue, Expenses, Net Income, Cash Position, Working Capital, DSO, Gross Margin
2. **Cash Forecasting**: Forward-looking cash projections
3. **13-Week Cash Flow**: Rolling weekly forecast
   - Inflows/Outflows tracking
   - Minimum balance alerts
   - Threshold warnings
   - Scenario analysis
   - Variance analysis
   - Payroll detection
4. **Capital Planning**: CapEx planning and ROI analysis
5. **Working Capital**: Working capital management and optimization
6. **Financial Ratios**: Key ratio trends (liquidity, profitability, efficiency)
7. **Scenario Analysis**: Sensitivity analysis & Monte Carlo simulation
8. **Period Comparison**: Period-over-period variance analysis
9. **Budget**: Budget planning and variance tracking

---

## AI & Machine Learning Features

### 1. **AI Insights Module**
*Route: `/ai-insights`*

Conversational AI interface for business insights:

#### Features
- **Chat-Based Interface**: Ask questions in natural language
- **Multi-Module Insights**: Financial, Sales, Procurement, Inventory, Production, Customer
- **Complexity Levels**:
  - Simple: Quick metrics and summaries
  - Advanced: Deep analysis with ML models
- **Context-Aware**: Understands business domain and data structure
- **Model Status Tracking**: Monitor ML model training status
- **OpenRouter Integration**: Uses free-tier LLMs (Llama, GPT, Gemini, Qwen, Mistral, Hermes)

#### Supported AI Models
1. `meta-llama/llama-3.3-70b-instruct:free` (Default)
2. `openai/gpt-oss-120b:free`
3. `google/gemini-2.0-flash-exp:free`
4. `qwen/qwen3-235b-a22b:free`
5. `mistralai/mistral-small-3.1-24b-instruct:free`
6. `nousresearch/hermes-3-llama-3.1-405b:free`

#### Example Queries
- "What were my top 5 customers last month?"
- "Show me inventory items that are low in stock"
- "What's my cash flow projection for next quarter?"
- "Which products have the highest profit margin?"
- "Identify customers at risk of churning"

### 2. **Dashboard Chat Assistant**

Floating AI chat button on all dashboards:

- **Context-Aware**: Understands current dashboard context
- **Session Management**: Maintains conversation history
- **Quick Suggestions**: Pre-built question prompts per dashboard type
- **Real-Time Insights**: Answers based on live dashboard data

### 3. **Machine Learning Models**

Six trained ML models for predictive analytics:

#### Customer Segmentation Model
- **Purpose**: RFM segmentation and CLV calculation
- **Algorithm**: K-Means clustering
- **Training Schedule**: Daily
- **Outputs**: Customer segments, tier assignments, churn probability

#### ABC/XYZ Classification Model
- **Purpose**: Inventory classification
- **Algorithm**: Value-based (ABC) + Demand variability (XYZ)
- **Training Schedule**: Weekly
- **Outputs**: 9 categories (A/B/C × X/Y/Z)

#### Sales Forecasting Model
- **Purpose**: Predict future sales
- **Algorithm**: Prophet (Facebook Time Series)
- **Training Schedule**: Daily
- **Outputs**: 30/60/90-day forecasts, confidence intervals

#### Payment Prediction Model
- **Purpose**: Predict payment delays
- **Algorithm**: Random Forest Classifier
- **Training Schedule**: Daily
- **Outputs**: Payment delay probability, expected payment date

#### Demand Forecasting Model
- **Purpose**: Predict product demand
- **Algorithm**: ARIMA / Prophet
- **Training Schedule**: Weekly
- **Outputs**: Item-level demand forecast, safety stock recommendations

#### Product Recommendations Model
- **Purpose**: Cross-sell and upsell recommendations
- **Algorithm**: Collaborative filtering + Association rules
- **Training Schedule**: Weekly
- **Outputs**: Product affinity matrix, top 10 recommendations per customer

### 4. **AI Agents**

Specialized AI agents for domain-specific analysis:

- **Sales Agent**: Sales performance, forecasting, customer insights
- **Risk Agent**: Risk assessment, early warning signals
- **Inventory Agent**: Stock optimization, reorder planning
- **Procurement Agent**: Supplier analysis, spend optimization
- **Financial Agent**: Financial analysis, cash flow management
- **Customer Agent**: Customer behavior, churn prediction
- **Tax Agent**: Tax compliance, optimization strategies
- **Query Router**: Intelligently routes questions to appropriate agent

### 5. **AI Configuration**

#### Settings (Insights Settings DocType)
- **Enable AI Analytics**: Master toggle
- **OpenRouter API Key**: Required for AI features (get from https://openrouter.ai/keys)
- **Primary AI Model**: Main model for queries
- **Fallback AI Model**: Backup if primary fails
- **Auto Refresh Schedule**: Daily/Weekly/Monthly
- **Daily AI Quota**: Request limit (default: 100)
- **Quota Used Today**: Current usage tracker (resets daily)

---

## Query System

### Query Types

#### 1. Visual Query Builder

**Step-by-Step Process:**

1. **Select Data Source**: Choose database connection
2. **Select Tables**: Add tables to query
3. **Define Joins**:
   - Auto-detected relationships (for Frappe DB)
   - Manual join configuration (column = column)
   - Join types: INNER, LEFT, RIGHT, FULL OUTER
4. **Select Columns**: Drag columns to result set
5. **Add Calculations**:
   - Formulas: `[column1] + [column2]`
   - Functions: `IF(condition, true_value, false_value)`
   - Aggregations: `SUM([amount])`, `AVG([price])`
6. **Apply Filters**:
   - Operators: `=`, `!=`, `>`, `<`, `>=`, `<=`, `IN`, `NOT IN`, `LIKE`, `BETWEEN`
   - Combine with AND/OR logic
   - Filter on raw or aggregated values
7. **Group By**: Group results by dimensions
8. **Sort**: Order by columns (ASC/DESC)
9. **Limit**: Limit result rows

**Example Use Case:**
```
Query: "Top 10 customers by revenue in 2024"

Tables: Sales Invoice, Customer
Join: Sales Invoice.customer = Customer.name
Columns: Customer.customer_name, SUM(Sales Invoice.grand_total) AS total_revenue
Filters: Sales Invoice.posting_date >= '2024-01-01'
Group By: Customer.customer_name
Sort: total_revenue DESC
Limit: 10
```

#### 2. Native SQL

Write raw SQL for complex queries:

```sql
-- Advanced sales analysis with window functions
SELECT
    customer_name,
    grand_total,
    posting_date,
    SUM(grand_total) OVER (
        PARTITION BY customer_name
        ORDER BY posting_date
    ) AS running_total,
    ROW_NUMBER() OVER (
        PARTITION BY MONTH(posting_date)
        ORDER BY grand_total DESC
    ) AS monthly_rank
FROM `tabSales Invoice`
WHERE posting_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
ORDER BY posting_date DESC;
```

**Features:**
- Full SQL support (database-dependent)
- Parameter binding: `{{ parameter_name }}`
- Syntax highlighting
- Query formatting
- Execution history

#### 3. Script Query (Python)

Use Python with Ibis framework:

```python
# Calculate customer lifetime value
from ibis import _

# Load tables
invoices = table('Sales Invoice')
customers = table('Customer')

# Join and aggregate
result = (
    invoices
    .join(customers, invoices.customer == customers.name)
    .group_by(customers.customer_name)
    .aggregate(
        total_revenue=invoices.grand_total.sum(),
        order_count=invoices.count(),
        avg_order_value=invoices.grand_total.mean(),
        first_order=invoices.posting_date.min(),
        last_order=invoices.posting_date.max()
    )
    .mutate(
        days_as_customer=(_.last_order - _.first_order).total_seconds() / 86400,
        clv=_.total_revenue * 1.2  # Simple CLV multiplier
    )
    .order_by(_.clv.desc())
)

return result
```

#### 4. AI-Assisted Query

Describe what you want in natural language:

**Input:** "Show me customers who haven't purchased in the last 90 days but have a lifetime value over $10,000"

**Generated SQL:**
```sql
SELECT
    c.customer_name,
    SUM(si.grand_total) AS lifetime_value,
    MAX(si.posting_date) AS last_purchase_date,
    DATEDIFF(CURDATE(), MAX(si.posting_date)) AS days_since_purchase
FROM `tabCustomer` c
LEFT JOIN `tabSales Invoice` si ON si.customer = c.name
GROUP BY c.customer_name
HAVING
    lifetime_value > 10000
    AND days_since_purchase > 90
ORDER BY lifetime_value DESC;
```

### Query Features

- **Auto-Save**: Queries save automatically
- **Versioning**: Track query changes over time
- **Sharing**: Share queries with teams or publicly
- **Scheduling**: Schedule queries to run automatically
- **Export**: Export results to CSV, Excel, JSON
- **Caching**: Results cached for configurable duration (default: 10 min)
- **Result Limit**: Configurable row limit (default: 1000)
- **Parameters**: Dynamic queries with user input parameters
- **Charts**: Visualize query results with 13+ chart types

---

## Data Warehouse

### Overview

Built-in data warehouse powered by **DuckDB** with **Parquet** storage format.

### Why Use Data Warehouse?

1. **Performance**: Orders of magnitude faster than querying remote databases
2. **Offline Analytics**: Access data even if source system is down
3. **Data Transformation**: Pre-process and clean data before analysis
4. **Reduced Load**: Minimize load on production databases
5. **Historical Analysis**: Keep snapshots of data over time

### Storage Architecture

```
/private/files/insights_data_warehouse/
├── insights.duckdb                    # Main DuckDB database
├── site_db.customer.parquet          # Parquet files per table
├── site_db.sales_invoice.parquet
├── postgres_prod.orders.parquet
└── bigquery_analytics.events.parquet
```

### Import Process

#### Full Sync
1. Connect to source database
2. Execute SELECT query on source table
3. Fetch data in batches (memory-aware)
4. Convert to Parquet format
5. Store in warehouse
6. Update table metadata

#### Incremental Sync (FIFO)
1. Check last sync bookmark (primary key value)
2. Fetch only new/updated records
3. Merge with existing Parquet file
4. Update bookmark

#### Configuration

**Per Table Settings** (Insights Table v3):
- `row_limit`: Max rows to import (default: 1,000,000)
- `before_import_script`: Python script to transform data before import
- `stored`: Flag indicating if table is in warehouse

**Global Settings** (Insights Settings):
- `enable_data_store`: Master toggle
- `max_records_to_sync`: Default row limit
- `max_memory_usage`: Memory limit in MB (default: 512)
- `max_execution_time`: Query timeout in seconds

#### Import API

```python
# Trigger manual import
frappe.call('insights.api.data_store.import_table', {
    'data_source': 'Site DB',
    'table': 'Sales Invoice'
})

# Check import status
frappe.call('insights.api.data_store.get_import_status', {
    'data_source': 'Site DB',
    'table': 'Sales Invoice'
})
```

#### Scheduled Sync

**Daily Sync** (all enabled tables):
- Scheduler task: `insights.api.data_store.sync_tables`
- Time: Runs daily at configured time
- Process: Iterates all tables with `stored=1`, triggers incremental sync

**Manual Sync**:
- Click "Import to Data Store" on any table
- Background job processes import
- Progress visible in Insights Table Import Log

### Import Logs

**DocType:** Insights Table Import Log

**Fields:**
- `data_source`: Source name
- `table_name`: Table being imported
- `status`: In Progress, Completed, Failed
- `rows_imported`: Total rows imported
- `batch_size`: Calculated batch size
- `row_size`: Average row size in KB
- `memory_limit`: Configured memory limit
- `row_limit`: Configured row limit
- `started_at`: Start timestamp
- `ended_at`: End timestamp
- `time_taken`: Duration in seconds
- `parquet_file`: Path to Parquet file
- `query`: SQL query used for import
- `log`: Detailed import log

---

## API Endpoints

### Authentication

All API endpoints require authentication:
- **Session-based**: Login via Frappe session
- **API Key/Secret**: Use Frappe API token authentication

### Core API Modules

#### 1. Data Source API
*Module: `insights.api.data_sources`*

```python
# List all data sources
GET /api/method/insights.api.data_sources.get_data_sources

# Create data source
POST /api/method/insights.api.data_sources.create_data_source
{
    "title": "My PostgreSQL",
    "database_type": "PostgreSQL",
    "host": "localhost",
    "port": 5432,
    ...
}

# Test connection
POST /api/method/insights.api.data_sources.test_connection
{
    "data_source": "My PostgreSQL"
}

# Get table list
GET /api/method/insights.api.data_sources.get_table_list?data_source=Site DB

# Get table columns
GET /api/method/insights.api.data_sources.get_table_columns?data_source=Site DB&table=Customer

# Get column values (for filters)
GET /api/method/insights.api.data_sources.get_column_values?data_source=Site DB&table=Customer&column=territory

# Import CSV
POST /api/method/insights.api.data_sources.import_csv
{
    "file_url": "/files/data.csv",
    "table_name": "imported_data"
}
```

#### 2. Query API
*Module: `insights.api.queries`*

```python
# List queries
GET /api/method/insights.api.queries.get_queries

# Create query
POST /api/method/insights.api.queries.create_query
{
    "title": "Top Customers",
    "data_source": "Site DB"
}

# Execute query
POST /api/method/insights.api.queries.execute_query
{
    "query": "query-name"
}

# Get query results
GET /api/method/insights.api.queries.get_query_results?query=query-name

# Export results
GET /api/method/insights.api.queries.export_query?query=query-name&format=csv
```

#### 3. Dashboard API
*Module: `insights.api.dashboards`*

```python
# List dashboards
GET /api/method/insights.api.dashboards.get_dashboards

# Get dashboard
GET /api/method/insights.api.dashboards.get_dashboard?name=dashboard-name

# Update dashboard layout
POST /api/method/insights.api.dashboards.update_dashboard_layout
{
    "dashboard": "dashboard-name",
    "items": [...]
}

# Duplicate dashboard
POST /api/method/insights.api.dashboards.duplicate_dashboard
{
    "dashboard": "dashboard-name"
}
```

#### 4. Data Store API
*Module: `insights.api.data_store`*

```python
# List warehouse tables
GET /api/method/insights.api.data_store.get_warehouse_tables

# Import table to warehouse
POST /api/method/insights.api.data_store.import_table
{
    "data_source": "Site DB",
    "table": "Sales Invoice"
}

# Sync all tables (scheduled)
POST /api/method/insights.api.data_store.sync_tables

# Get import status
GET /api/method/insights.api.data_store.get_import_status?data_source=Site DB&table=Sales Invoice
```

#### 5. ML API
*Module: `insights.api.ml`*

```python
# Get ML model status
GET /api/method/insights.api.ml.get_ml_status

# Run all ML models (caution: resource intensive)
POST /api/method/insights.api.ml.run_all_models

# Customer Intelligence APIs
GET /api/method/insights.api.ml.get_customer_segments
GET /api/method/insights.api.ml.get_customer_clv_tiers
GET /api/method/insights.api.ml.get_rfm_segmentation
GET /api/method/insights.api.ml.predict_customer_churn

# Sales Intelligence APIs
GET /api/method/insights.api.ml.get_sales_forecast
GET /api/method/insights.api.ml.get_revenue_trends
GET /api/method/insights.api.ml.get_sales_rep_performance

# Inventory Intelligence APIs
GET /api/method/insights.api.ml.get_abc_xyz_classification
GET /api/method/insights.api.ml.get_inventory_turnover
GET /api/method/insights.api.ml.predict_stockouts
GET /api/method/insights.api.ml.get_reorder_recommendations

# Procurement Intelligence APIs
GET /api/method/insights.api.ml.get_supplier_performance
GET /api/method/insights.api.ml.calculate_supplier_risk_score
GET /api/method/insights.api.ml.get_spend_analysis

# Financial Intelligence APIs
GET /api/method/insights.api.ml.get_financial_ratios
GET /api/method/insights.api.ml.get_cash_flow_forecast
GET /api/method/insights.api.ml.get_working_capital_metrics

# Risk Intelligence APIs
GET /api/method/insights.api.ml.calculate_overall_risk_score
GET /api/method/insights.api.ml.get_risk_alerts
GET /api/method/insights.api.ml.predict_payment_delays

# Tax Intelligence APIs
GET /api/method/insights.api.ml.calculate_corporate_tax
GET /api/method/insights.api.ml.get_tax_liability
GET /api/method/insights.api.ml.classify_expenses
```

#### 6. AI Insights API
*Module: `insights.api.ai_insights`*

```python
# Get AI insights
POST /api/method/insights.api.ai_insights.get_ai_insights
{
    "query": "What were my top customers last month?",
    "module": "selling",
    "complexity": "simple"
}

# Get dashboard context for AI
GET /api/method/insights.api.ai_insights.get_dashboard_context?dashboard_type=sales

# Get business intelligence by module
GET /api/method/insights.api.ai_insights.get_business_intelligence?module=accounts&from_date=2024-01-01&to_date=2024-12-31
```

#### 7. Dashboard Chat API
*Module: `insights.api.dashboard_chat`*

```python
# Start chat session
POST /api/method/insights.api.dashboard_chat.start_session
{
    "dashboard_type": "sales_intelligence"
}

# Send message
POST /api/method/insights.api.dashboard_chat.send_message
{
    "session_id": "session-123",
    "message": "Show me top products"
}

# Get chat history
GET /api/method/insights.api.dashboard_chat.get_history?session_id=session-123

# Get quick actions
GET /api/method/insights.api.dashboard_chat.get_quick_actions?dashboard_type=sales_intelligence
```

---

## Configuration & Settings

### Insights Settings (Single DocType)

Access: **Insights > Settings**

#### Onboarding
- `setup_complete`: Whether initial setup is complete
- `onboarding_complete`: Whether onboarding wizard is complete

#### Permissions
- `enable_permissions`: Enable row-level permissions
- `apply_user_permissions`: Apply Frappe user permissions to queries

#### Query Configuration
- `auto_execute_query`: Auto-execute queries on load
- `query_result_expiry`: Cache duration in minutes (default: 10)
- `query_result_limit`: Max rows per query (default: 1000)
- `allow_subquery`: Allow subqueries in SQL

#### Calendar Settings
- `fiscal_year_start`: Fiscal year start date
- `week_starts_on`: First day of week (Monday-Sunday)

#### Data Store
- `enable_data_store`: Enable warehouse feature
- `max_records_to_sync`: Default import row limit
- `max_memory_usage`: Memory limit in MB (default: 512)
- `max_execution_time`: Query timeout in seconds

#### Integrations
- `telegram_api_token`: Telegram bot token for alerts
- `allowed_origins`: CORS whitelist for embedding (comma-separated URLs)

#### AI Analytics
- `enable_ai_analytics`: Master toggle for AI features
- `openrouter_api_key`: OpenRouter API key (get from https://openrouter.ai/keys)
- `ai_model`: Primary AI model
  - Options: Llama 3.3 70B, GPT OSS 120B, Gemini 2.0 Flash, Qwen3 235B, Mistral Small 3.1, Hermes 3 405B
- `ai_model_fallback`: Fallback model if primary fails
- `refresh_schedule`: Auto-refresh (Disabled, Daily, Weekly, Monthly)
- `last_ai_refresh`: Last AI refresh timestamp
- `daily_ai_quota`: Daily API request limit (default: 100)
- `ai_quota_used`: Current day usage (resets daily)

---

## User Roles & Permissions

### Built-in Roles

#### 1. **Insights Admin**
- Full access to all features
- Can create/edit/delete data sources
- Can manage users and permissions
- Can configure settings
- Can access all dashboards and queries

#### 2. **Insights User**
- Can create and edit own queries/dashboards
- Can view shared queries/dashboards
- Cannot manage data sources
- Cannot change settings
- Read-only access to shared resources

#### 3. **System Manager**
- All Insights Admin permissions
- Plus system-level configuration

### Permission System

#### Team-Based Permissions
- **Insights Team** DocType manages team membership
- Resources (queries, dashboards, data sources) can be assigned to teams
- Users inherit access from team membership

#### Row-Level Permissions
When `enable_permissions = 1`:
- Queries automatically filtered by user permissions
- Uses Frappe's User Permission system
- Example: User with permission for "Territory = North" only sees North data

#### Sharing
- **Private**: Only creator can access
- **Team**: Team members can access
- **Public**: Anyone with link can access (read-only)

---

## Getting Started

### Installation

#### Prerequisites
- Frappe Framework v14 or v15
- Python 3.10+
- Node.js 18+
- MariaDB 10.6+ or PostgreSQL 12+

#### Install Insights App

```bash
# Get the app
bench get-app insights https://github.com/frappe/insights

# Install on site
bench --site your-site.local install-app insights

# Build frontend assets
bench build --app insights

# Restart
bench restart
```

### Initial Setup

1. **Access Insights**
   - Navigate to: `http://your-site.local/insights`
   - Or click "Insights" in app launcher

2. **Setup Wizard**
   - First-time setup walks through:
     - Data source configuration
     - Sample dashboard creation
     - AI analytics setup (optional)

3. **Configure Site DB**
   - Automatically created data source pointing to your Frappe site database
   - Provides access to all DocTypes

### Quick Start Guide

#### 1. Create Your First Query

**Visual Query:**
1. Go to: Insights > Query > New Query
2. Select data source: "Site DB"
3. Add table: "Sales Invoice"
4. Select columns: customer_name, grand_total, posting_date
5. Add filter: posting_date >= "2024-01-01"
6. Click "Run"

**SQL Query:**
1. Go to: Insights > Query > New Query
2. Switch to "SQL" mode
3. Write query:
   ```sql
   SELECT customer_name, SUM(grand_total) as total
   FROM `tabSales Invoice`
   WHERE posting_date >= '2024-01-01'
   GROUP BY customer_name
   ORDER BY total DESC
   LIMIT 10
   ```
4. Click "Run"

#### 2. Create a Chart

1. After running query, click "Visualize"
2. Select chart type (e.g., Bar Chart)
3. Configure:
   - X-axis: customer_name
   - Y-axis: total
4. Customize colors, labels, title
5. Save

#### 3. Build a Dashboard

1. Go to: Insights > Dashboard > New Dashboard
2. Enter title: "Sales Overview"
3. Click "Add Widget"
4. Select saved chart or create new
5. Resize and position widgets by dragging
6. Add filters for interactivity
7. Save dashboard

#### 4. Enable AI Analytics (Optional)

1. Get free API key from https://openrouter.ai/keys
2. Go to: Insights > Settings
3. Enable "Enable AI Analytics"
4. Paste API key in "OpenRouter API Key"
5. Select primary model (default: Llama 3.3 70B)
6. Save
7. Navigate to: Insights > AI Insights
8. Start asking questions!

### Connecting External Databases

#### PostgreSQL Example

1. Go to: Insights > Data Source > New Data Source
2. Fill in:
   - **Title**: Production PostgreSQL
   - **Database Type**: PostgreSQL
   - **Host**: db.example.com
   - **Port**: 5432
   - **Database Name**: production_db
   - **Schema**: public
   - **Username**: insights_user
   - **Password**: ********
   - **Use SSL**: ✅
3. Click "Test Connection"
4. If successful, click "Save"
5. Click "Sync Tables" to discover tables
6. Start querying!

---

## FAQ

### General Questions

**Q: Is Frappe Insights free?**
A: Yes, Insights is open-source under GPLv3 license. Free to use, modify, and distribute.

**Q: Does Insights work without ERPNext?**
A: Yes! While it integrates deeply with ERPNext, Insights works standalone with any supported database.

**Q: Can I use Insights in production?**
A: Yes, Insights is production-ready and used by many organizations worldwide.

**Q: What's the difference between Insights v2 and v3?**
A: v3 is a complete rewrite with improved performance, better UX, AI features, and data warehouse.

### Data Sources

**Q: How many data sources can I connect?**
A: Unlimited. You can connect as many data sources as needed.

**Q: Can I query across multiple data sources in a single query?**
A: Not directly in SQL. Use the data warehouse to import tables from different sources, then query the warehouse.

**Q: Does Insights support real-time data?**
A: Queries fetch real-time data from source databases. For warehouse, sync frequency determines freshness.

**Q: How do I connect to Amazon RDS PostgreSQL?**
A: Use PostgreSQL database type, enter RDS endpoint as host, enable SSL.

**Q: Can I connect to Google Sheets?**
A: Not directly. Export to CSV and import via DuckDB HTTP data source.

### Performance

**Q: My queries are slow. How to improve performance?**
A:
1. Use the data warehouse for large tables
2. Add indexes on source database
3. Use aggregations instead of fetching all rows
4. Enable query result caching
5. Limit result rows

**Q: How much data can the data warehouse handle?**
A: DuckDB can handle billions of rows. Practical limit depends on disk space and query complexity.

**Q: Does Insights slow down my production database?**
A:
- Direct queries: Minimal impact with proper indexing
- Warehouse sync: Runs as background job, configurable memory/time limits
- Recommendation: Use database replicas for analytics

### AI Features

**Q: Do I need to pay for AI features?**
A: OpenRouter offers free-tier models (Llama, Gemini, etc.). No payment required for basic usage.

**Q: How accurate are ML predictions?**
A: Accuracy depends on data quality and quantity. Models improve with more historical data.

**Q: Can I use custom ML models?**
A: Currently, only built-in models are supported. Custom model support is planned.

**Q: Does AI send my data to external servers?**
A: Only query metadata and aggregate statistics are sent to OpenRouter. Raw data stays on your server.

### Security & Privacy

**Q: Is my data secure?**
A: Yes. Insights runs entirely on your infrastructure. Database credentials encrypted. HTTPS recommended.

**Q: Can I restrict user access to specific data?**
A: Yes, using:
1. Team-based permissions
2. Row-level permissions (User Permissions)
3. Query-level sharing controls

**Q: Does Insights support SSO?**
A: Yes, through Frappe's built-in SSO support (SAML, OAuth, LDAP).

### Customization

**Q: Can I customize dashboard themes?**
A: Basic theming available. Advanced customization requires CSS modifications.

**Q: Can I add custom widgets?**
A: Yes, by extending the widget system in code. Documentation coming soon.

**Q: Can I embed dashboards in my website?**
A: Yes:
1. Add your domain to "Allowed Origins" in Settings
2. Use iframe: `<iframe src="https://your-site.local/insights/dashboard/dashboard-name">`

### Troubleshooting

**Q: "Permission Denied" error when running query**
A:
- Check if you have access to the data source
- Check if enable_permissions is on and you have user permissions
- Contact Insights Admin

**Q: Data warehouse import fails**
A:
- Check import log for errors
- Increase max_memory_usage if out-of-memory
- Reduce row_limit for large tables
- Check source database connectivity

**Q: AI quota exceeded**
A:
- Wait until daily reset (midnight)
- Increase daily_ai_quota in Settings
- Use AI sparingly for complex queries only

**Q: Charts not displaying**
A:
- Ensure query returns data
- Check if columns are properly mapped to axes
- Clear browser cache
- Check browser console for errors

---

## Troubleshooting

### Common Issues

#### 1. **Connection Timeout**

**Symptoms:** "Connection timeout" when testing data source

**Solutions:**
- Verify host and port are correct
- Check firewall rules allow connection
- For cloud databases, whitelist your server IP
- Test connection using command-line tools (psql, mysql)

#### 2. **Out of Memory During Import**

**Symptoms:** Import fails with "Out of memory" error

**Solutions:**
- Reduce `max_memory_usage` in Settings
- Reduce `row_limit` for the specific table
- Split large tables into multiple smaller imports
- Increase server RAM

#### 3. **Query Execution Timeout**

**Symptoms:** "Query exceeded max execution time"

**Solutions:**
- Increase `max_execution_time` in Settings
- Optimize query (add indexes, reduce joins)
- Use warehouse instead of direct query
- Break into multiple smaller queries

#### 4. **AI Not Responding**

**Symptoms:** AI Insights returns no response or errors

**Solutions:**
- Verify OpenRouter API key is valid
- Check internet connectivity
- Verify AI quota not exceeded
- Try fallback model
- Check browser console for errors

#### 5. **Dashboard Widgets Not Loading**

**Symptoms:** Blank widgets or infinite loading

**Solutions:**
- Check if underlying queries are valid
- Verify data source is active
- Clear query result cache
- Check browser console for errors
- Verify queries return data

### Debug Mode

Enable debug mode for detailed logs:

```python
# In site_config.json
{
    "developer_mode": 1,
    "logging": 2
}
```

Then check logs:
```bash
tail -f logs/frappe.log
```

### Support Channels

- **GitHub Issues**: https://github.com/frappe/insights/issues
- **Frappe Forum**: https://discuss.frappe.io
- **Documentation**: https://docs.frappe.io/insights
- **Community Chat**: Frappe Discord

---

## Roadmap

### Upcoming Features

#### Q1 2025
- ✅ AI-powered insights (Completed)
- ✅ ML models for customer/sales/inventory (Completed)
- 🚧 ERP connector framework (In Progress)
  - Business Central connector
  - SAP OData connector
  - Tally ERP connector
- 🚧 Scheduled alerts via email/Telegram
- 📝 Collaborative notebooks

#### Q2 2025
- 📝 Custom ML model upload
- 📝 Advanced embedding options
- 📝 White-label branding
- 📝 Mobile app (iOS/Android)
- 📝 Workflow automation

#### Q3 2025
- 📝 Streaming data sources (Kafka, Kinesis)
- 📝 Graph database support (Neo4j)
- 📝 Advanced NLP for query generation
- 📝 Multi-tenancy support
- 📝 Marketplace for dashboards/queries

#### Q4 2025
- 📝 Federated queries across sources
- 📝 Version control for queries/dashboards
- 📝 A/B testing framework
- 📝 Advanced forecasting models
- 📝 Regulatory compliance reports

### Feature Requests

Submit feature requests:
- GitHub: https://github.com/frappe/insights/issues
- Forum: https://discuss.frappe.io

---

## Database Integration Matrix

| Feature | MariaDB | PostgreSQL | SQLite | DuckDB | BigQuery | ClickHouse | MSSQL | Frappe DB |
|---------|---------|------------|--------|--------|----------|------------|-------|-----------|
| **Read Operations** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Write Operations** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **SSL/TLS** | ✅ | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | ✅ |
| **SSH Tunnel** | ❌ | ❌ | N/A | ❌ | ❌ | ❌ | ❌ | N/A |
| **Schema Discovery** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Table Relationships** | Manual | Manual | Manual | Manual | Manual | Manual | Manual | Auto |
| **Data Warehouse Sync** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Incremental Sync** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HTTP Data Sources** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **JSON Support** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Window Functions** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CTEs (WITH)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Custom Functions** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Appendix

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run Query | `Cmd/Ctrl + Enter` |
| Format SQL | `Cmd/Ctrl + Shift + F` |
| Toggle Sidebar | `Cmd/Ctrl + B` |
| New Query | `Cmd/Ctrl + N` |
| Save | `Cmd/Ctrl + S` |
| Search | `Cmd/Ctrl + K` |

### File Locations

| Resource | Path |
|----------|------|
| Data Warehouse | `/private/files/insights_data_warehouse/` |
| Query Cache | Redis cache |
| Import Logs | `Insights Table Import Log` DocType |
| Settings | `Insights Settings` Single DocType |

### Environment Variables

Set in `site_config.json`:

```json
{
  "insights_enable_profiling": true,
  "insights_cache_ttl": 600,
  "insights_max_concurrent_imports": 3
}
```

### License

Frappe Insights is licensed under **GNU General Public License v3.0**

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ Must disclose source
- ⚠️ License and copyright notice required
- ⚠️ Same license for derivatives

---

## Credits

**Developed by:** Frappe Technologies Pvt. Ltd.
**Contributors:** https://github.com/frappe/insights/graphs/contributors
**Documentation:** Community-maintained
**Last Updated:** January 2025

---

**Need Help?**

- 📧 Email: hello@frappe.io
- 💬 Forum: https://discuss.frappe.io
- 🐛 Bug Reports: https://github.com/frappe/insights/issues
- 📖 Docs: https://docs.frappe.io/insights

**Happy Analyzing! 📊**
