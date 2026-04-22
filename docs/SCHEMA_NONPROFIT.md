# ISSOFBC Database Schema - Non-Profit Immigration Services

## Project Context

**Organization**: IISofBC (Immigration Integration Services of BC)  
**Type**: Non-Profit Immigration Services Organization  
**Programs**: Settlement, English Learning, Employment Support, Refugee Services  
**Funding**: Government Grants + Donations

---

## Core Entities

### 1. Beneficiaries (People We Help)

```yaml
beneficiaries:
  - beneficiary_id (PK)
  - status (Active, Completed, Inactive)
  - first_name
  - last_name
  - date_of_birth
  - gender (M/F/Other)
  - immigration_status (Refugee, Permanent Resident, Citizen, Work Permit, Study Permit)
  - arrival_date (when they came to Canada)
  - primary_language (native language)
  - english_proficiency_start (A1-C2 CEFR level at intake)
  - country_of_origin
  - household_size
  - income_level_start
  - contact_phone
  - contact_email
  - referred_by
  - created_date
  - updated_date
```

### 2. Programs (What We Offer)

```yaml
programs:
  - program_id (PK)
  - program_code (SETTLE, ENGLISH, WORK, REFUGEE)
  - program_name (Settlement Program, English Learning Program, etc)
  - description
  - program_type (Group, Individual, Online, Hybrid)
  - target_audience (Refugees, Economic Immigrants, All)
  - duration_weeks
  - frequency (Weekly, Bi-weekly, etc)
  - max_capacity
  - budget_allocated (annual budget for this program)
  - created_date
```

### 3. Program Enrollments

```yaml
program_enrollments:
  - enrollment_id (PK)
  - beneficiary_id (FK)
  - program_id (FK)
  - enrollment_date
  - status (Active, Completed, Dropped Out, On Hold)
  - completion_date
  - attendance_rate (percent)
  - notes
  - created_date
```

### 4. Staff & Volunteers

```yaml
staff_volunteers:
  - person_id (PK)
  - first_name
  - last_name
  - email
  - phone
  - person_type (Staff, Volunteer, Contractor)
  - employment_status (Active, Inactive)
  - department (Program Management, Outreach, Finance, Operations)
  - roles (Counselor, Instructor, Mentor, Coordinator)
  - languages_spoken
  - hire_date
  - salary_hourly_rate (if applicable)
  - volunteer_hours_target (annual)
  - created_date
```

### 5. Program Sessions

```yaml
program_sessions:
  - session_id (PK)
  - program_id (FK)
  - session_number (1, 2, 3...)
  - start_date
  - end_date
  - instructor_id (FK -> staff_volunteers)
  - location (office, online, partner site)
  - session_type (Workshop, Class, Consultation, Group Activity)
  - max_capacity
  - material_topic
  - created_date
```

### 6. Session Attendance

```yaml
session_attendance:
  - attendance_id (PK)
  - session_id (FK)
  - beneficiary_id (FK)
  - attended (Yes/No)
  - arrival_time
  - departure_time
  - notes (e.g., left early, first time, engaged well)
  - created_date
```

### 7. Outcomes & Progress Tracking

```yaml
outcomes:
  - outcome_id (PK)
  - beneficiary_id (FK)
  - outcome_type (English Test, Job Placement, Settlement Milestone, Health ID Obtained, Housing Secured, etc)
  - program_id (FK - nullable, outcome may not be tied to specific program)
  - metric_name (IELTS Score, CLB Level, Job Title, Salary, etc)
  - metric_value (numeric or text)
  - metric_date
  - created_date
```

### 8. Donations & Funding

```yaml
donations:
  - donation_id (PK)
  - donor_name
  - donor_type (Individual, Corporate, Foundation, Anonymous)
  - donation_amount
  - donation_date
  - donation_type (Cash, In-kind, Pledge)
  - item_type (for in-kind: clothing, furniture, food, equipment)
  - quantity
  - purpose (General, Specific Program, Emergency Support)
  - tax_receipt_issued (Yes/No)
  - receipt_number
  - notes
  - created_date
```

### 9. Government Grants

```yaml
government_grants:
  - grant_id (PK)
  - grant_name
  - grant_number
  - funding_source (Federal, Provincial, Municipal)
  - program_id (FK)
  - grant_amount
  - grant_year
  - start_date
  - end_date
  - reporting_requirements (text)
  - amount_claimed_ytd
  - amount_approved_ytd
  - status (Active, Completed, Pending Approval)
  - notes
  - created_date
```

### 10. Expenses

```yaml
expenses:
  - expense_id (PK)
  - expense_date
  - category (Program Delivery, Materials, Staff, Admin, Volunteer Appreciation, etc)
  - description
  - amount
  - vendor_name
  - approval_status (Submitted, Approved, Rejected, Reimbursed)
  - approved_by (staff_id)
  - program_id (FK - which program this expense supports)
  - grant_id (FK - charged to which grant)
  - receipt_attached (Yes/No)
  - created_date
```

### 11. Services Provided (Detailed)

```yaml
services_delivered:
  - service_id (PK)
  - beneficiary_id (FK)
  - service_type (Career Coaching, Resume Writing, Job Interview Prep, ESL Class, Settlement Counseling, etc)
  - provider_id (FK -> staff_volunteers)
  - service_date
  - duration_minutes
  - location
  - outcome_description (what was accomplished)
  - follow_up_needed (Yes/No)
  - notes
  - created_date
```

### 12. Job Placements

```yaml
job_placements:
  - placement_id (PK)
  - beneficiary_id (FK)
  - job_title
  - employer_name
  - placement_date
  - employment_type (Full-time, Part-time, Contract, Self-employed)
  - salary_range_start
  - status (Active, Completed - Left, Completed - Terminated)
  - end_date
  - industry_sector
  - match_score (how well the job matched their profile)
  - created_date
```

### 13. Settlement Milestones

```yaml
settlement_milestones:
  - milestone_id (PK)
  - beneficiary_id (FK)
  - milestone_type (SIN Obtained, Bank Account Opened, Child in School, Provincial ID, Housing Secured, Health Card, Job Found, Professional License Started)
  - milestone_date
  - notes
  - supporting_staff_id (FK)
  - created_date
```

### 14. Communication Log

```yaml
communication_log:
  - comm_id (PK)
  - beneficiary_id (FK)
  - staff_id (FK)
  - communication_type (Phone, Email, In-Person, SMS, Other)
  - subject
  - notes
  - outcome
  - next_action_required (Yes/No)
  - comm_date
  - created_date
```

---

## Key Relationships

```
beneficiaries
  ├─ program_enrollments → programs
  ├─ session_attendance → program_sessions → programs
  ├─ outcomes
  ├─ donations (referrer)
  ├─ services_delivered → staff_volunteers
  ├─ job_placements
  ├─ settlement_milestones
  └─ communication_log → staff_volunteers

programs
  ├─ program_enrollments → beneficiaries
  ├─ program_sessions
  ├─ government_grants
  └─ expenses

staff_volunteers
  ├─ program_sessions (instructor)
  ├─ services_delivered
  └─ communication_log

government_grants
  └─ expenses

donations
  └─ potentially linked to specific program needs
```

---

## Key Metrics for Reporting

### Beneficiary Metrics
- Total active beneficiaries
- Beneficiaries by immigration status
- Beneficiaries by language of origin
- New intakes per month

### Program Engagement
- Enrollment by program
- Completion rate by program
- Attendance rate (program-level)
- Dropout rate

### Outcomes
- % of participants who improved English level
- Average job placement rate
- Average time to job placement
- Settlement milestones achieved

### Funding
- Total donations received (monthly, yearly)
- Government grant funding
- Cost per beneficiary served
- Program budget utilization

### Staff/Volunteer
- Total volunteer hours
- Cost per volunteer hour
- Staff utilization rate
- Languages available (staff capabilities)

---

## Sample Dashboards

### 1. Program Performance Dashboard
```
- Total Enrollments by Program
- Completion Rates
- Attendance Trends
- Outcomes per Program (jobs placed, settlements, etc)
```

### 2. Beneficiary Progress Dashboard
```
- New Arrivals (monthly)
- English Proficiency Improvements
- Job Placements
- Settlement Milestones Achieved
- Time to Employment
```

### 3. Funding & Budget Dashboard
```
- Total Donations vs Budget
- Grant Funding Status
- Expenses vs Budget by Program
- Cost per Beneficiary by Program
```

### 4. Operational Dashboard
```
- Staff/Volunteer Availability
- Service Delivery (sessions, availability)
- Pending Follow-ups
- Referral Sources
```

---

## Sample Queries

### Q1: How many beneficiaries completed the English program this quarter?
```sql
SELECT 
  COUNT(DISTINCT pe.beneficiary_id) as completed_count,
  AVG(CASE WHEN o.metric_name = 'CLB Level' THEN o.metric_value END) as avg_final_level
FROM program_enrollments pe
JOIN programs p ON pe.program_id = p.program_id
LEFT JOIN outcomes o ON pe.beneficiary_id = o.beneficiary_id
WHERE p.program_code = 'ENGLISH'
  AND pe.status = 'Completed'
  AND QUARTER(pe.completion_date) = QUARTER(CURDATE())
```

### Q2: What's our job placement rate for this year?
```sql
SELECT 
  COUNT(DISTINCT jp.beneficiary_id) as placements,
  COUNT(DISTINCT pe.beneficiary_id) as program_completions,
  ROUND(COUNT(DISTINCT jp.beneficiary_id) / COUNT(DISTINCT pe.beneficiary_id) * 100, 2) as placement_rate_pct
FROM job_placements jp
JOIN program_enrollments pe ON jp.beneficiary_id = pe.beneficiary_id
WHERE YEAR(jp.placement_date) = YEAR(CURDATE())
  AND pe.program_id = (SELECT program_id FROM programs WHERE program_code = 'WORK')
```

### Q3: How are donations trending vs government grants?
```sql
SELECT 
  DATE_TRUNC('month', donation_date) as month,
  SUM(CASE WHEN donation_type = 'Cash' THEN donation_amount ELSE 0 END) as donation_amount,
  (SELECT SUM(grant_amount) FROM government_grants WHERE MONTH(start_date) = MONTH(donation_date)) as grant_amount
FROM donations
GROUP BY DATE_TRUNC('month', donation_date)
ORDER BY month DESC
```

### Q4: Which staff/volunteers have the highest service delivery volume?
```sql
SELECT 
  CONCAT(sv.first_name, ' ', sv.last_name) as name,
  COUNT(sd.service_id) as services_delivered,
  SUM(sd.duration_minutes) / 60 as hours_served,
  COUNT(DISTINCT sd.beneficiary_id) as unique_beneficiaries
FROM staff_volunteers sv
LEFT JOIN services_delivered sd ON sv.person_id = sd.provider_id
WHERE sv.employment_status = 'Active'
GROUP BY sv.person_id
ORDER BY services_delivered DESC
```

---

## Migration Considerations

### Data Import from Current Systems
- Where do you currently store beneficiary info?
- How are program enrollments currently tracked?
- Where are donations/grants recorded?
- Are there existing systems to extract from?

---

## Next Steps

1. ✅ Design schema for non-profit (DONE)
2. ⏳ Convert to SQLite DDL
3. ⏳ Create sample data
4. ⏳ Update API examples for non-profit use cases
5. ⏳ Design non-profit focused dashboard examples

