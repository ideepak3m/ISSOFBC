# Database Schema Changes - Commercial → Non-Profit

## What Changed and Why

You originally asked about a business intelligence platform for IISofBC. After you clarified that **IISofBC is actually a non-profit immigration services organization** (not a commercial business), the entire database schema needed to be redesigned.

---

## Original Schema (Wrong ❌)

Designed for a **commercial business model**:

```
Organizations → Employees, Departments
           → Contacts (Customers, Vendors)
           → Products
           → Sales Transactions (invoices, orders)
           → Purchase Transactions
           → GL Transactions (accounting)
           → Payroll Records
           → CRM (opportunities, activities)
           → HR (leave requests)

Total: 20 tables
Focus: Revenue, Costs, Profit, Sales Pipeline
```

**Problem**: This is built for companies that have:
- Customers who buy products
- Vendors who sell things
- Sales revenue tracking
- Traditional accounting (GL)
- Employee payroll
- Sales pipeline management

---

## New Schema (Correct ✅)

Designed for a **non-profit immigration service organization**:

```
Beneficiaries (People we help)
         → Program Enrollments → Programs (Settlement, English, Work, etc)
         → Program Sessions & Attendance
         → Outcomes (job placements, English levels, settlement milestones)
         → Services Delivered (coaching, counseling, etc)
         → Job Placements
         → Settlement Milestones
         → Communication Log

Funding:
         → Donations (from donors)
         → Government Grants (from federal/provincial/municipal)
         → Expenses (program costs)

Staff/Volunteers
         → Services Delivered
         → Sessions Taught

Total: 14 tables
Focus: Beneficiary outcomes, Program impact, Funding utilization
```

**Solution**: This is built for organizations that:
- Serve beneficiaries/participants (not customers)
- Deliver programs (not products)
- Track outcomes (not revenue)
- Receive donations and grants (not customer payments)
- Measure impact (not profit)
- Track volunteers and staff (not payroll)

---

## Side-by-Side Comparison

| Aspect | Old (Commercial) | New (Non-Profit) |
|--------|------------------|------------------|
| **Core Entity** | Customers | Beneficiaries |
| **Transactions** | Sales, Purchases | Program Enrollments |
| **Products** | Inventory | Programs & Services |
| **Financial** | GL, Revenue, COGS | Donations, Grants, Expenses |
| **Outcomes** | Profit Margin | Job Placements, Settlement Success |
| **Staff** | Employees with Payroll | Staff & Volunteers |
| **Success Metric** | Revenue & Profit | Lives Changed & Impact |

---

## What Tables Were Added/Removed

### Removed (Not needed for non-profit):
- ❌ `organizations` (hierarchy) - Simplified
- ❌ `departments` (org structure) - Simplified
- ❌ `employees` (traditional payroll)
- ❌ `contacts` (generic customers/vendors) → Replaced with `beneficiaries` + `staff_volunteers`
- ❌ `products` (inventory) → Replaced with `programs`
- ❌ `sales_transactions` & `sales_line_items` → Replaced with `program_enrollments`
- ❌ `purchase_transactions` & `purchase_line_items` → Not needed
- ❌ `gl_transactions` (traditional accounting) → Simplified to just track expenses
- ❌ `payroll_records` & `payroll_deductions` → Not needed for volunteers
- ❌ `crm_opportunities` & `crm_activities` → Replaced with `services_delivered`
- ❌ `hr_leave_requests` → Not applicable to volunteers

**Total removed: 20 - 14 = 6 tables eliminated**

### Added (Specific to immigration services):
- ✅ `beneficiaries` - People we serve
- ✅ `programs` - 5 programs (Settlement, English, Work, Refugee, Mentoring)
- ✅ `program_enrollments` - Who enrolled in what
- ✅ `program_sessions` - Individual classes/workshops
- ✅ `session_attendance` - Tracking attendance
- ✅ `outcomes` - Achievement tracking (job placement, English level, etc)
- ✅ `services_delivered` - Individual services (coaching, counseling)
- ✅ `job_placements` - Successful employment
- ✅ `settlement_milestones` - Life achievements (housing, banking, health cards)
- ✅ `communication_log` - Interaction tracking
- ✅ `donations` - Donor records
- ✅ `government_grants` - Grant funding tracking
- ✅ `expenses` - Budget and spending
- ✅ `staff_volunteers` - Both paid and volunteer contributors

---

## Sample Queries: Before vs After

### Before (Commercial Model - Wrong)

**Q: "How much did we sell?"**
```sql
SELECT SUM(total_amount) FROM sales_transactions WHERE status = 'Paid';
```

### After (Non-Profit Model - Right)

**Q: "How many beneficiaries found jobs?"**
```sql
SELECT COUNT(*) FROM job_placements 
WHERE employment_type = 'Full-time';
```

---

## Database Size Implications

| Aspect | Before | After |
|--------|--------|-------|
| Tables | 20 | 14 |
| Relationships | 25+ | 20 |
| Typical Row Count | Sales: 1000+, GL: 5000+ | Beneficiaries: 200-500, Outcomes: 500-1000 |
| Query Complexity | High (GL reconciliation) | Medium (outcome tracking) |
| Real-time Needs | High (transactions) | Low (periodic reports) |

---

## Deployment Impact

### Database Choice

**Before**: MySQL or PostgreSQL (full-featured relational DB)
- **Reason**: High transaction volume, complex accounting
- **Problem**: Overkill for non-profit; adds complexity

**After**: SQLite (embedded database)
- **Reason**: Low transaction volume, episodic reporting
- **Benefit**: Zero setup, portable, deployable with API
- **Advantage**: Perfect for demo and MVP

---

## What This Means for Your Demo

### Old Direction ❌
- Complex database with 20 tables
- MySQL setup required
- GL accounting reconciliation
- Sales pipeline tracking
- Not relevant to ISSOFBC's actual business

### New Direction ✅
- Simplified 14-table schema
- SQLite - runs everywhere
- Beneficiary outcome tracking
- Program impact measurement
- Perfect for ISSOFBC's immigration services

---

## Going Forward

### Use the New Schema For:
✅ Demo (this week)
✅ MVP (next 4 weeks)
✅ Production (ongoing)

### Never Use the Old Schema For:
❌ ISSOFBC (wrong business model)
❌ Any non-profit immigration services org
❌ Any social services organization

---

## Key Lessons

1. **Schema design must match business model**
   - A commercial business schema doesn't work for non-profits
   - Non-profits need outcome metrics, not profit metrics

2. **SQLite is perfect for non-profits**
   - Low cost
   - Easy to deploy
   - No infrastructure needed
   - Can migrate to PostgreSQL later if needed

3. **Documentation is crucial**
   - Showed you the wrong schema first
   - Corrected it when you clarified the business model
   - Now you have the RIGHT schema for your actual needs

---

## Files Updated/Corrected

| File | Status | Notes |
|------|--------|-------|
| `README.md` | ✅ Updated | Now describes non-profit model |
| `SCHEMA_NONPROFIT.md` | ✅ New | Correct schema for immigration services |
| `schema_sqlite.sql` | ✅ New | SQLite version with 14 tables |
| `generate_sample_data_sqlite.py` | ✅ New | Sample data for non-profit model |
| `QUICKSTART_SQLITE.md` | ✅ New | Demo setup guide |
| `DEMO_READY.md` | ✅ New | Demo walkthrough |
| `DATABASE_SCHEMA_DESIGN.md` | ⚠️ Old | Keep for reference, don't use |
| `schema.sql` | ⚠️ Old | Keep for reference, don't use |
| `schema.yaml` | ⚠️ Old | Keep for reference, don't use |

---

## Timeline Impact

Old approach (wrong schema):
- Setup: 2 hours (MySQL)
- Data generation: 1 hour
- Total: 3 hours
- **Problem**: Wrong for your use case

New approach (correct schema):
- Setup: 5 minutes (SQLite)
- Data generation: 1 minute
- Total: 6 minutes
- **Better**: Right for your use case

**Net savings**: Actually faster AND more appropriate!

---

## Questions?

This document explains:
- ✅ What changed
- ✅ Why it changed
- ✅ How it benefits you
- ✅ What to use for demo

If you have specific questions, refer to:
- `SCHEMA_NONPROFIT.md` - Data model details
- `QUICKSTART_SQLITE.md` - Setup and testing
- `DEMO_READY.md` - Demo flow

---

**Corrected**: April 22, 2026  
**Status**: ✅ Schema Now Matches Your Business Model

