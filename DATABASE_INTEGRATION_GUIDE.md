# Database Integration Guide - Frappe Insights

Complete guide for connecting Insights to various database systems with examples, best practices, and troubleshooting.

---

## Table of Contents

1. [MariaDB / MySQL](#mariadb--mysql)
2. [PostgreSQL](#postgresql)
3. [SQLite](#sqlite)
4. [DuckDB](#duckdb)
5. [Google BigQuery](#google-bigquery)
6. [ClickHouse](#clickhouse)
7. [Microsoft SQL Server](#microsoft-sql-server)
8. [Frappe DB (ERPNext)](#frappe-db-erpnext)
9. [Future: Business Central](#future-business-central)
10. [Future: SAP](#future-sap)
11. [Future: Tally ERP](#future-tally-erp)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## MariaDB / MySQL

### Overview
- **Default Port:** 3306
- **Authentication:** Username/Password
- **SSL:** Supported
- **Use Cases:** ERPNext, WordPress, Magento, general web apps

### Configuration

#### Basic Connection
```json
{
  "title": "Production MySQL",
  "database_type": "MariaDB",
  "host": "localhost",
  "port": 3306,
  "database_name": "my_database",
  "username": "insights_user",
  "password": "secure_password",
  "use_ssl": false
}
```

#### SSL Connection
```json
{
  "title": "Secure MySQL",
  "database_type": "MariaDB",
  "host": "db.example.com",
  "port": 3306,
  "database_name": "production",
  "username": "analytics",
  "password": "********",
  "use_ssl": true
}
```

### User Setup

```sql
-- Create read-only user
CREATE USER 'insights_user'@'%' IDENTIFIED BY 'secure_password';

-- Grant SELECT on all tables in database
GRANT SELECT ON my_database.* TO 'insights_user'@'%';

-- Grant SELECT on specific tables only
GRANT SELECT ON my_database.customers TO 'insights_user'@'%';
GRANT SELECT ON my_database.orders TO 'insights_user'@'%';
GRANT SELECT ON my_database.products TO 'insights_user'@'%';

-- Flush privileges
FLUSH PRIVILEGES;
```

### Performance Optimization

```sql
-- Add indexes for common query patterns
CREATE INDEX idx_customer_created ON customers(created_at);
CREATE INDEX idx_order_date ON orders(order_date);
CREATE INDEX idx_order_customer ON orders(customer_id);

-- Analyze tables for query optimizer
ANALYZE TABLE customers, orders, products;
```

### Connection Troubleshooting

```bash
# Test connection from command line
mysql -h db.example.com -P 3306 -u insights_user -p my_database

# Common issues:
# 1. Firewall blocking port 3306
# 2. User not allowed from host (check user@host in MySQL)
# 3. Database doesn't exist
```

---

## PostgreSQL

### Overview
- **Default Port:** 5432
- **Authentication:** Username/Password, Connection String
- **SSL:** Supported (multiple modes)
- **Use Cases:** Advanced analytics, GIS applications, large-scale data

### Configuration

#### Basic Connection
```json
{
  "title": "PostgreSQL Production",
  "database_type": "PostgreSQL",
  "host": "postgres.example.com",
  "port": 5432,
  "database_name": "analytics_db",
  "schema": "public",
  "username": "insights_ro",
  "password": "********",
  "use_ssl": true
}
```

#### Connection String
```json
{
  "title": "PostgreSQL via Connection String",
  "database_type": "PostgreSQL",
  "connection_string": "postgresql://user:pass@host:5432/database?sslmode=require&sslrootcert=/path/to/ca.crt"
}
```

#### Amazon RDS PostgreSQL
```json
{
  "title": "AWS RDS PostgreSQL",
  "database_type": "PostgreSQL",
  "host": "mydb.abc123.us-east-1.rds.amazonaws.com",
  "port": 5432,
  "database_name": "production",
  "schema": "public",
  "username": "insights",
  "password": "********",
  "use_ssl": true
}
```

### User Setup

```sql
-- Create read-only role
CREATE ROLE insights_ro WITH LOGIN PASSWORD 'secure_password';

-- Grant connect to database
GRANT CONNECT ON DATABASE analytics_db TO insights_ro;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO insights_ro;

-- Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO insights_ro;

-- Grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO insights_ro;

-- For specific schema
GRANT USAGE ON SCHEMA sales_data TO insights_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA sales_data TO insights_ro;
```

### Schema Isolation

PostgreSQL supports multiple schemas per database:

```sql
-- Create schemas for different departments
CREATE SCHEMA finance;
CREATE SCHEMA sales;
CREATE SCHEMA operations;

-- Grant access to specific schemas
GRANT USAGE ON SCHEMA finance TO insights_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA finance TO insights_ro;
```

In Insights configuration:
```json
{
  "schema": "finance"  // Only see finance schema tables
}
```

### Performance Optimization

```sql
-- Create indexes
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_customers_country ON customers(country);

-- Vacuum and analyze for query planner
VACUUM ANALYZE orders;
VACUUM ANALYZE customers;

-- Create materialized view for complex aggregations
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
    DATE(order_date) as sale_date,
    COUNT(*) as order_count,
    SUM(total_amount) as total_sales
FROM orders
GROUP BY DATE(order_date);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW mv_daily_sales;
```

### SSL Modes

```
sslmode=disable      # No SSL (not recommended)
sslmode=allow        # Try SSL, fallback to non-SSL
sslmode=prefer       # Try SSL, fallback if not available (default)
sslmode=require      # Require SSL, no verification
sslmode=verify-ca    # Require SSL, verify CA certificate
sslmode=verify-full  # Require SSL, verify CA and hostname
```

---

## SQLite

### Overview
- **Default Port:** N/A (file-based)
- **Authentication:** File system permissions
- **SSL:** N/A
- **Use Cases:** Local databases, embedded apps, testing

### Configuration

```json
{
  "title": "Local SQLite DB",
  "database_type": "SQLite",
  "database_name": "/path/to/database.db"
}
```

### Use Cases

1. **Import CSV/Excel to SQLite**
```python
import sqlite3
import pandas as pd

# Load CSV
df = pd.read_csv('sales_data.csv')

# Save to SQLite
conn = sqlite3.connect('analytics.db')
df.to_sql('sales', conn, if_exists='replace', index=False)
conn.close()
```

2. **Query SQLite from Insights**
- Point database_name to `/path/to/analytics.db`
- Tables appear automatically

### Limitations

- No concurrent writes (single writer)
- Limited to ~280 TB database size
- No network access (file must be on same server)

---

## DuckDB

### Overview
- **Default Port:** N/A (file-based or in-memory)
- **Authentication:** File permissions, HTTP headers
- **SSL:** For HTTP sources
- **Use Cases:** Analytical queries, Parquet/CSV processing, HTTP data sources

### Configuration

#### Local File
```json
{
  "title": "DuckDB Analytics",
  "database_type": "DuckDB",
  "database_name": "/path/to/analytics.duckdb"
}
```

#### In-Memory
```json
{
  "title": "DuckDB In-Memory",
  "database_type": "DuckDB",
  "database_name": ":memory:"
}
```

#### HTTP Data Source (CSV)
```json
{
  "title": "Public CSV Dataset",
  "database_type": "DuckDB",
  "database_name": "https://raw.githubusercontent.com/user/repo/main/data.csv"
}
```

#### HTTP Data Source (Parquet)
```json
{
  "title": "S3 Parquet Files",
  "database_type": "DuckDB",
  "database_name": "https://my-bucket.s3.amazonaws.com/data/*.parquet",
  "http_headers": {
    "Authorization": "Bearer token123"
  }
}
```

### Use Cases

1. **Query Multiple Parquet Files**
```sql
-- DuckDB can query multiple Parquet files as a single table
SELECT * FROM '/data/sales/2024-*.parquet'
WHERE sale_date >= '2024-01-01';
```

2. **Query CSV from URL**
```sql
SELECT * FROM read_csv_auto('https://example.com/data.csv');
```

3. **Join Local and Remote Data**
```sql
SELECT
    local.customer_name,
    remote.order_count
FROM '/local/customers.parquet' local
JOIN 'https://api.example.com/orders.csv' remote
    ON local.id = remote.customer_id;
```

### Performance Benefits

- **Columnar Storage**: Parquet format optimized for analytics
- **Compression**: Snappy compression reduces storage by 70-90%
- **Vectorized Execution**: SIMD instructions for fast queries
- **No Network Overhead**: Direct file access

---

## Google BigQuery

### Overview
- **Default Port:** N/A (API-based)
- **Authentication:** Service Account JSON
- **SSL:** Always encrypted
- **Use Cases:** Petabyte-scale data warehouse, Google Analytics 360, Firebase

### Prerequisites

1. **Create Service Account** in Google Cloud Console
2. **Grant Permissions**:
   - `BigQuery Data Viewer` (read access)
   - `BigQuery Job User` (run queries)
3. **Download JSON Key**

### Configuration

```json
{
  "title": "BigQuery Analytics",
  "database_type": "BigQuery",
  "bigquery_project_id": "my-project-12345",
  "bigquery_dataset_id": "analytics_dataset",
  "bigquery_service_account_key": {
    "type": "service_account",
    "project_id": "my-project-12345",
    "private_key_id": "abc123...",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMII...\n-----END PRIVATE KEY-----\n",
    "client_email": "insights@my-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
  }
}
```

### Setting Up Service Account

```bash
# Create service account
gcloud iam service-accounts create insights-sa \
    --display-name="Insights Analytics"

# Grant BigQuery Data Viewer role
gcloud projects add-iam-policy-binding my-project-12345 \
    --member="serviceAccount:insights-sa@my-project-12345.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

# Grant BigQuery Job User role
gcloud projects add-iam-policy-binding my-project-12345 \
    --member="serviceAccount:insights-sa@my-project-12345.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=insights-sa@my-project-12345.iam.gserviceaccount.com
```

### Query Optimization

BigQuery is **billed by data processed**, so optimize queries:

```sql
-- ❌ BAD: Scans entire table
SELECT * FROM `project.dataset.large_table`;

-- ✅ GOOD: Limit columns and use partitioning
SELECT customer_id, total
FROM `project.dataset.large_table`
WHERE _PARTITIONTIME >= '2024-01-01'  -- Uses partition pruning
LIMIT 10000;
```

### Cost Management

- Enable **query result caching** in Insights
- Use **clustered tables** in BigQuery
- **Partition** tables by date
- Limit row count in Insights settings

---

## ClickHouse

### Overview
- **Default Port:** 8123 (HTTP), 9000 (Native)
- **Authentication:** Username/Password
- **SSL:** Supported
- **Use Cases:** Real-time analytics, time-series data, log analysis

### Configuration

```json
{
  "title": "ClickHouse Analytics",
  "database_type": "ClickHouse",
  "host": "clickhouse.example.com",
  "port": 8123,
  "database_name": "analytics",
  "username": "insights",
  "password": "********",
  "use_ssl": true
}
```

### User Setup

```sql
-- Create read-only user
CREATE USER insights IDENTIFIED BY 'secure_password';

-- Grant read access to database
GRANT SELECT ON analytics.* TO insights;

-- Read-only access to specific tables
GRANT SELECT ON analytics.events TO insights;
GRANT SELECT ON analytics.users TO insights;
```

### Query Optimization

ClickHouse is optimized for **aggregate queries**:

```sql
-- Efficient aggregation on billion-row table
SELECT
    toDate(event_time) AS date,
    event_type,
    COUNT(*) AS event_count,
    uniq(user_id) AS unique_users
FROM events
WHERE event_time >= today() - 30
GROUP BY date, event_type
ORDER BY date DESC;
```

### Use Cases

1. **Website Analytics**: Page views, user sessions, conversions
2. **IoT Data**: Sensor readings, device telemetry
3. **Application Logs**: Error tracking, performance monitoring
4. **Ad Tech**: Impressions, clicks, conversions

---

## Microsoft SQL Server

### Overview
- **Default Port:** 1433
- **Authentication:** SQL Server Auth, Windows Auth
- **SSL:** Supported
- **Use Cases:** Enterprise Windows environments, Azure SQL

### Configuration

#### SQL Server Authentication
```json
{
  "title": "SQL Server Production",
  "database_type": "Microsoft SQL Server",
  "host": "sqlserver.example.com",
  "port": 1433,
  "database_name": "Sales",
  "username": "insights_user",
  "password": "********",
  "use_ssl": true
}
```

#### Azure SQL Database
```json
{
  "title": "Azure SQL",
  "database_type": "Microsoft SQL Server",
  "host": "myserver.database.windows.net",
  "port": 1433,
  "database_name": "Production",
  "username": "insights@myserver",
  "password": "********",
  "use_ssl": true
}
```

### User Setup

```sql
-- Create login
CREATE LOGIN insights_user WITH PASSWORD = 'SecurePassword123!';

-- Create user in database
USE Sales;
CREATE USER insights_user FOR LOGIN insights_user;

-- Grant read-only access
GRANT SELECT ON SCHEMA::dbo TO insights_user;

-- Or specific tables
GRANT SELECT ON dbo.Customers TO insights_user;
GRANT SELECT ON dbo.Orders TO insights_user;
```

### Performance Optimization

```sql
-- Create indexes
CREATE INDEX idx_orders_date ON Orders(OrderDate);

-- Update statistics
UPDATE STATISTICS Orders;
UPDATE STATISTICS Customers;

-- Create view for complex joins
CREATE VIEW vw_customer_orders AS
SELECT
    c.CustomerID,
    c.CustomerName,
    o.OrderID,
    o.OrderDate,
    o.TotalAmount
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID;

-- Grant access to view
GRANT SELECT ON vw_customer_orders TO insights_user;
```

---

## Frappe DB (ERPNext)

### Overview
- **Default Port:** Automatic (uses site database)
- **Authentication:** Automatic (site credentials)
- **SSL:** Inherits from site
- **Use Cases:** ERPNext, Frappe apps, custom Frappe applications

### Configuration

The "Site DB" data source is **automatically created** when you install Insights.

### Features

#### 1. Automatic DocType Discovery
All ERPNext DocTypes appear as tables:
- `tabCustomer` → Customer
- `tabSales Invoice` → Sales Invoice
- `tabItem` → Item
- etc.

#### 2. Relationship Mapping
Links between DocTypes are auto-detected:
```python
# Frappe knows these relationships:
Sales Invoice → Customer (via customer field)
Sales Invoice Item → Item (via item_code field)
Customer → Territory (via territory field)
```

#### 3. Child Table Support
```sql
-- Parent-child joins work automatically
SELECT
    si.name,
    si.customer,
    si.grand_total,
    sii.item_code,
    sii.qty
FROM `tabSales Invoice` si
JOIN `tabSales Invoice Item` sii ON sii.parent = si.name;
```

#### 4. Virtual Fields
Some computed fields available:
```sql
SELECT
    name,
    customer,
    grand_total,
    outstanding_amount,
    status
FROM `tabSales Invoice`;
```

### ERPNext Module Access

#### Accounts Module
```sql
-- Financial analysis
SELECT
    posting_date,
    account,
    debit,
    credit
FROM `tabGL Entry`
WHERE posting_date >= '2024-01-01'
    AND company = 'Your Company';
```

#### Sales Module
```sql
-- Sales performance
SELECT
    customer,
    SUM(grand_total) AS total_revenue,
    COUNT(*) AS invoice_count,
    AVG(grand_total) AS avg_invoice
FROM `tabSales Invoice`
WHERE docstatus = 1  -- Submitted invoices only
    AND posting_date >= '2024-01-01'
GROUP BY customer
ORDER BY total_revenue DESC;
```

#### Inventory Module
```sql
-- Stock levels
SELECT
    item_code,
    warehouse,
    actual_qty,
    valuation_rate,
    stock_value
FROM `tabStock Ledger Entry`
WHERE is_cancelled = 0;
```

### Using Replica Databases

For **high-traffic sites**, query analytics from a replica:

1. **Set up MySQL replication**
2. **Configure replica in ERPNext**:
```python
# site_config.json
{
    "read_from_replica": 1,
    "replica_host": "replica.example.com"
}
```
3. Insights automatically uses replica for read queries

---

## Future: Business Central

> **Status:** Planned (see [ERP Integration Plan](/Users/mac/.claude/plans/fluffy-stargazing-pancake.md))

### Overview
- **API Type:** OData v4 REST API
- **Authentication:** OAuth2 (Azure AD)
- **Base URL:** `https://api.businesscentral.dynamics.com/v2.0/{tenant}/api/v2.0/`

### Future Configuration (Planned)

```json
{
  "title": "Business Central Production",
  "database_type": "Business Central",
  "api_endpoint": "https://api.businesscentral.dynamics.com/v2.0/production/api/v2.0",
  "oauth_client_id": "abc-123-def",
  "oauth_client_secret": "********",
  "oauth_tenant_id": "tenant-guid",
  "company_id": "CRONUS USA, Inc."
}
```

### Available Entities (Planned)

**Financial:**
- General Ledger Entries
- Accounts
- Trial Balance

**Sales:**
- Sales Invoices
- Sales Orders
- Customers

**Procurement:**
- Purchase Invoices
- Purchase Orders
- Vendors

**Inventory:**
- Items
- Item Categories

---

## Future: SAP

> **Status:** Planned (see [ERP Integration Plan](/Users/mac/.claude/plans/fluffy-stargazing-pancake.md))

### Overview
- **API Type:** OData / REST (S/4HANA), Service Layer (Business One)
- **Authentication:** OAuth2 or Session-based
- **Base URL:** Varies by SAP product

### Future Configuration (Planned)

```json
{
  "title": "SAP Business One",
  "database_type": "SAP OData",
  "api_endpoint": "https://sap-server:50000/b1s/v1",
  "username": "insights",
  "password": "********",
  "company_id": "SBODEMOUS"
}
```

### Available Entities (Planned)

**Financial:**
- Journal Entries
- Chart of Accounts

**Sales:**
- Sales Invoices (Invoices)
- Business Partners (Customers)

**Procurement:**
- Purchase Invoices
- Business Partners (Suppliers)

**Inventory:**
- Items
- Warehouses

---

## Future: Tally ERP

> **Status:** Planned (see [ERP Integration Plan](/Users/mac/.claude/plans/fluffy-stargazing-pancake.md))

### Overview
- **API Type:** XML over HTTP
- **Authentication:** Basic Auth or License-based
- **Default Port:** 9000

### Future Configuration (Planned)

```json
{
  "title": "Tally ERP 9",
  "database_type": "Tally ERP",
  "api_endpoint": "http://localhost:9000",
  "api_key": "********",
  "company_id": "My Company"
}
```

### Available Entities (Planned)

**Financial:**
- Ledgers
- Vouchers (Journal Entries)
- Groups

**Sales:**
- Sales Vouchers
- Sundry Debtors (Customers)

**Procurement:**
- Purchase Vouchers
- Sundry Creditors (Suppliers)

**Inventory:**
- Stock Items
- Stock Groups
- Godowns (Warehouses)

---

## Best Practices

### 1. Security

#### Create Read-Only Users
```sql
-- Never use admin/root accounts
-- Always create dedicated read-only users
GRANT SELECT ON database.* TO 'insights_ro'@'%';
```

#### Use SSL/TLS
```json
{
  "use_ssl": true  // Always enable for production
}
```

#### Restrict Network Access
```bash
# Firewall: Only allow Insights server IP
iptables -A INPUT -p tcp --dport 3306 -s insights-server-ip -j ACCEPT
iptables -A INPUT -p tcp --dport 3306 -j DROP
```

#### Rotate Credentials
- Change database passwords quarterly
- Use password managers
- Never commit credentials to git

### 2. Performance

#### Use Database Replicas
- Analytics queries on replica
- Production writes on primary
- Reduces load on production DB

#### Create Indexes
```sql
-- Index frequently filtered columns
CREATE INDEX idx_created_date ON orders(created_at);
CREATE INDEX idx_customer ON orders(customer_id);
```

#### Use Data Warehouse
- Import large tables to Insights warehouse
- Query warehouse instead of live DB
- Schedule syncs during off-peak hours

#### Limit Result Rows
```python
# In Insights Settings
query_result_limit: 1000  # Don't fetch millions of rows
```

### 3. Data Governance

#### Document Data Sources
```markdown
# Data Source: Production MySQL
- Owner: Data Team
- Update Frequency: Real-time
- Retention: 7 years
- PII: Yes (customer names, emails)
```

#### Implement Row-Level Security
```sql
-- User sees only their region's data
CREATE VIEW vw_regional_sales AS
SELECT * FROM sales
WHERE region = CURRENT_USER();
```

#### Monitor Query Costs
- For BigQuery: Track bytes processed
- For cloud DBs: Monitor compute usage
- Set budget alerts

### 4. Monitoring

#### Log All Queries
```python
# Insights automatically logs:
# - Who ran the query
# - When it was run
# - How long it took
# - How many rows returned
```

#### Set Up Alerts
```python
# Alert if query takes > 60 seconds
# Alert if warehouse sync fails
# Alert if connection drops
```

#### Track Data Freshness
```sql
-- Check last updated timestamp
SELECT MAX(updated_at) FROM orders;
```

---

## Troubleshooting

### Connection Errors

#### "Connection refused"
```bash
# Check if database is running
systemctl status mysql
systemctl status postgresql

# Check if port is open
telnet db.example.com 3306

# Check firewall
sudo ufw status
```

#### "Access denied"
```sql
-- Verify user exists and has permissions
SELECT user, host FROM mysql.user WHERE user = 'insights_user';
SHOW GRANTS FOR 'insights_user'@'%';
```

#### "Unknown database"
```sql
-- List databases
SHOW DATABASES;

-- Check if database exists
SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA;
```

### Performance Issues

#### Slow Queries
```sql
-- Check query execution plan
EXPLAIN SELECT * FROM large_table WHERE ...;

-- Add missing indexes
CREATE INDEX idx_column ON large_table(column);

-- Use warehouse for large tables
-- Import to warehouse and query from there
```

#### High Memory Usage
```python
# Reduce batch size in Insights Settings
max_memory_usage: 256  # Down from 512

# Limit rows per table
row_limit: 100000  # Down from 1M
```

#### Connection Pool Exhausted
```python
# Increase connection pool size in database
max_connections = 200

# Or reduce concurrent queries in Insights
```

### Data Sync Issues

#### Warehouse Import Fails
```python
# Check import log
Insights Table Import Log → View latest failed log

# Common causes:
# 1. Out of memory → Reduce max_memory_usage
# 2. Timeout → Increase max_execution_time
# 3. Connection lost → Check network stability
# 4. Disk full → Free up disk space
```

#### Data Not Refreshing
```python
# Check sync schedule
Insights Settings → enable_data_store = 1

# Manually trigger sync
Data Sources → Site DB → Tables → Select table → Import to Data Store

# Check scheduler is running
bench doctor
```

### Authentication Issues

#### OAuth Token Expired
```python
# For future ERP integrations (BC, SAP)
# Token auto-refreshes hourly
# Check oauth_token_expiry field

# Manual refresh:
Insights Settings → ERP Sync → Refresh Tokens
```

#### Service Account Key Invalid
```json
// For BigQuery
// Download new key from Google Cloud Console
// Replace bigquery_service_account_key
```

---

## Summary Comparison

| Database | Best For | Difficulty | Cost | Scale |
|----------|----------|------------|------|-------|
| **MariaDB** | Web apps, ERPNext | Easy | Free | TB |
| **PostgreSQL** | Advanced analytics | Easy | Free | TB |
| **SQLite** | Local files, testing | Easy | Free | TB |
| **DuckDB** | File-based analytics | Easy | Free | TB |
| **BigQuery** | Massive datasets | Medium | Pay-per-query | PB |
| **ClickHouse** | Real-time analytics | Medium | Free/Cloud | PB |
| **MS SQL** | Windows enterprise | Easy | License | TB |
| **Frappe DB** | ERPNext data | Easy | Free | TB |
| **Business Central** | Microsoft ERP | Medium | License | GB-TB |
| **SAP** | Enterprise ERP | Hard | License | TB-PB |
| **Tally** | India/Asia SMB | Medium | License | GB |

---

**Questions?**

- 📧 Email: hello@frappe.io
- 💬 Forum: https://discuss.frappe.io
- 🐛 Issues: https://github.com/frappe/insights/issues
