"""
Sample Data Generator for ISSOFBC Staging Database
Simulates data from 4 source systems:
  - Newtract (CRM / D365)  → clients, programs, outcomes
  - Business Central (Finance) → donations, grants, GL, budget
  - BambooHR (HR)          → departments, employees, leave, reviews
  - Paywork (Payroll)      → pay runs, pay stubs

Usage:
    python generate_sample_data_sqlite.py

Requires:
    pip install faker
"""

import sqlite3
import random
from datetime import datetime, timedelta, date
from pathlib import Path

try:
    from faker import Faker
except ImportError:
    print("Please install required packages:")
    print("  pip install faker")
    exit(1)

_ROOT = Path(__file__).parent.parent
DB_PATH     = str(_ROOT / "database" / "issofbc.db")
SCHEMA_PATH = str(_ROOT / "database" / "schema_sqlite.sql")

fake = Faker()
Faker.seed(42)
random.seed(42)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn):
    conn.executescript(Path(SCHEMA_PATH).read_text())
    conn.commit()
    print("✓ Database schema created")


def rand_date(start_days_ago=730, end_days_ago=0):
    start = date.today() - timedelta(days=start_days_ago)
    end   = date.today() - timedelta(days=end_days_ago)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def biweekly_periods(start: date, end: date):
    """Yield (period_start, period_end, pay_date) bi-weekly from start to end."""
    cursor = start
    while cursor < end:
        period_end = cursor + timedelta(days=13)
        pay_date   = period_end + timedelta(days=4)
        yield cursor, min(period_end, end), pay_date
        cursor = period_end + timedelta(days=1)


# ---------------------------------------------------------------------------
# Newtract (CRM/D365) — existing nonprofit domain tables
# ---------------------------------------------------------------------------

def generate_programs(conn):
    print("\n🎓 Generating programs...")
    programs = [
        ("EMP", "Employment Support",
         "Job search assistance, resume writing, interview preparation",
         "Group", "Newcomers", 12, "Weekly", 30, 85000.00),
        ("ENG", "English Learning",
         "ESL classes for all proficiency levels",
         "Group", "All Immigrants", 24, "3x per week", 20, 120000.00),
        ("SET", "Settlement Program",
         "General settlement services for newly arrived clients",
         "Individual", "Newcomers", 8, "As needed", 50, 95000.00),
        ("REF", "Refugee Integration",
         "Specialized holistic support for government-assisted refugees",
         "Hybrid", "Refugees", 16, "Weekly", 25, 110000.00),
        ("MEN", "Mentoring & Counseling",
         "One-on-one mentoring and mental health counseling services",
         "Individual", "All Clients", 20, "Bi-weekly", 15, 75000.00),
    ]
    conn.executemany("""
        INSERT INTO programs
            (program_code, program_name, description, program_type,
             target_audience, duration_weeks, frequency, max_capacity,
             budget_allocated, is_active)
        VALUES (?,?,?,?,?,?,?,?,?,1)
    """, programs)
    conn.commit()
    print(f"  ✓ Inserted {len(programs)} programs")
    return [r[0] for r in conn.execute("SELECT program_id FROM programs")]


def generate_staff_volunteers(conn, count=20):
    print(f"\n👥 Generating {count} staff/volunteers...")
    person_types = (["Staff"] * 12) + (["Volunteer"] * 5) + (["Contractor"] * 3)
    departments  = ["Programs", "Finance", "Admin", "Outreach", "Counseling"]
    languages    = ["English, French", "English, Mandarin", "English, Arabic",
                    "English, Spanish", "English, Punjabi", "English, Tagalog", "English"]
    records = []
    for i in range(count):
        ptype = person_types[i] if i < len(person_types) else "Staff"
        records.append((
            fake.first_name(), fake.last_name(),
            f"staff{i+1}@issofbc.org", fake.phone_number(),
            ptype, "Active",
            random.choice(departments),
            "Case Worker" if ptype == "Staff" else ("Volunteer" if ptype == "Volunteer" else "Contractor"),
            random.choice(languages),
            str(rand_date(1825, 90)),
            round(random.uniform(18, 45), 2) if ptype != "Staff" else None,
            random.randint(50, 200) if ptype == "Volunteer" else None,
        ))
    conn.executemany("""
        INSERT INTO staff_volunteers
            (first_name, last_name, email, phone, person_type, employment_status,
             department, roles, languages_spoken, hire_date,
             salary_hourly_rate, volunteer_hours_target)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} staff/volunteers")
    return [r[0] for r in conn.execute("SELECT person_id FROM staff_volunteers")]


def generate_beneficiaries(conn, count=200):
    print(f"\n🌍 Generating {count} beneficiaries...")
    statuses      = (["Active"] * 3) + ["Completed", "Inactive"]
    imm_statuses  = ["Refugee", "Refugee", "Permanent Resident",
                     "Work Permit", "Study Permit", "Citizen"]
    languages     = ["Arabic", "Mandarin", "Spanish", "Tagalog", "Punjabi",
                     "Somali", "Ukrainian", "French", "Hindi", "Persian"]
    proficiencies = ["None", "Basic", "Intermediate", "Advanced"]
    countries     = ["Syria", "China", "Philippines", "India", "Mexico",
                     "Somalia", "Ukraine", "Nigeria", "Vietnam", "Iran"]
    records = []
    for _ in range(count):
        records.append((
            random.choice(statuses),
            fake.first_name(), fake.last_name(),
            str(rand_date(365*50, 365*18)),
            random.choice(["M", "F", "Other"]),
            random.choice(imm_statuses),
            str(rand_date(1825, 30)),
            random.choice(languages),
            random.choice(proficiencies),
            random.choice(countries),
            random.randint(1, 7),
            round(random.uniform(0, 45000), 2),
            fake.phone_number(), fake.email(),
            random.choice(["Community referral", "Self-referral",
                           "Government", "Other org", None]),
        ))
    conn.executemany("""
        INSERT INTO beneficiaries
            (status, first_name, last_name, date_of_birth, gender,
             immigration_status, arrival_date, primary_language,
             english_proficiency_start, country_of_origin, household_size,
             income_level_start, contact_phone, contact_email, referred_by)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} beneficiaries")
    return [r[0] for r in conn.execute("SELECT beneficiary_id FROM beneficiaries")]


def generate_enrollments(conn, beneficiary_ids, program_ids):
    print("\n📝 Generating program enrollments...")
    statuses = (["Active"] * 2) + ["Completed", "Dropped Out", "On Hold"]
    records, enrolled = [], set()
    for b_id in beneficiary_ids:
        for p_id in random.sample(program_ids, random.randint(1, 3)):
            if (b_id, p_id) in enrolled:
                continue
            enrolled.add((b_id, p_id))
            status     = random.choice(statuses)
            enroll_dt  = rand_date(365, 0)
            compl_date = str(rand_date(30, 0)) if status == "Completed" else None
            records.append((b_id, p_id, str(enroll_dt), status,
                            compl_date, round(random.uniform(50, 100), 1), None))
    conn.executemany("""
        INSERT INTO program_enrollments
            (beneficiary_id, program_id, enrollment_date, status,
             completion_date, attendance_rate, notes)
        VALUES (?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} enrollments")


def generate_sessions(conn, program_ids, staff_ids):
    print("\n📅 Generating program sessions...")
    s_types    = ["Workshop", "Class", "Consultation", "Group Activity"]
    locations  = ["Main Hall", "Room 101", "Room 202", "Online", "Community Centre"]
    records = []
    for p_id in program_ids:
        for i in range(random.randint(8, 20)):
            start = rand_date(300, 0)
            records.append((
                p_id, i + 1, str(start), str(start + timedelta(days=1)),
                random.choice(staff_ids), random.choice(locations),
                random.choice(s_types), random.randint(10, 25),
                f"Session {i+1} topic",
            ))
    conn.executemany("""
        INSERT INTO program_sessions
            (program_id, session_number, start_date, end_date,
             instructor_id, location, session_type, max_capacity, material_topic)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} sessions")


def generate_services(conn, beneficiary_ids, staff_ids, count=400):
    print(f"\n🤝 Generating {count} services delivered...")
    s_types = ["Case Management", "Language Assessment", "Employment Counseling",
               "Interpretation", "Settlement Assistance", "Mental Health Support",
               "Legal Aid Referral", "Housing Support"]
    records = [(
        random.choice(beneficiary_ids), random.choice(s_types),
        random.choice(staff_ids), str(rand_date(365, 0)),
        random.randint(15, 120),
        random.choice(["Office", "Phone", "Online", "Community"]),
        fake.sentence(), random.random() < 0.3, None,
    ) for _ in range(count)]
    conn.executemany("""
        INSERT INTO services_delivered
            (beneficiary_id, service_type, provider_id, service_date,
             duration_minutes, location, outcome_description, follow_up_needed, notes)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} services")


def generate_job_placements(conn, beneficiary_ids, count=80):
    print(f"\n💼 Generating {count} job placements...")
    industries = ["Food & Hospitality", "Retail", "Healthcare Support", "IT",
                  "Manufacturing", "Education", "Transportation",
                  "Construction", "Finance", "Other"]
    emp_types  = ["Full-time", "Part-time", "Contract", "Self-employed"]
    sample     = random.sample(beneficiary_ids, min(count, len(beneficiary_ids)))
    records = [(
        b_id, fake.job(), fake.company(), str(rand_date(365, 0)),
        random.choice(emp_types),
        round(random.uniform(15, 45) * 2080, 2),
        random.choice(["Active", "Completed - Left", "Completed - Terminated"]),
        None, random.choice(industries),
        round(random.uniform(0.5, 1.0), 2),
    ) for b_id in sample]
    conn.executemany("""
        INSERT INTO job_placements
            (beneficiary_id, job_title, employer_name, placement_date,
             employment_type, salary_range_start, status, end_date,
             industry_sector, match_score)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} job placements")


def generate_outcomes(conn, beneficiary_ids, program_ids, count=300):
    print(f"\n🏆 Generating {count} outcomes...")
    o_types = ["Employment", "Language Improvement", "Housing Secured",
               "Citizenship Achieved", "Program Completion",
               "Social Integration", "Financial Stability"]
    records = [(
        random.choice(beneficiary_ids), random.choice(o_types),
        random.choice(program_ids), fake.word(),
        str(random.randint(1, 10)), str(rand_date(365, 0)),
    ) for _ in range(count)]
    conn.executemany("""
        INSERT INTO outcomes
            (beneficiary_id, outcome_type, program_id, metric_name,
             metric_value, metric_date)
        VALUES (?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} outcomes")


def generate_milestones(conn, beneficiary_ids, staff_ids, count=250):
    print(f"\n🎯 Generating {count} settlement milestones...")
    m_types = ["SIN Obtained", "Health Card Obtained", "Bank Account Opened",
               "School Enrollment", "Driver's License", "Permanent Residency",
               "First Job", "Own Housing", "Citizenship Application"]
    records = [(
        random.choice(beneficiary_ids), random.choice(m_types),
        str(rand_date(730, 0)), None, random.choice(staff_ids),
    ) for _ in range(count)]
    conn.executemany("""
        INSERT INTO settlement_milestones
            (beneficiary_id, milestone_type, milestone_date,
             notes, supporting_staff_id)
        VALUES (?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} milestones")


def generate_communications(conn, beneficiary_ids, staff_ids, count=350):
    print(f"\n📞 Generating {count} communication logs...")
    c_types = ["Phone", "Email", "In-Person", "SMS", "Other"]
    records = []
    for _ in range(count):
        d = rand_date(365, 0)
        records.append((
            random.choice(beneficiary_ids), random.choice(staff_ids),
            random.choice(c_types), fake.sentence(nb_words=6),
            fake.sentence(),
            random.choice(["Resolved", "Follow-up scheduled", "No action needed"]),
            random.random() < 0.25,
            str(datetime.combine(d, datetime.min.time())),
        ))
    conn.executemany("""
        INSERT INTO communication_log
            (beneficiary_id, staff_id, communication_type, subject,
             notes, outcome, next_action_required, comm_date)
        VALUES (?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} communication records")


# ---------------------------------------------------------------------------
# Business Central (Finance) — donations, grants, expenses + GL + budget
# ---------------------------------------------------------------------------

def generate_donations(conn, count=150):
    print(f"\n💰 Generating {count} donations...")
    d_types  = ["Individual", "Corporate", "Foundation", "Anonymous"]
    purposes = ["General Fund", "Employment Program", "English Classes",
                "Refugee Integration", "Unrestricted"]
    records = []
    for i in range(count):
        dtype = random.choice(d_types)
        records.append((
            fake.name() if dtype != "Anonymous" else "Anonymous",
            dtype,
            round(random.uniform(25, 10000), 2),
            str(rand_date(730, 0)),
            random.choice(["Cash", "In-kind", "Pledge"]),
            None, None,
            random.choice(purposes), True,
            f"RCP{2024000 + i}", None,
        ))
    conn.executemany("""
        INSERT INTO donations
            (donor_name, donor_type, donation_amount, donation_date,
             donation_type, item_type, quantity, purpose,
             tax_receipt_issued, receipt_number, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    total = conn.execute(
        "SELECT SUM(donation_amount) FROM donations WHERE donation_type='Cash'"
    ).fetchone()[0] or 0
    print(f"  ✓ Inserted {count} donations (Cash total: ${total:,.2f})")


def generate_grants(conn, program_ids):
    print("\n🏛️  Generating government grants...")
    grants = [
        ("IRCC Settlement Fund 2024",   "IRCC-2024-001", "Federal",   program_ids[2], 250000, 2024),
        ("IRCC Language Training 2024",  "IRCC-2024-002", "Federal",   program_ids[1], 180000, 2024),
        ("BC Employment Program 2024",   "BC-2024-015",   "Provincial", program_ids[0],  95000, 2024),
        ("BC Refugee Support 2024",      "BC-2024-022",   "Provincial", program_ids[3], 120000, 2024),
        ("City of Vancouver Grant 2024", "COV-2024-008",  "Municipal",  program_ids[4],  45000, 2024),
        ("IRCC Settlement Fund 2025",   "IRCC-2025-001", "Federal",   program_ids[2], 265000, 2025),
        ("IRCC Language Training 2025",  "IRCC-2025-002", "Federal",   program_ids[1], 195000, 2025),
        ("BC Employment Program 2025",   "BC-2025-018",   "Provincial", program_ids[0], 105000, 2025),
        ("BC Refugee Support 2025",      "BC-2025-031",   "Provincial", program_ids[3], 130000, 2025),
        ("City of Vancouver Grant 2025", "COV-2025-004",  "Municipal",  program_ids[4],  50000, 2025),
    ]
    records = []
    for name, gnum, source, pid, amount, year in grants:
        claimed = round(amount * random.uniform(0.4, 0.95), 2)
        records.append((
            name, gnum, source, pid, amount, year,
            f"{year}-04-01", f"{year+1}-03-31",
            "Quarterly narrative and financial reports required",
            claimed, claimed, "Active", None,
        ))
    conn.executemany("""
        INSERT INTO government_grants
            (grant_name, grant_number, funding_source, program_id,
             grant_amount, grant_year, start_date, end_date,
             reporting_requirements, amount_claimed_ytd,
             amount_approved_ytd, status, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} grants")


def generate_expenses(conn, staff_ids, program_ids, count=200):
    print(f"\n🧾 Generating {count} expenses...")
    categories = ["Salaries", "Rent", "Supplies", "Technology",
                  "Training", "Events", "Translation", "Travel",
                  "Advertising", "Insurance", "Audit Fees"]
    records = [(
        str(rand_date(730, 0)), random.choice(categories),
        fake.sentence(nb_words=5),
        round(random.uniform(50, 5000), 2),
        fake.company(),
        random.choice(["Approved", "Approved", "Submitted",
                       "Rejected", "Reimbursed"]),
        random.choice(staff_ids), random.choice(program_ids), None, True,
    ) for _ in range(count)]
    conn.executemany("""
        INSERT INTO expenses
            (expense_date, category, description, amount, vendor_name,
             approval_status, approved_by, program_id, grant_id,
             receipt_attached)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} expenses")


def generate_gl_accounts(conn):
    print("\n📊 Generating GL chart of accounts...")
    accounts = [
        # Assets
        ("1000", "Cash and Cash Equivalents",         "Asset",     "Current Assets"),
        ("1100", "Accounts Receivable - Gov Grants",  "Asset",     "Current Assets"),
        ("1110", "Accounts Receivable - Donations",   "Asset",     "Current Assets"),
        ("1200", "Prepaid Expenses",                  "Asset",     "Current Assets"),
        ("1300", "Security Deposits",                 "Asset",     "Non-current Assets"),
        # Liabilities
        ("2000", "Accounts Payable",                  "Liability", "Current Liabilities"),
        ("2100", "Accrued Salaries and Benefits",     "Liability", "Current Liabilities"),
        ("2200", "Deferred Revenue - Gov Grants",     "Liability", "Current Liabilities"),
        ("2300", "GST/HST Payable",                   "Liability", "Current Liabilities"),
        # Equity
        ("3000", "Net Assets - Unrestricted",         "Equity",    "Net Assets"),
        ("3100", "Net Assets - Restricted",           "Equity",    "Net Assets"),
        # Revenue
        ("4000", "Government Grants - Federal",       "Revenue",   "Grant Revenue"),
        ("4010", "Government Grants - Provincial",    "Revenue",   "Grant Revenue"),
        ("4020", "Government Grants - Municipal",     "Revenue",   "Grant Revenue"),
        ("4100", "Individual Donations",              "Revenue",   "Donation Revenue"),
        ("4200", "Corporate Donations",               "Revenue",   "Donation Revenue"),
        ("4300", "Foundation Grants",                 "Revenue",   "Donation Revenue"),
        ("4400", "Program Fees",                      "Revenue",   "Other Revenue"),
        ("4500", "Other Income",                      "Revenue",   "Other Revenue"),
        # Expenses
        ("5000", "Salaries - Full-time Staff",        "Expense",   "Personnel"),
        ("5010", "Salaries - Part-time / Contract",   "Expense",   "Personnel"),
        ("5100", "Employee Benefits (CPP/EI/Health)", "Expense",   "Personnel"),
        ("5200", "Rent and Utilities",                "Expense",   "Occupancy"),
        ("5300", "Office Supplies",                   "Expense",   "Operating"),
        ("5400", "Technology and Software",           "Expense",   "Operating"),
        ("5500", "Staff Training and Development",    "Expense",   "Operating"),
        ("5600", "Program Delivery Costs",            "Expense",   "Program"),
        ("5700", "Translation and Interpretation",    "Expense",   "Program"),
        ("5800", "Travel and Transportation",         "Expense",   "Operating"),
        ("5900", "Advertising and Outreach",          "Expense",   "Operating"),
        ("5910", "Audit and Accounting Fees",         "Expense",   "Admin"),
        ("5920", "Insurance",                         "Expense",   "Admin"),
    ]
    conn.executemany("""
        INSERT INTO gl_accounts (account_code, account_name, account_type, account_category)
        VALUES (?,?,?,?)
    """, accounts)
    conn.commit()
    print(f"  ✓ Inserted {len(accounts)} GL accounts")
    # Return account_id keyed by code
    return {r[0]: r[1] for r in conn.execute(
        "SELECT account_code, account_id FROM gl_accounts"
    )}


def generate_gl_transactions(conn, account_map):
    print("\n📒 Generating GL transactions (2024–2025)...")
    records = []
    ref_num = 1

    for year in [2024, 2025]:
        ytd_salary = 0.0
        for month in range(1, 13):
            if year == 2025 and month > 4:
                break  # only up to Apr 2026 demo data
            d = date(year, month, 28)
            period = month

            # --- Monthly salary run (debit Salaries, credit Bank) ---
            salary = round(random.uniform(55000, 70000) / 12, 2)
            ytd_salary += salary
            records += [
                (account_map["5000"], str(d), year, period,
                 salary, 0, f"Monthly salaries - {year}-{month:02d}",
                 f"PAY-{year}-{month:02d}", "Payroll"),
                (account_map["1000"], str(d), year, period,
                 0, salary, f"Monthly salaries - {year}-{month:02d}",
                 f"PAY-{year}-{month:02d}", "Payroll"),
            ]

            # --- Monthly benefits (debit Benefits, credit Bank) ---
            benefits = round(salary * 0.12, 2)
            records += [
                (account_map["5100"], str(d), year, period,
                 benefits, 0, f"Benefits {year}-{month:02d}",
                 f"BEN-{year}-{month:02d}", "Payroll"),
                (account_map["1000"], str(d), year, period,
                 0, benefits, f"Benefits {year}-{month:02d}",
                 f"BEN-{year}-{month:02d}", "Payroll"),
            ]

            # --- Monthly rent (debit Rent, credit AP) ---
            rent = 8500.0
            records += [
                (account_map["5200"], str(d), year, period,
                 rent, 0, "Monthly rent - IISofBC office",
                 f"RENT-{year}-{month:02d}", "Expenses"),
                (account_map["2000"], str(d), year, period,
                 0, rent, "Monthly rent - IISofBC office",
                 f"RENT-{year}-{month:02d}", "Expenses"),
            ]

            # --- Monthly donations (debit Cash, credit Donation Revenue) ---
            don_cash = round(random.uniform(5000, 20000), 2)
            records += [
                (account_map["1000"], str(d), year, period,
                 don_cash, 0, f"Monthly donations received {year}-{month:02d}",
                 f"DON-{year}-{month:02d}", "Donations"),
                (account_map["4100"], str(d), year, period,
                 0, don_cash, f"Monthly donations received {year}-{month:02d}",
                 f"DON-{year}-{month:02d}", "Donations"),
            ]

            # --- Quarterly grant instalments ---
            if month in [4, 7, 10, 1]:
                grant_rev = round(random.uniform(60000, 90000), 2)
                records += [
                    (account_map["1100"], str(d), year, period,
                     grant_rev, 0, f"Grant instalment Q{(month//3)+1} {year}",
                     f"GRT-{year}-{ref_num:04d}", "Grants"),
                    (account_map["4000"], str(d), year, period,
                     0, grant_rev, f"Grant instalment Q{(month//3)+1} {year}",
                     f"GRT-{year}-{ref_num:04d}", "Grants"),
                ]
                ref_num += 1

            # --- Random operating expense ---
            op_exp = round(random.uniform(1000, 6000), 2)
            op_acct = random.choice(["5300", "5400", "5500", "5600",
                                     "5700", "5800", "5900"])
            records += [
                (account_map[op_acct], str(d), year, period,
                 op_exp, 0, f"Operating expenses {year}-{month:02d}",
                 f"EXP-{year}-{month:02d}-{ref_num}", "Expenses"),
                (account_map["2000"], str(d), year, period,
                 0, op_exp, f"Operating expenses {year}-{month:02d}",
                 f"EXP-{year}-{month:02d}-{ref_num}", "Expenses"),
            ]
            ref_num += 1

    conn.executemany("""
        INSERT INTO gl_transactions
            (account_id, transaction_date, fiscal_year, fiscal_period,
             debit_amount, credit_amount, description,
             reference_number, source_module)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} GL transaction lines")


def generate_budget_lines(conn, account_map, program_ids):
    print("\n📋 Generating budget lines (2024–2025)...")
    records = []
    for year in [2024, 2025]:
        budget_plan = [
            # (account_code, program_id_or_None, annual_budget)
            ("5000",  None,          700000),
            ("5010",  None,          120000),
            ("5100",  None,          100000),
            ("5200",  None,          102000),
            ("5300",  None,           15000),
            ("5400",  None,           25000),
            ("5500",  None,           12000),
            ("5600",  program_ids[0], 40000),
            ("5600",  program_ids[1], 50000),
            ("5600",  program_ids[2], 35000),
            ("5600",  program_ids[3], 45000),
            ("5600",  program_ids[4], 30000),
            ("5700",  None,           18000),
            ("5800",  None,            8000),
            ("5900",  None,           10000),
            ("5910",  None,           14000),
            ("5920",  None,            6000),
            ("4000",  None,          450000),
            ("4010",  None,          225000),
            ("4020",  None,           50000),
            ("4100",  None,          120000),
            ("4200",  None,           80000),
        ]
        for code, prog_id, annual in budget_plan:
            q = round(annual / 4, 2)
            actual = round(annual * random.uniform(0.7, 1.05), 2)
            records.append((
                year, account_map[code], prog_id, annual,
                q, q, q, q, actual, None,
            ))
    conn.executemany("""
        INSERT INTO budget_lines
            (fiscal_year, account_id, program_id, annual_budget,
             q1_budget, q2_budget, q3_budget, q4_budget,
             actual_ytd, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} budget lines")


# ---------------------------------------------------------------------------
# BambooHR (HR)
# ---------------------------------------------------------------------------

def generate_hr_departments(conn):
    print("\n🏢 Generating HR departments...")
    depts = [
        ("Programs",   "PROG", "CC-PROG"),
        ("Finance",    "FIN",  "CC-FIN"),
        ("Admin",      "ADM",  "CC-ADM"),
        ("Outreach",   "OUT",  "CC-OUT"),
        ("Counseling", "CNS",  "CC-CNS"),
    ]
    conn.executemany("""
        INSERT INTO hr_departments (department_name, department_code, cost_center)
        VALUES (?,?,?)
    """, depts)
    conn.commit()
    print(f"  ✓ Inserted {len(depts)} departments")
    dept_map = {r[0]: r[1] for r in conn.execute(
        "SELECT department_name, dept_id FROM hr_departments"
    )}
    return dept_map


def generate_hr_employees(conn, staff_ids, dept_map):
    print("\n👤 Generating HR employee records (BambooHR)...")
    dept_names = list(dept_map.keys())
    positions  = {
        "Programs":   ["Program Manager", "Case Worker", "Program Coordinator"],
        "Finance":    ["Finance Manager", "Bookkeeper", "Finance Officer"],
        "Admin":      ["Executive Director", "Office Manager", "Admin Assistant"],
        "Outreach":   ["Outreach Coordinator", "Community Liaison"],
        "Counseling": ["Senior Counselor", "Mental Health Counselor", "Settlement Worker"],
    }
    emp_types = {
        "Staff":      "Full-time",
        "Contractor": "Contract",
        "Volunteer":  "Casual",
    }

    # Look up person_type for each person_id
    ptype_map = {r[0]: r[1] for r in conn.execute(
        "SELECT person_id, person_type FROM staff_volunteers"
    )}

    records = []
    manager_id = None
    for i, person_id in enumerate(staff_ids):
        ptype    = ptype_map[person_id]
        dept_nm  = conn.execute(
            "SELECT department FROM staff_volunteers WHERE person_id=?", (person_id,)
        ).fetchone()[0]
        dept_id  = dept_map.get(dept_nm, dept_map[random.choice(dept_names)])
        pos_list = positions.get(dept_nm, ["Staff Member"])
        pos      = pos_list[i % len(pos_list)]
        emp_type = emp_types.get(ptype, "Full-time")
        annual   = round(random.uniform(45000, 90000), 2) if emp_type in ("Full-time", "Contract") else None
        hourly   = round(random.uniform(18, 35), 2) if emp_type == "Casual" else None
        start_dt = str(rand_date(1825, 90))

        records.append((
            person_id,
            f"EMP{1000 + i}",
            dept_id, pos, emp_type, "Active",
            start_dt, None, annual, hourly,
            manager_id,
            "Vancouver", "BC", 1 if emp_type == "Full-time" else 0,
        ))
        if i == 0:
            # first person becomes the default manager for subsequent records
            manager_id = None  # set after insert

    conn.executemany("""
        INSERT INTO hr_employees
            (person_id, employee_number, dept_id, position_title,
             employment_type, employment_status, start_date, end_date,
             annual_salary, hourly_rate, manager_hr_employee_id,
             city, province, benefits_enrolled)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} HR employee records")

    # Return map: person_id → hr_employee_id
    return {r[0]: r[1] for r in conn.execute(
        "SELECT person_id, hr_employee_id FROM hr_employees"
    )}


def generate_leave_requests(conn, hr_emp_ids, count=80):
    print(f"\n🏖️  Generating {count} leave requests...")
    l_types   = ["Vacation", "Vacation", "Sick", "Sick", "Maternity",
                 "Bereavement", "Unpaid", "Other"]
    statuses  = ["Approved", "Approved", "Approved", "Pending", "Rejected"]
    emp_list  = list(hr_emp_ids.values())
    records   = []
    for _ in range(count):
        emp_id   = random.choice(emp_list)
        approver = random.choice(emp_list)
        start    = rand_date(365, 0)
        days     = random.randint(1, 15)
        end      = start + timedelta(days=days - 1)
        records.append((
            emp_id, random.choice(l_types),
            str(start), str(end), float(days),
            random.choice(statuses), approver, None,
        ))
    conn.executemany("""
        INSERT INTO hr_leave_requests
            (hr_employee_id, leave_type, start_date, end_date,
             total_days, status, approved_by_hr_employee_id, reason)
        VALUES (?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {count} leave requests")


def generate_performance_reviews(conn, hr_emp_ids):
    print("\n⭐ Generating performance reviews...")
    emp_list = list(hr_emp_ids.values())
    records  = []
    for emp_id in emp_list:
        reviewer = random.choice(emp_list)
        for year in [2024, 2025]:
            for period in ["Mid-Year", "Annual"]:
                records.append((
                    emp_id, year, period,
                    random.randint(2, 5), reviewer,
                    str(date(year, 6 if period == "Mid-Year" else 12,
                             random.randint(1, 28))),
                    random.choice(["All goals met", "Most goals met",
                                   "Partially met", "Exceeded expectations"]),
                    fake.sentence(),
                ))
    conn.executemany("""
        INSERT INTO hr_performance_reviews
            (hr_employee_id, review_year, review_period,
             overall_rating, reviewer_hr_employee_id, review_date,
             goals_met, development_notes)
        VALUES (?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✓ Inserted {len(records)} performance reviews")


# ---------------------------------------------------------------------------
# Paywork (Payroll)
# ---------------------------------------------------------------------------

def generate_payroll(conn):
    print("\n💳 Generating payroll runs and records (Paywork)...")

    # Only Staff and Contractor person types get payroll
    payroll_persons = [r[0] for r in conn.execute("""
        SELECT person_id FROM staff_volunteers
        WHERE person_type IN ('Staff', 'Contractor')
    """)]

    # Fetch annual salary from hr_employees for each person
    salary_map = {r[0]: r[1] for r in conn.execute(
        "SELECT person_id, COALESCE(annual_salary, 52000) FROM hr_employees"
    )}

    run_records    = []
    record_rows    = []
    ytd_gross_map  = {}  # person_id → YTD gross (resets each calendar year)
    ytd_tax_map    = {}

    start = date(2024, 1, 1)
    end   = date(2026, 3, 31)
    current_year  = None

    for period_start, period_end, pay_date in biweekly_periods(start, end):
        if period_start.year != current_year:
            current_year = period_start.year
            ytd_gross_map = {p: 0.0 for p in payroll_persons}
            ytd_tax_map   = {p: 0.0 for p in payroll_persons}

        run_gross = 0.0
        run_deductions = 0.0
        run_net   = 0.0
        period_records = []

        for person_id in payroll_persons:
            annual = salary_map.get(person_id, 55000)
            gross  = round(annual / 26, 2)
            fed_tx = round(gross * 0.20, 2)
            prov_tx = round(gross * 0.07, 2)
            cpp    = round(min(gross * 0.0595, 148.76), 2)
            ei     = round(min(gross * 0.0166,  41.40), 2)
            other  = round(random.uniform(0, 50), 2)
            total_ded = fed_tx + prov_tx + cpp + ei + other
            net    = round(gross - total_ded, 2)

            ytd_gross_map[person_id] = round(ytd_gross_map[person_id] + gross, 2)
            ytd_tax_map[person_id]   = round(ytd_tax_map[person_id] + fed_tx + prov_tx, 2)

            run_gross      += gross
            run_deductions += total_ded
            run_net        += net

            period_records.append((
                None,  # run_id filled after run insert
                person_id,
                80.0 if annual > 40000 else 60.0,
                round(random.uniform(0, 2), 2),
                gross, fed_tx, prov_tx, cpp, ei, other, net,
                ytd_gross_map[person_id], ytd_tax_map[person_id],
            ))

        run_records.append((
            str(period_start), str(period_end), str(pay_date),
            "Regular", "Paid",
            round(run_gross, 2), round(run_deductions, 2),
            round(run_net, 2), len(payroll_persons),
        ))

        record_rows.append(period_records)

    # Insert runs and then records
    for i, run in enumerate(run_records):
        conn.execute("""
            INSERT INTO payroll_runs
                (pay_period_start, pay_period_end, pay_date, run_type, status,
                 total_gross, total_deductions, total_net, employee_count)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, run)
        run_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.executemany("""
            INSERT INTO payroll_records
                (run_id, person_id, regular_hours, overtime_hours,
                 gross_pay, federal_tax, provincial_tax, cpp_deduction,
                 ei_deduction, other_deductions, net_pay, ytd_gross, ytd_tax)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, [(run_id,) + tuple(r[1:]) for r in record_rows[i]])

    conn.commit()
    total_runs = conn.execute("SELECT COUNT(*) FROM payroll_runs").fetchone()[0]
    total_recs = conn.execute("SELECT COUNT(*) FROM payroll_records").fetchone()[0]
    print(f"  ✓ Inserted {total_runs} payroll runs / {total_recs} pay records")


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def generate_data_sources(conn):
    print("\n🗂️  Generating data source metadata...")
    now = str(datetime.now().replace(microsecond=0))
    sources = [
        # Newtract / D365
        ("Newtract",        "beneficiaries",       "Client/beneficiary master records",              "Daily",  now),
        ("Newtract",        "programs",             "Service programs offered by IISofBC",            "Daily",  now),
        ("Newtract",        "program_enrollments",  "Client program enrollment and status",           "Daily",  now),
        ("Newtract",        "program_sessions",     "Scheduled program sessions",                     "Daily",  now),
        ("Newtract",        "session_attendance",   "Per-session attendance records",                 "Daily",  now),
        ("Newtract",        "outcomes",             "Tracked client outcomes",                        "Daily",  now),
        ("Newtract",        "services_delivered",   "Individual service delivery log",                "Daily",  now),
        ("Newtract",        "job_placements",       "Employment placement tracking",                  "Daily",  now),
        ("Newtract",        "settlement_milestones","Key settlement milestone achievements",          "Daily",  now),
        ("Newtract",        "communication_log",    "Staff-client communication history",             "Daily",  now),
        # Business Central
        ("BusinessCentral", "donations",            "Donation receipts and in-kind records",          "Daily",  now),
        ("BusinessCentral", "government_grants",    "Grant agreements and claimed amounts",           "Weekly", now),
        ("BusinessCentral", "expenses",             "Operational expense records",                    "Daily",  now),
        ("BusinessCentral", "gl_accounts",          "Chart of accounts",                              "Monthly",now),
        ("BusinessCentral", "gl_transactions",      "General ledger transaction lines",               "Daily",  now),
        ("BusinessCentral", "budget_lines",         "Annual budget allocations by account/program",   "Monthly",now),
        # BambooHR
        ("BambooHR",        "staff_volunteers",     "Staff, volunteer and contractor roster",         "Daily",  now),
        ("BambooHR",        "hr_departments",       "Organizational department structure",            "Monthly",now),
        ("BambooHR",        "hr_employees",         "Employee HR details (salary, type, manager)",    "Daily",  now),
        ("BambooHR",        "hr_leave_requests",    "Leave requests and approvals",                   "Daily",  now),
        ("BambooHR",        "hr_performance_reviews","Annual and mid-year performance reviews",       "Monthly",now),
        # Paywork
        ("Paywork",         "payroll_runs",         "Bi-weekly payroll run summaries",                "Daily",  now),
        ("Paywork",         "payroll_records",      "Individual employee pay stub details",           "Daily",  now),
    ]
    conn.executemany("""
        INSERT INTO data_sources
            (source_system, table_name, description, sync_frequency, last_synced_at)
        VALUES (?,?,?,?,?)
    """, sources)
    conn.commit()
    print(f"  ✓ Inserted {len(sources)} data source entries")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary(conn):
    tables = [
        # Newtract
        ("beneficiaries",        "Beneficiaries (Newtract)"),
        ("programs",             "Programs (Newtract)"),
        ("program_enrollments",  "Enrollments (Newtract)"),
        ("program_sessions",     "Sessions (Newtract)"),
        ("services_delivered",   "Services Delivered (Newtract)"),
        ("job_placements",       "Job Placements (Newtract)"),
        ("outcomes",             "Outcomes (Newtract)"),
        ("settlement_milestones","Milestones (Newtract)"),
        ("communication_log",    "Communications (Newtract)"),
        # Business Central
        ("donations",            "Donations (Business Central)"),
        ("government_grants",    "Grants (Business Central)"),
        ("expenses",             "Expenses (Business Central)"),
        ("gl_accounts",          "GL Accounts (Business Central)"),
        ("gl_transactions",      "GL Transactions (Business Central)"),
        ("budget_lines",         "Budget Lines (Business Central)"),
        # BambooHR
        ("staff_volunteers",     "Staff/Volunteers (BambooHR)"),
        ("hr_departments",       "Departments (BambooHR)"),
        ("hr_employees",         "HR Employees (BambooHR)"),
        ("hr_leave_requests",    "Leave Requests (BambooHR)"),
        ("hr_performance_reviews","Performance Reviews (BambooHR)"),
        # Paywork
        ("payroll_runs",         "Payroll Runs (Paywork)"),
        ("payroll_records",      "Payroll Records (Paywork)"),
    ]
    print("\n====== DATABASE SUMMARY ======")
    print(f"Database : {DB_PATH}")
    print(f"Systems  : Newtract · Business Central · BambooHR · Paywork\n")
    for tbl, label in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {label:<42} {count:>6,}")
    cash_don = conn.execute(
        "SELECT SUM(donation_amount) FROM donations WHERE donation_type='Cash'"
    ).fetchone()[0] or 0
    grant_tot = conn.execute(
        "SELECT SUM(grant_amount) FROM government_grants"
    ).fetchone()[0] or 0
    payroll_gross = conn.execute(
        "SELECT SUM(total_gross) FROM payroll_runs"
    ).fetchone()[0] or 0
    print(f"\n  Total Cash Donations : ${cash_don:>12,.2f}")
    print(f"  Total Grant Funding  : ${grant_tot:>12,.2f}")
    print(f"  Total Payroll Gross  : ${payroll_gross:>12,.2f}")
    print("==============================\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("====== ISSOFBC SQLite Staging DB - Sample Data ======")

    conn = connect()
    print(f"✓ Connected to SQLite database: {DB_PATH}")

    create_schema(conn)

    # --- Newtract (CRM) ---
    program_ids     = generate_programs(conn)
    staff_ids       = generate_staff_volunteers(conn, count=20)
    beneficiary_ids = generate_beneficiaries(conn, count=200)
    generate_enrollments(conn, beneficiary_ids, program_ids)
    generate_sessions(conn, program_ids, staff_ids)
    generate_services(conn, beneficiary_ids, staff_ids, count=400)
    generate_job_placements(conn, beneficiary_ids, count=80)
    generate_outcomes(conn, beneficiary_ids, program_ids, count=300)
    generate_milestones(conn, beneficiary_ids, staff_ids, count=250)
    generate_communications(conn, beneficiary_ids, staff_ids, count=350)

    # --- Business Central (Finance) ---
    generate_donations(conn, count=150)
    generate_grants(conn, program_ids)
    generate_expenses(conn, staff_ids, program_ids, count=200)
    account_map = generate_gl_accounts(conn)
    generate_gl_transactions(conn, account_map)
    generate_budget_lines(conn, account_map, program_ids)

    # --- BambooHR (HR) ---
    dept_map    = generate_hr_departments(conn)
    hr_emp_ids  = generate_hr_employees(conn, staff_ids, dept_map)
    generate_leave_requests(conn, hr_emp_ids, count=80)
    generate_performance_reviews(conn, hr_emp_ids)

    # --- Paywork (Payroll) ---
    generate_payroll(conn)

    # --- Metadata ---
    generate_data_sources(conn)

    print("\n✓ Sample data generation completed!")
    print_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
