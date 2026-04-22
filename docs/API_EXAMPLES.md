# Text To Chart API - Quick Start Guide & Examples

## Quick Start

### 1. Setup Database

```bash
# Connect to MySQL
mysql -u root -p

# Run the DDL script
source schema.sql

# Verify tables created
SHOW TABLES;
```

### 2. Generate Sample Data

```bash
# Install dependencies
pip install faker mysql-connector-python

# Generate sample data with default settings
python generate_sample_data.py

# Or customize parameters
python generate_sample_data.py \
  --host localhost \
  --user root \
  --password your_password \
  --database issofbc_analytics \
  --seed 42 \
  --employees 200 \
  --contacts 150 \
  --sales 1000
```

### 3. Verify Data

```sql
-- Check counts
SELECT COUNT(*) as organization_count FROM organizations;
SELECT COUNT(*) as employee_count FROM employees;
SELECT COUNT(*) as sales_count FROM sales_transactions;
SELECT COUNT(*) as customer_count FROM contacts WHERE contact_type = 'Customer';

-- Sample queries
SELECT 
  c.company_name,
  COUNT(st.transaction_id) as order_count,
  SUM(st.total_amount) as total_sales
FROM sales_transactions st
JOIN contacts c ON st.customer_id = c.contact_id
WHERE st.status = 'Paid'
GROUP BY c.contact_id
ORDER BY total_sales DESC
LIMIT 10;
```

---

## API Endpoints

All endpoints return JSON responses with the following structure:

```json
{
  "status": "success" | "error",
  "query_id": "uuid",
  "execution_time_ms": 250,
  "summary": { ... },
  "results": [ ... ],
  "chart_spec": { ... },
  "error_message": null
}
```

### POST /api/query
**Execute an ad-hoc natural language query**

#### Request
```json
{
  "query": "Show me sales by customer for the last quarter",
  "organization_id": 1,
  "limit": 100,
  "include_chart": true
}
```

#### Response
```json
{
  "status": "success",
  "query_id": "q-2026-04-22-001",
  "execution_time_ms": 245,
  "generated_sql": "SELECT c.company_name, SUM(st.total_amount) as total_sales ...",
  "summary": {
    "total_records": 25,
    "total_amount": 2850000,
    "average_sale": 114000,
    "period": "Q1 2026",
    "insights": [
      "Top customer accounts for 22% of sales",
      "Average deal size increased 15% vs previous quarter"
    ]
  },
  "tabulation": {
    "headers": ["Customer", "Total Sales", "Order Count", "Status"],
    "rows": [
      ["ABC Corporation", 450000, 15, "Active"],
      ["XYZ Industries", 380000, 12, "Active"],
      ...
    ],
    "row_count": 25
  },
  "chart_spec": {
    "chart_type": "bar",
    "title": "Sales by Customer - Q1 2026",
    "x_axis": {
      "field": "company_name",
      "label": "Customer Name"
    },
    "y_axis": {
      "field": "total_sales",
      "label": "Total Sales ($)"
    },
    "data_rows": 25
  }
}
```

---

### POST /api/reports
**Get list of predefined reports**

#### Request
```json
{
  "organization_id": 1,
  "category": "sales" | "financial" | "hr" | "crm"
}
```

#### Response
```json
{
  "status": "success",
  "reports": [
    {
      "report_id": "RPT-SALES-001",
      "name": "Sales Performance Dashboard",
      "description": "Monthly sales trends, top products, and rep performance",
      "category": "sales",
      "last_run": "2026-04-21T14:30:00Z",
      "parameters": [
        {
          "name": "start_date",
          "type": "date",
          "required": true,
          "default": "2026-01-01"
        },
        {
          "name": "end_date",
          "type": "date",
          "required": true,
          "default": "2026-12-31"
        }
      ]
    },
    ...
  ]
}
```

---

### POST /api/reports/{report_id}/execute
**Execute a predefined report**

#### Request
```json
{
  "organization_id": 1,
  "parameters": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31"
  }
}
```

#### Response
```json
{
  "status": "success",
  "report_id": "RPT-SALES-001",
  "execution_time_ms": 1200,
  "sections": [
    {
      "section_name": "Sales Summary",
      "type": "kpi_cards",
      "data": {
        "total_sales": 2850000,
        "order_count": 125,
        "order_count_trend": "+12%",
        "avg_deal_size": 22800
      }
    },
    {
      "section_name": "Sales by Product",
      "type": "bar_chart",
      "chart_spec": { ... },
      "data": [ ... ]
    },
    {
      "section_name": "Top Sales Reps",
      "type": "table",
      "data": [ ... ]
    }
  ]
}
```

---

### GET /api/schema
**Get database schema metadata**

#### Response
```json
{
  "status": "success",
  "tables": [
    {
      "table_name": "sales_transactions",
      "description": "All sales orders, invoices, and quotes",
      "fact_table": true,
      "columns": [
        {
          "column_name": "transaction_id",
          "type": "int",
          "nullable": false,
          "primary_key": true
        },
        ...
      ],
      "relationships": [
        {
          "foreign_table": "contacts",
          "foreign_column": "contact_id",
          "local_column": "customer_id"
        }
      ]
    }
  ]
}
```

---

### GET /api/schema/tables/{table_name}
**Get detailed schema for a specific table**

#### Response
```json
{
  "status": "success",
  "table_name": "sales_transactions",
  "description": "All sales orders, invoices, and quotes",
  "columns": [
    {
      "name": "transaction_id",
      "type": "int",
      "nullable": false,
      "primary_key": true,
      "description": "Unique transaction identifier"
    },
    {
      "name": "status",
      "type": "enum",
      "allowed_values": ["Draft", "Posted", "Partially Paid", "Paid", "Overdue", "Cancelled"],
      "description": "Current status of the transaction"
    }
  ],
  "summary_metrics": [
    "total_sales",
    "count_transactions",
    "sales_by_customer",
    "sales_by_product"
  ]
}
```

---

## Usage Examples

### Example 1: Top Customers

**User Query:**
```
"What are my top 10 customers by revenue this year?"
```

**Generated SQL:**
```sql
SELECT 
  c.company_name,
  COUNT(st.transaction_id) as order_count,
  SUM(st.total_amount) as total_revenue,
  AVG(st.total_amount) as avg_order_value,
  MAX(st.transaction_date) as last_order_date
FROM sales_transactions st
JOIN contacts c ON st.customer_id = c.contact_id
WHERE YEAR(st.transaction_date) = YEAR(CURDATE())
  AND st.status IN ('Paid', 'Partially Paid')
GROUP BY st.customer_id, c.company_name
ORDER BY total_revenue DESC
LIMIT 10
```

**JSON Response:**
```json
{
  "status": "success",
  "summary": {
    "total_customers": 10,
    "combined_revenue": 5420000,
    "average_customer_value": 542000,
    "top_customer": "ABC Corporation with $890,000"
  },
  "results": [
    {
      "company_name": "ABC Corporation",
      "order_count": 15,
      "total_revenue": 890000,
      "avg_order_value": 59333,
      "last_order_date": "2026-04-20"
    },
    {
      "company_name": "XYZ Industries",
      "order_count": 12,
      "total_revenue": 750000,
      "avg_order_value": 62500,
      "last_order_date": "2026-04-19"
    }
  ],
  "chart_spec": {
    "chart_type": "bar",
    "title": "Top 10 Customers by Revenue - 2026",
    "x_axis": "company_name",
    "y_axis": "total_revenue",
    "series": [
      {
        "name": "Revenue",
        "field": "total_revenue",
        "type": "bar",
        "color": "#2ecc71"
      }
    ]
  }
}
```

---

### Example 2: Sales vs Costs Trend

**User Query:**
```
"Show me revenue vs cost of goods sold by month for the last 12 months"
```

**Generated SQL:**
```sql
SELECT 
  DATE_TRUNC('month', st.transaction_date) as month,
  SUM(st.total_amount) as revenue,
  SUM(pt.total_amount) as cogs,
  SUM(st.total_amount) - SUM(pt.total_amount) as gross_profit,
  ROUND((SUM(st.total_amount) - SUM(pt.total_amount)) / SUM(st.total_amount) * 100, 2) as profit_margin_percent
FROM sales_transactions st
LEFT JOIN purchase_transactions pt ON MONTH(st.transaction_date) = MONTH(pt.transaction_date)
  AND YEAR(st.transaction_date) = YEAR(pt.transaction_date)
WHERE st.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
  AND st.status = 'Paid'
  AND pt.status = 'Paid'
GROUP BY DATE_TRUNC('month', st.transaction_date)
ORDER BY month
```

**Chart Specification:**
```json
{
  "chart_type": "combo",
  "title": "Revenue vs Cost of Goods Sold - Last 12 Months",
  "subtitle": "Monthly trend with profit margin",
  "x_axis": {
    "field": "month",
    "type": "date",
    "format": "MMM YYYY"
  },
  "series": [
    {
      "name": "Revenue",
      "field": "revenue",
      "type": "line",
      "color": "#2ecc71",
      "yAxis": "left"
    },
    {
      "name": "COGS",
      "field": "cogs",
      "type": "line",
      "color": "#e74c3c",
      "yAxis": "left"
    },
    {
      "name": "Profit Margin %",
      "field": "profit_margin_percent",
      "type": "area",
      "color": "#3498db",
      "yAxis": "right",
      "opacity": 0.3
    }
  ],
  "recommended_actions": [
    "Monitor increasing COGS relative to revenue",
    "Cost control opportunity in Q4"
  ]
}
```

---

### Example 3: Employee Activity Report

**User Query:**
```
"Which sales reps had the most customer interactions last month?"
```

**Generated SQL:**
```sql
SELECT 
  CONCAT(e.first_name, ' ', e.last_name) as rep_name,
  COUNT(ca.activity_id) as total_activities,
  COUNT(DISTINCT ca.contact_id) as unique_contacts,
  SUM(CASE WHEN ca.activity_type = 'Call' THEN 1 ELSE 0 END) as num_calls,
  SUM(CASE WHEN ca.activity_type = 'Meeting' THEN 1 ELSE 0 END) as num_meetings,
  SUM(CASE WHEN ca.activity_type = 'Email' THEN 1 ELSE 0 END) as num_emails,
  SUM(CASE WHEN ca.activity_type = 'Meeting' THEN ca.duration_minutes ELSE 0 END) as total_meeting_hours
FROM crm_activities ca
JOIN employees e ON ca.employee_id = e.employee_id
WHERE MONTH(ca.activity_date) = MONTH(CURDATE() - INTERVAL 1 MONTH)
  AND YEAR(ca.activity_date) = YEAR(CURDATE() - INTERVAL 1 MONTH)
  AND ca.status = 'Completed'
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY total_activities DESC
```

**Response:**
```json
{
  "status": "success",
  "summary": {
    "total_activities": 342,
    "total_reps": 12,
    "avg_activities_per_rep": 28.5,
    "top_performer": "John Smith with 52 activities"
  },
  "tabulation": {
    "headers": ["Rep Name", "Total Activities", "Unique Contacts", "Calls", "Meetings", "Emails", "Meeting Hours"],
    "rows": [
      ["John Smith", 52, 18, 22, 8, 22, 6.5],
      ["Sarah Johnson", 48, 16, 20, 7, 21, 5.75],
      ["Mike Chen", 45, 15, 18, 6, 21, 4.5]
    ]
  },
  "chart_spec": {
    "chart_type": "bubble",
    "title": "Sales Rep Activity Analysis - March 2026",
    "x_axis": {
      "field": "unique_contacts",
      "label": "Unique Contacts"
    },
    "y_axis": {
      "field": "total_activities",
      "label": "Total Activities"
    },
    "bubble_size": {
      "field": "total_meeting_hours",
      "label": "Meeting Hours"
    },
    "color_by": "rep_name"
  }
}
```

---

## Error Handling

### Invalid Query

**Request:**
```json
{
  "query": "Show me data from a table that doesn't exist"
}
```

**Response:**
```json
{
  "status": "error",
  "error_code": "INVALID_QUERY",
  "error_message": "Could not generate SQL from query. The tables mentioned do not exist in the schema.",
  "suggestion": "Try: 'Show me sales transactions' or 'What are my top customers?'"
}
```

### Query Timeout

**Response:**
```json
{
  "status": "error",
  "error_code": "QUERY_TIMEOUT",
  "error_message": "Query exceeded maximum execution time of 30 seconds.",
  "suggestion": "Try narrowing the date range or adding more specific filters.",
  "partial_results": null
}
```

### Access Denied

**Response:**
```json
{
  "status": "error",
  "error_code": "ACCESS_DENIED",
  "error_message": "You do not have permission to access payroll data.",
  "error_details": "User role: Sales Representative"
}
```

---

## Authentication (to be implemented)

All API requests should include:

```header
Authorization: Bearer {JWT_TOKEN}
X-Organization-ID: {ORG_ID}
```

---

## Rate Limiting

- **Free Tier**: 100 queries/hour, 10 concurrent queries
- **Basic**: 1000 queries/hour, 25 concurrent queries
- **Enterprise**: Unlimited

Responses include rate limit headers:
```header
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 842
X-RateLimit-Reset: 2026-04-22T15:00:00Z
```

---

## Performance Tips

1. **Add date filters** for large datasets
2. **Limit results** with `limit: 50` for dashboards
3. **Use specific tables** instead of joins when possible
4. **Cache results** for infrequently changing data
5. **Schedule reports** during off-peak hours

---

## Next Steps

1. Choose backend framework (FastAPI, Express, Django)
2. Implement SQL generation engine using LLM prompts
3. Build authentication & authorization layer
4. Create web frontend for query builder
5. Integrate with real data sources
6. Deploy to cloud infrastructure

