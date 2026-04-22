# ISSOFBC Text To Chart - SQLite Demo Quick Start

## 🚀 Setup (5 minutes)

### 1. Create Database & Schema

```bash
# Navigate to project folder
cd d:\SoftwareProjects\AI Projects\ISSOFBC

# Create SQLite database with schema
sqlite3 issofbc.db < schema_sqlite.sql

# Verify tables created
sqlite3 issofbc.db
> .tables
> .quit
```

### 2. Install Python Dependencies

```bash
pip install faker
```

### 3. Generate Sample Data

```bash
python generate_sample_data_sqlite.py
```

**Expected output:**
```
====== ISSOFBC SQLite - Sample Data ======
✓ Connected to SQLite database: issofbc.db
✓ Database schema created

🎓 Generating programs...
  ✓ Inserted 5 programs
👥 Generating 20 staff/volunteers...
  ✓ Inserted 20 staff/volunteers
🌍 Generating 200 beneficiaries...
  ✓ Inserted 200 beneficiaries
📝 Generating program enrollments...
  ✓ Inserted 248 enrollments
.... (more data generation)
✓ Sample data generation completed!
====== SUMMARY ======
Database: issofbc.db
Beneficiaries: 200
Programs: 5
Enrollments: 248
Total Donations: $52,340.00
```

### 4. Verify Data

```bash
sqlite3 issofbc.db

# Count records
sqlite> SELECT 'Beneficiaries' as table_name, COUNT(*) as count FROM beneficiaries
        UNION ALL
        SELECT 'Programs', COUNT(*) FROM programs
        UNION ALL
        SELECT 'Staff/Volunteers', COUNT(*) FROM staff_volunteers
        UNION ALL
        SELECT 'Program Enrollments', COUNT(*) FROM program_enrollments
        UNION ALL
        SELECT 'Job Placements', COUNT(*) FROM job_placements;

# Sample beneficiary
sqlite> SELECT * FROM beneficiaries LIMIT 1;

# Exit
sqlite> .quit
```

---

## 📊 Sample Queries

### 1. Program Enrollment Summary

**Question**: _"How many people are enrolled in each program?"_

```sql
SELECT 
  p.program_name,
  COUNT(pe.enrollment_id) as total_enrollments,
  SUM(CASE WHEN pe.status = 'Active' THEN 1 ELSE 0 END) as active,
  SUM(CASE WHEN pe.status = 'Completed' THEN 1 ELSE 0 END) as completed,
  AVG(pe.attendance_rate) as avg_attendance_pct
FROM programs p
LEFT JOIN program_enrollments pe ON p.program_id = pe.program_id
GROUP BY p.program_id
ORDER BY total_enrollments DESC;
```

**Sample Result:**
```
| Program Name              | Total Enrollments | Active | Completed | Avg Attendance |
|---------------------------|-------------------|--------|-----------|-----------------|
| Employment Support        | 40                | 28     | 12        | 85.3            |
| English Learning          | 38                | 25     | 13        | 82.1            |
| Settlement Program        | 35                | 22     | 13        | 79.2            |
| Refugee Integration       | 35                | 20     | 15        | 81.5            |
| Mentoring & Counseling    | 28                | 18     | 10        | 83.2            |
```

### 2. Job Placement Success Rate

**Question**: _"What percentage of program completers found jobs?"_

```sql
SELECT 
  p.program_name,
  COUNT(DISTINCT pe.beneficiary_id) as program_completers,
  COUNT(DISTINCT jp.beneficiary_id) as job_placements,
  ROUND(COUNT(DISTINCT jp.beneficiary_id) * 100.0 / COUNT(DISTINCT pe.beneficiary_id), 1) as placement_rate_pct
FROM programs p
LEFT JOIN program_enrollments pe ON p.program_id = pe.program_id AND pe.status = 'Completed'
LEFT JOIN job_placements jp ON pe.beneficiary_id = jp.beneficiary_id
WHERE pe.beneficiary_id IS NOT NULL
GROUP BY p.program_id
ORDER BY placement_rate_pct DESC;
```

### 3. Donation Trends

**Question**: _"What's our donation trend by month?"_

```sql
SELECT 
  strftime('%Y-%m', donation_date) as month,
  COUNT(*) as donation_count,
  SUM(donation_amount) as total_donations,
  AVG(donation_amount) as avg_donation
FROM donations
WHERE donation_type = 'Cash'
GROUP BY strftime('%Y-%m', donation_date)
ORDER BY month DESC
LIMIT 12;
```

### 4. Staff/Volunteer Productivity

**Question**: _"Which staff/volunteers delivered the most services?"_

```sql
SELECT 
  sv.first_name || ' ' || sv.last_name as staff_name,
  sv.person_type,
  COUNT(sd.service_id) as services_delivered,
  SUM(sd.duration_minutes) / 60.0 as hours_served,
  COUNT(DISTINCT sd.beneficiary_id) as unique_beneficiaries
FROM staff_volunteers sv
LEFT JOIN services_delivered sd ON sv.person_id = sd.provider_id
WHERE sv.employment_status = 'Active'
GROUP BY sv.person_id
ORDER BY services_delivered DESC
LIMIT 10;
```

### 5. Beneficiary Outcome Tracking

**Question**: _"How many beneficiaries achieved outcomes?"_

```sql
SELECT 
  outcome_type,
  COUNT(DISTINCT beneficiary_id) as beneficiaries_with_outcome,
  COUNT(*) as total_outcomes
FROM outcomes
GROUP BY outcome_type
ORDER BY beneficiaries_with_outcome DESC;
```

---

## 🌐 Deployment Path

### Option 1: Simple API + Vercel Frontend

```
Frontend (Vercel)
    ↓
API (Serverless Functions)
    ↓
SQLite Database (Deployed with API)
```

### Option 2: Backend API + Vercel Frontend

```
Frontend (Vercel)
    ↓
REST API (Python/Node hosted on AWS/Heroku/Railway)
    ↓
SQLite Database (Local or Cloud Storage)
```

### For Demo Purposes

**Simplest approach:**
1. Build a small Node.js/Python API that reads from `issofbc.db`
2. Deploy API to **Railway.app** or **Render.com** (free tier)
3. Deploy frontend to **Vercel**
4. Copy `issofbc.db` to API server

### What the API Will Do

```
POST /api/query
{
  "query": "Show me job placements by program"
}

Response:
{
  "summary": {
    "total_placements": 87,
    "programs": 5,
    "placement_rate": "42.5%"
  },
  "results": [
    {
      "program": "Employment Support",
      "count": 28,
      "rate": "70%"
    },
    ...
  ],
  "chart_spec": {
    "type": "bar",
    "title": "Job Placements by Program",
    "data": [...]
  }
}
```

---

## 📁 Project Files

```
ISSOFBC/
├── schema_sqlite.sql                    ← SQLite schema (14 tables)
├── generate_sample_data_sqlite.py       ← Data generator
├── issofbc.db                           ← SQLite database (generated)
├── SCHEMA_NONPROFIT.md                  ← Design documentation
├── API_EXAMPLES.md                      ← API specification
├── ARCHITECTURE.md                      ← System architecture
├── README.md                            ← Project overview
└── ...
```

---

## 🎯 Next Steps

### 1. Understand the Data Model
- Read `SCHEMA_NONPROFIT.md` to understand tables
- Run sample queries to explore data

### 2. Build the API
Choose a framework:
- **Python**: FastAPI (recommended for LLM integration)
- **Node.js**: Express or Remix
- **Go**: Echo or Gin

### 3. Implement SQL Generation
- Use OpenAI API to convert natural language → SQL
- Validate generated SQL against schema
- Execute and return results

### 4. Add Chart Detection
- Parse result columns and data types
- Recommend chart type (bar, line, pie, etc)
- Generate chart specification

### 5. Deploy

**Frontend (Vercel):**
```bash
# In your frontend repo
vercel deploy
```

**API (Railway.com):**
```bash
# Create railway.toml
# Push code to GitHub
# Railway auto-deploys on push
```

---

## 🧪 Testing Sample Queries

### Quick Test in SQLite CLI

```bash
sqlite3 issofbc.db

# Test 1: Count tables
.tables

# Test 2: See schema
.schema beneficiaries

# Test 3: Run a query
SELECT COUNT(*) FROM beneficiaries;

# Test 4: Export to CSV
.mode csv
.output results.csv
SELECT * FROM program_enrollments LIMIT 100;
.quit
```

### Python Test Script

```python
import sqlite3

conn = sqlite3.connect('issofbc.db')
cursor = conn.cursor()

# Run query
cursor.execute("""
    SELECT p.program_name, COUNT(*) as count 
    FROM program_enrollments pe
    JOIN programs p ON pe.program_id = p.program_id
    GROUP BY p.program_id
""")

# Fetch and print results
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} enrollments")

conn.close()
```

---

## 🔧 Troubleshooting

### "schema_sqlite.sql not found"
Solution: Make sure you're running from the ISSOFBC folder, or provide full path

### "No module named faker"
Solution: `pip install faker`

### Database is locked
Solution: Close any other SQLite connections first

### Sample data not generating
Solution: Check you have write permissions in the folder

---

## 📊 Expected Database Size

- **Schema**: 14 tables
- **Sample Data**: ~200 beneficiaries, 5 programs, 250+ enrollments
- **Database File Size**: ~500KB (can compress to ~100KB)
- **Ready for**: 10-50 concurrent queries

---

## ✅ Demo Flow

1. **Show Database**: Open in SQLite browser
2. **Run Sample Queries**: Show data trends
3. **Explain Schema**: Program → Enrollments → Outcomes
4. **Show Text-to-SQL concept**: "Query → SQL → Results → Chart"
5. **Discuss API**: How it will accept natural language
6. **Discuss Deployment**: SQLite on API server, frontend on Vercel

---

## 🚀 Ready for Next Phase?

Once you have the database working:
1. Build a simple FastAPI server
2. Add one endpoint: `POST /api/query`
3. Integrate OpenAI for SQL generation
4. Test with sample queries
5. Build Vercel frontend
6. Deploy!

**Estimated time**: 2-3 weeks for full MVP

---

**Last Updated**: April 22, 2026
**Status**: Demo-ready with SQLite!

