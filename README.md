# Text To Chart - AI-Powered Reporting Platform

A natural language to analytics API that generates reports from consolidated non-profit data.

## 🎯 Project Overview

**Organization**: IISofBC - Immigration Integration Services of BC  
**Website**: https://issbc.org/  
**Type**: Non-Profit Immigration Services Organization  
**Objective**: Build an API that accepts natural language queries and returns summarized data, tabulations, and auto-generated charts for program reporting and impact measurement.

### Services Offered
- **Settlement Programs** - Help newcomers adjust to life in BC
- **English Learning** - Improve language skills (ESL)
- **Employment Support** - Career coaching and job placement
- **Refugee Services** - Specialized support for refugees
- **Mentoring & Counseling** - One-on-one support

### Funding Sources
- Government grants (federal, provincial, municipal)
- Donations (individual, corporate, foundation)
- Service fees

---

## 📁 Project Structure

```
ISSOFBC/
├── README.md                            ← This file
├── QUICKSTART_SQLITE.md                 ← Demo setup guide (START HERE!)
├── SCHEMA_NONPROFIT.md                  ← Database design for non-profit
├── ARCHITECTURE.md                      ← System architecture & data flow
├── API_EXAMPLES.md                      ← API endpoints & usage examples
├── schema_sqlite.sql                    ← SQLite DDL (14 tables)
├── generate_sample_data_sqlite.py       ← Sample data generator
├── issofbc.db                           ← SQLite database (generated)
└── docs/
    ├── sql_examples.md                  ← Sample queries
    └── deployment_guide.md              ← Deployment to Vercel + API
```

---

## 🏗️ Phase 1: Database & Schema (CURRENT)

### Completed ✅
- [x] Non-profit data model redesigned (14 tables)
- [x] SQLite schema created (perfect for demos)
- [x] Sample data generator (Python)
- [x] Architecture documentation
- [x] API specification
- [x] Quick start guide

### Key Tables

**Core Reference**:
- `beneficiaries` - People we serve (immigrants, refugees, etc)
- `programs` - Programs offered (Settlement, English, Work, Refugee, Mentoring)
- `staff_volunteers` - Staff and volunteers

**Program Management**:
- `program_enrollments` - Who is enrolled in which program
- `program_sessions` - Class/workshop sessions
- `session_attendance` - Attendance tracking

**Outcomes & Progress**:
- `outcomes` - Tracking improvements (English level, job placement, etc)
- `services_delivered` - Individual services (coaching, counseling)
- `job_placements` - Employment success tracking
- `settlement_milestones` - Life achievements (housing, banking, health cards)

**Operations**:
- `communication_log` - Interaction tracking
- `donations` - Donation records
- `government_grants` - Grant funding
- `expenses` - Spending and budget tracking

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SQLite (included with Python)
- Git

### 1. Setup Database

```bash
# Create SQLite database from schema
sqlite3 issofbc.db < schema_sqlite.sql

# Verify tables created
sqlite3 issofbc.db ".tables"
```

### 2. Generate Sample Data

```bash
# Install Python dependencies
pip install faker

# Run generator
python generate_sample_data_sqlite.py
```

### 3. Verify Installation

```bash
sqlite3 issofbc.db
> SELECT COUNT(*) FROM beneficiaries;
> SELECT COUNT(*) FROM program_enrollments;
> .quit
```

**✓ Done!** You now have a fully populated demo database.

---

## 📊 Core Features

### 1. Natural Language Queries
Non-profit managers can ask in plain English:
- "How many people completed the English program this quarter?"
- "What's our job placement rate?"
- "Show me donation trends by month"
- "Which staff delivered the most services?"
- "How many refugees achieved settlement milestones?"

### 2. Intelligent SQL Generation
The system:
- Parses natural language query
- Maps to schema tables (beneficiaries, programs, outcomes, etc)
- Generates optimized SQL
- Adds non-profit-specific metrics

### 3. Smart Summarization
Results include:
- Executive summary with key metrics
- Comparison to previous periods
- Notable achievements and opportunities
- Impact metrics

### 4. Auto Chart Detection
Determines if data needs visualization:
- Time-series → Line/Area chart (trends over time)
- Categories → Bar/Pie chart (breakdown by type)
- Program comparisons → Radar chart
- Single values → KPI card (key metrics)

---

## 🔌 API Endpoints

### Ad-hoc Queries
```
POST /api/query
```
Send natural language query, get data + charts

**Example**:
```json
{
  "query": "How many beneficiaries completed the English program this quarter?"
}
```

### Predefined Reports
```
GET /api/reports
POST /api/reports/{id}/execute
```
Pre-built dashboards for common use cases

### Schema Browsing
```
GET /api/schema
GET /api/schema/tables/{name}
```
Explore available data structures

---

## 📋 Database Schema

**14 Tables** organized by function:

**Programs & Enrollment**:
```
Beneficiaries ← Program Enrollments → Programs
                                ↓
                        Program Sessions ← Attendance
```

**Outcomes & Impact**:
```
Beneficiaries → Outcomes (English level, job, settlement)
           → Job Placements
           → Settlement Milestones
           → Services Delivered
           → Communication Log
```

**Funding & Budget**:
```
Donations
Government Grants → Programs → Expenses
```

---

## 📈 Sample Queries & Results

### Query 1: Program Completion Rates
```
"How many beneficiaries completed each program this year?"
```

**Summary:**
- Employment Program: 40 completions (85% of enrolled)
- English Learning: 38 completions (80% of enrolled)
- Settlement: 35 completions (75% of enrolled)
- **Overall completion rate: 80%**

**Chart:** Bar chart showing completion rates by program

---

### Query 2: Job Placement Success
```
"What percentage of our employment program participants found jobs?"
```

**Summary:**
- Program completers: 40
- Job placements: 28
- **Placement rate: 70%**
- Average time to placement: 8 weeks
- Average salary: $52,000

**Chart:** KPI card showing 70% + supporting metrics

---

### Query 3: Funding Analysis
```
"Show me donations vs government grants by month"
```

**Summary:**
- YTD Government Grants: $450,000
- YTD Donations: $52,340
- **Total Funding: $502,340**
- Average donation: $349
- Top donor: XYZ Foundation ($12,500)

**Chart:** Combo chart with funding sources side-by-side

---

### Query 4: Staff Productivity
```
"Which volunteers delivered the most services?"
```

**Summary:**
- Top volunteer: Maria Garcia - 156 services (234 hours)
- 2nd place: John Smith - 142 services (198 hours)
- Team total: 1,247 services delivered
- Avg beneficiaries per volunteer: 18

**Chart:** Top 10 volunteers by hours served

---

## 📋 Business Rules

### Program Management
- Beneficiaries can enroll in multiple programs
- Enrollment status: Active, Completed, Dropped Out
- Completion requires 75% attendance
- Session attendance tracked for reporting

### Outcomes & Success Metrics
- English proficiency tracked from A1 (beginner) to C2 (fluent)
- Job placement tracked with salary and employer info
- Settlement milestones: SIN, bank account, housing, health card
- Services count toward outcome achievement

### Funding & Budgeting
- Government grants tied to specific programs
- Expenses tracked by category and program
- Donation receipt issued for tax purposes
- Budget utilization reported quarterly

### Staff & Volunteers
- Volunteers hours tracked against annual targets
- Staff assigned to programs and sessions
- Volunteer languages recorded for matching
- Productivity measured by services delivered

---

## 🔧 Technology Stack (Planned)

### Database
- **SQLite** (for demo & development)
- **PostgreSQL** (for production, if needed)

### Backend API
- **Framework**: FastAPI (Python) or Express (Node.js)
- **LLM**: OpenAI GPT-4 for SQL generation
- **Hosting**: Railway.com or Render (free tier)
- **Database**: SQLite file deployed with API

### Frontend
- **Framework**: React or Vue.js
- **Deployment**: Vercel (free tier)
- **Charting**: Apache ECharts or Plotly
- **UI**: TailwindCSS or Material-UI

### Development
- **Local Database**: SQLite (issofbc.db)
- **Data Generation**: Python + Faker
- **Testing**: pytest for API, Vitest for frontend
- **CI/CD**: GitHub Actions

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `QUICKSTART_SQLITE.md` | **START HERE** - Demo setup in 5 minutes |
| `SCHEMA_NONPROFIT.md` | Detailed non-profit data model |
| `ARCHITECTURE.md` | System architecture & data flow |
| `API_EXAMPLES.md` | Complete API reference |
| `schema_sqlite.sql` | SQL DDL for creating tables |
| `generate_sample_data_sqlite.py` | Python script to populate data |

---

## 🎓 Example: End-to-End Query Flow

### 1. User Input
```
"What percentage of refugees completed our settlement program and found jobs?"
```

### 2. Request to API
```json
{
  "query": "What percentage of refugees completed our settlement program and found jobs?"
}
```

### 3. SQL Generated
```sql
SELECT 
  COUNT(DISTINCT pe.beneficiary_id) as refugees_completed,
  COUNT(DISTINCT jp.beneficiary_id) as found_jobs,
  ROUND(COUNT(DISTINCT jp.beneficiary_id) * 100.0 / 
        COUNT(DISTINCT pe.beneficiary_id), 1) as success_rate_pct
FROM beneficiaries b
JOIN program_enrollments pe ON b.beneficiary_id = pe.beneficiary_id
LEFT JOIN job_placements jp ON b.beneficiary_id = jp.beneficiary_id
JOIN programs p ON pe.program_id = p.program_id
WHERE b.immigration_status = 'Refugee'
  AND p.program_code = 'SETTLE'
  AND pe.status = 'Completed'
```

### 4. Summary Generated
```
🎯 Refugee Settlement & Employment Outcomes

Key Findings:
✓ 28 refugees completed settlement program
✓ 19 refugees found employment
✓ 67.9% employment rate among completers
✓ Average time to job placement: 7 weeks
✓ Average starting salary: $48,500

Impact Achieved:
- Housing secured: 26/28 (93%)
- Bank accounts opened: 27/28 (96%)
- Health cards obtained: 28/28 (100%)
```

### 5. Chart Generated
```json
{
  "chart_type": "bar",
  "title": "Refugee Settlement Program Success",
  "series": [
    {
      "name": "Program Completers",
      "value": 28,
      "color": "#3498db"
    },
    {
      "name": "Employment Found",
      "value": 19,
      "color": "#2ecc71"
    }
  ]
}
```

---

## 🔐 Security Considerations

### Data Access
- Row-level security by organization
- Department-level access controls
- Salary/sensitive data encryption

### Query Safety
- Parameterized queries (prevent SQL injection)
- Query timeout limits (max 30 seconds)
- Audit logging of all queries

### Authentication
- JWT tokens for API access
- OAuth 2.0 for future integrations
- API key rotation

---

## 📊 Performance Expectations

| Operation | Expected Time |
|-----------|---------------|
| Simple aggregation (last 1 month) | < 100ms |
| Complex join + aggregation | 200-500ms |
| Full year analysis | 1-3s |
| Very large result sets (>100K rows) | 5-10s |

---

## ❓ FAQs

**Q: Why SQLite instead of a "real" database?**  
A: For demos, development, and MVP - SQLite is fast, portable, and requires zero setup. Switch to PostgreSQL for production if needed.

**Q: Where do I deploy this?**  
A: Frontend on Vercel, API on Railway.com or Render (free tiers available). SQLite database travels with the API.

**Q: Can I import data from existing systems?**  
A: Yes - write ETL scripts to extract from current systems and populate the schema. We'll help design the mappings.

**Q: How many people can use this simultaneously?**  
A: With SQLite: 5-10. With PostgreSQL: 100+. Depends on your infrastructure.

**Q: How do I customize this for other organizations?**  
A: The schema is generic enough for any immigration/social services non-profit. Customize program names and metrics.

---

## 🚧 Development Roadmap

### Phase 1: ✅ Database & Schema (DONE)
- [x] Design non-profit data model
- [x] Create SQLite tables
- [x] Build sample data generator
- [x] Documentation complete

### Phase 2: Core API 🟡 (NEXT)
- [ ] Build FastAPI server
- [ ] Integrate OpenAI for SQL generation
- [ ] Implement query executor
- [ ] Create result processor
- [ ] Estimated time: 2 weeks

### Phase 3: Frontend 🔵
- [ ] Build Vercel app
- [ ] Create query builder UI
- [ ] Integrate chart library
- [ ] Estimated time: 1 week

### Phase 4: Deployment 🔵
- [ ] Deploy API to Railway
- [ ] Deploy frontend to Vercel
- [ ] Test end-to-end
- [ ] Estimated time: 3 days

### Phase 5: Integration 🔵
- [ ] ETL from existing systems (if applicable)
- [ ] Real-time or scheduled data sync
- [ ] Additional reporting

---

## 🚀 Next Steps (for demo)

### Quick Start (5 minutes)
```bash
cd d:\SoftwareProjects\AI Projects\ISSOFBC

# Create database
sqlite3 issofbc.db < schema_sqlite.sql

# Generate data
pip install faker
python generate_sample_data_sqlite.py

# Verify
sqlite3 issofbc.db "SELECT COUNT(*) FROM beneficiaries;"
```

**Now you have a working database ready for API development!**

### Then Build the API
1. Choose framework (FastAPI recommended)
2. Connect to SQLite database
3. Create `/api/query` endpoint
4. Integrate OpenAI for SQL generation
5. Test with sample queries
6. Deploy to Railway

### Then Build the Frontend
1. Create Vercel project
2. Build query input
3. Add chart rendering
4. Connect to API
5. Deploy

---

## 📞 Support & Questions

**For database questions:**
- See `SCHEMA_NONPROFIT.md` for table definitions
- See `QUICKSTART_SQLITE.md` for setup issues
- Run sample queries to understand data

**For API design:**
- See `API_EXAMPLES.md` for endpoints
- See `ARCHITECTURE.md` for data flow

**For schema customization:**
- Edit `schema_sqlite.sql`
- Regenerate sample data
- Update API queries accordingly

---

## 📄 License

[To be determined by IISofBC]

---

**Last Updated**: April 22, 2026  
**Status**: Foundation Complete - SQLite Ready for Demo & Development!

