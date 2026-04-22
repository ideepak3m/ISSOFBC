# Text To Chart App - Architecture & Implementation Plan

## Executive Summary

You're building a natural language to report generation system for IISofBC. The architecture consists of:

1. **Unified Database Schema** - Consolidates data from 4 existing systems
2. **SQL Generation Engine** - Converts natural language queries to SQL using the schema + business rules
3. **Query Executor** - Runs the generated SQL
4. **Results Processor** - Summarizes, tabulates, and determines if charts are needed
5. **Chart Generator** - Creates chart specifications based on data

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Future)                      │
│              Web App / Mobile / Voice Input                      │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                   TEXT TO CHART API                             │
├────────────────────────────────────────────────────────────────┤
│  1. Request Handler: Accept natural language query              │
│  2. Context Detector: Identify which entities are relevant      │
│  3. SQL Generator: Use schema.yaml to generate SQL             │
│  4. Query Executor: Run SQL against database                    │
│  5. Result Processor: Summarize & detect chart needs            │
│  6. Chart Spec Generator: Define chart type & columns           │
│  7. Response Formatter: Return JSON response                    │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                 UNIFIED ANALYTICS DATABASE                      │
├────────────────────────────────────────────────────────────────┤
│  Sources: Newtract │ Business Central │ Paywork │ BambooHR      │
│                                                                  │
│  ├─ Organizations          ├─ Sales Transactions                │
│  ├─ Departments            ├─ Purchase Transactions             │
│  ├─ Employees              ├─ GL Transactions                   │
│  ├─ Contacts               ├─ Payroll Records                   │
│  ├─ Products               ├─ CRM Opportunities                 │
│  └─ HR Leave Requests      └─ CRM Activities                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Schema Definition (schema.yaml)
**Purpose**: Single source of truth for data structure
**Contains**:
- Table definitions with all columns, types, constraints
- Foreign key relationships
- Allowed values for categorical fields
- Summary metrics for each table
- Business rules for calculations

**Usage**:
- SQL Generator reads this to understand available fields
- Context detector uses it to map user queries to tables
- Chart generator uses it to determine appropriate visualizations

### 2. SQL Generation Engine
**Process**:
```
User Query → Extract Entities → Choose Tables → 
Build WHERE clause → Add Joins → Add Aggregations → SQL
```

**Example Transformations**:

**Query 1**: _"Show me total sales by customer for the last quarter"_
```sql
-- Generated SQL
SELECT 
  c.company_name,
  SUM(st.total_amount) as total_sales,
  COUNT(*) as num_invoices
FROM sales_transactions st
JOIN contacts c ON st.customer_id = c.contact_id
WHERE st.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
  AND st.status IN ('Paid', 'Partially Paid')
GROUP BY c.contact_id, c.company_name
ORDER BY total_sales DESC
```

**Query 2**: _"Which employees had the most activities this month?"_
```sql
SELECT 
  CONCAT(e.first_name, ' ', e.last_name) as employee_name,
  COUNT(*) as activity_count,
  COUNT(DISTINCT ca.contact_id) as unique_contacts
FROM crm_activities ca
JOIN employees e ON ca.employee_id = e.employee_id
WHERE MONTH(ca.activity_date) = MONTH(CURDATE())
  AND YEAR(ca.activity_date) = YEAR(CURDATE())
  AND ca.status = 'Completed'
GROUP BY ca.employee_id
ORDER BY activity_count DESC
```

### 3. Query Executor
- Executes SQL against the unified database
- Handles pagination for large result sets
- Returns structured result set

### 4. Result Processor
**Responsibility**: Make sense of raw SQL results

**Tasks**:
- **Summarization**: Generate executive summary
  - Total rows returned
  - Key metrics (sum, avg, count, min, max)
  - Notable trends or outliers
  
- **Tabulation**: Format results as table
  - Column names and types
  - Row-by-row data
  - Quick statistics
  
- **Chart Detection**: Determine if visualization needed
  - If result has time dimension → line/bar chart
  - If result has categorical grouping → pie/bar chart
  - If result has geographic dimension → map
  - If result is single value → KPI card

### 5. Chart Specification Generator
**Output**: Chart definition (not the visual itself)

**Format**:
```json
{
  "chart_type": "bar",
  "title": "Sales by Customer",
  "x_axis": "company_name",
  "y_axis": "total_sales",
  "series": null,
  "filters": ["last_quarter"],
  "data_rows": 25
}
```

---

## Data Flow Example

### User asks: _"Show me revenue and costs by month for 2025"_

#### Step 1: Request Parsing
```
Query: "Show me revenue and costs by month for 2025"
Detected Entities: [revenue, costs, month, 2025]
```

#### Step 2: Context Detection
```
- "revenue" → sales_transactions.total_amount (WHERE status='Paid')
- "costs" → purchase_transactions.total_amount (WHERE status='Paid')  
- "by month" → date-based grouping
- "2025" → date filter
```

#### Step 3: SQL Generation
```sql
SELECT 
  DATE_TRUNC('month', st.transaction_date) as month,
  SUM(st.total_amount) as revenue,
  SUM(pt.total_amount) as cost,
  SUM(st.total_amount) - SUM(pt.total_amount) as profit_margin
FROM sales_transactions st
FULL OUTER JOIN purchase_transactions pt 
  ON DATE_TRUNC('month', st.transaction_date) = 
     DATE_TRUNC('month', pt.transaction_date)
WHERE YEAR(st.transaction_date) = 2025
  AND st.status = 'Paid'
  AND pt.status = 'Paid'
GROUP BY DATE_TRUNC('month', st.transaction_date)
ORDER BY month
```

#### Step 4: Execution
```
Results:
2025-01 | 450000 | 280000 | 170000
2025-02 | 520000 | 310000 | 210000
2025-03 | 485000 | 295000 | 190000
...
```

#### Step 5: Summarization
```
📊 Revenue vs Costs Analysis - 2025

Summary:
- Total Revenue: $5,890,000
- Total Costs: $3,650,000
- Total Profit: $2,240,000
- Avg Monthly Profit: $186,667
- Best Month: March with $210,000 profit
- Worst Month: January with $170,000 profit

Insights:
✓ Profit margins stable (37-41%)
✓ Upward revenue trend from Jan to Mar
⚠ Cost increase correlates with revenue
```

#### Step 6: Chart Specification
```json
{
  "chart_type": "combo",
  "title": "Revenue vs Costs - 2025",
  "subtitle": "Monthly trend analysis",
  "x_axis": {
    "field": "month",
    "type": "date",
    "format": "MMM"
  },
  "series": [
    {
      "name": "Revenue",
      "field": "revenue",
      "type": "line",
      "color": "#2ecc71"
    },
    {
      "name": "Costs", 
      "field": "cost",
      "type": "line",
      "color": "#e74c3c"
    },
    {
      "name": "Profit",
      "field": "profit_margin",
      "type": "bar",
      "color": "#3498db"
    }
  ],
  "data_rows": 12,
  "recommended_action": "Compare profitability trends"
}
```

---

## Predefined Reports (Phase 2)

These will be built once the API is solid:

### 1. Sales Performance Dashboard
- Top customers by revenue
- Sales by product category
- Order fulfillment rate
- Sales trend YoY

### 2. Financial Health Report
- Revenue vs expenses
- GL account balances
- Cash flow analysis
- Profitability by department

### 3. HR Analytics Report
- Headcount by department
- Payroll expense trending
- Leave utilization
- Turnover analysis

### 4. CRM Pipeline Report
- Opportunity stage distribution
- Sales funnel conversion
- Pipeline value forecast
- Activity metrics by rep

---

## Implementation Roadmap

### Phase 1: Database & Schema ✅ 
- [x] Design unified schema
- [x] Define YAML structure
- [ ] Create SQL DDL scripts
- [ ] Generate sample data (faker)

### Phase 2: Core API
- [ ] Build SQL generator (prompts + parsing)
- [ ] Implement query executor
- [ ] Build result processor
- [ ] Implement chart detector

### Phase 3: Advanced Features
- [ ] Build predefined report templates
- [ ] Multi-language support
- [ ] Caching layer
- [ ] Performance optimization

### Phase 4: Frontend
- [ ] Web UI for queries
- [ ] Report dashboard
- [ ] Chart rendering
- [ ] Export to PDF/Excel

### Phase 5: Integration
- [ ] Data extraction from 4 systems
- [ ] Real-time sync mechanism
- [ ] Data quality validation
- [ ] Audit logging

---

## Technology Stack (Suggested)

### Backend API
- **Language**: Python (FastAPI) or Node.js (Express)
- **LLM Integration**: OpenAI API (GPT-4) or local LLM
- **Database**: PostgreSQL (open source) or SQL Server (if on MS ecosystem)
- **Async Processing**: Celery or similar for long-running queries

### Key Libraries
- **LLM**: langchain, llama_index
- **SQL**: sqlalchemy, sql-parse
- **Data Processing**: pandas, polars
- **API**: FastAPI, Pydantic
- **Testing**: pytest

### Frontend (Future)
- **Framework**: React or Vue.js
- **Charting**: Apache ECharts, Plotly, or Chart.js
- **UI Components**: Material-UI or shadcn/ui

---

## Next Immediate Steps

1. **Create SQL DDL Scripts**
   - Generate CREATE TABLE statements from schema.yaml
   - Add indexes on frequently queried columns
   - Create views for common aggregations

2. **Generate Sample Data**
   - Create Python script using Faker library
   - Populate ~100 organizations, 500 employees, 2000+ transactions
   - Ensure realistic relationships and data distributions

3. **Design API Endpoints**
   - POST /api/query - Execute ad-hoc query
   - GET /api/reports - List predefined reports
   - GET /api/schema - Get schema metadata
   - GET /api/schema/tables/{table_name} - Get table details

4. **Choose & Setup LLM**
   - If using OpenAI: Cost analysis & rate limiting
   - If using local LLM: Model selection & infrastructure

5. **Build Prompt Engineering Framework**
   - System prompts for SQL generation
   - Few-shot examples
   - Error handling & regeneration logic

---

## Key Considerations

### Data Quality
- Implement validation rules when syncing from source systems
- Handle missing/null values appropriately
- Log data quality issues for investigation

### Performance
- Index heavily queried dimensions (date, customer, employee)
- Partition large tables (e.g., transactions by month)
- Implement query result caching
- Set query timeout limits

### Security
- Implement row-level security (some users see only their department)
- Audit all queries and data access
- Use parameterized queries to prevent SQL injection
- Encrypt sensitive fields (salary, email)

### Scalability
- Design for historical data (multi-year retention)
- Consider materialized views for complex calculations
- Plan for real-time updates from source systems

