-- ISSOFBC Non-Profit Immigration Services Database Schema
-- SQLite Version (Perfect for demos, local development, and deployment)
-- 
-- Run this script to create all tables:
-- sqlite3 issofbc.db < schema_sqlite.sql

-- ============================================
-- DIMENSION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS beneficiaries (
    beneficiary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL CHECK(status IN ('Active', 'Completed', 'Inactive')),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT CHECK(gender IN ('M', 'F', 'Other')),
    immigration_status TEXT CHECK(immigration_status IN ('Refugee', 'Permanent Resident', 'Citizen', 'Work Permit', 'Study Permit')),
    arrival_date DATE,
    primary_language TEXT,
    english_proficiency_start TEXT,
    country_of_origin TEXT,
    household_size INTEGER,
    income_level_start DECIMAL(10, 2),
    contact_phone TEXT,
    contact_email TEXT,
    referred_by TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_beneficiary_status ON beneficiaries(status);
CREATE INDEX IF NOT EXISTS idx_beneficiary_immigration ON beneficiaries(immigration_status);
CREATE INDEX IF NOT EXISTS idx_beneficiary_created ON beneficiaries(created_date);

CREATE TABLE IF NOT EXISTS programs (
    program_id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_code TEXT NOT NULL UNIQUE,
    program_name TEXT NOT NULL,
    description TEXT,
    program_type TEXT CHECK(program_type IN ('Group', 'Individual', 'Online', 'Hybrid')),
    target_audience TEXT,
    duration_weeks INTEGER,
    frequency TEXT,
    max_capacity INTEGER,
    budget_allocated DECIMAL(12, 2),
    is_active BOOLEAN DEFAULT 1,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_program_code ON programs(program_code);
CREATE INDEX IF NOT EXISTS idx_program_active ON programs(is_active);

CREATE TABLE IF NOT EXISTS staff_volunteers (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    person_type TEXT NOT NULL CHECK(person_type IN ('Staff', 'Volunteer', 'Contractor')),
    employment_status TEXT NOT NULL CHECK(employment_status IN ('Active', 'Inactive')),
    department TEXT,
    roles TEXT,
    languages_spoken TEXT,
    hire_date DATE,
    salary_hourly_rate DECIMAL(10, 2),
    volunteer_hours_target INTEGER,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_staff_status ON staff_volunteers(employment_status);
CREATE INDEX IF NOT EXISTS idx_staff_type ON staff_volunteers(person_type);

-- ============================================
-- PROGRAM & SESSION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS program_enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiary_id INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    enrollment_date DATE NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Active', 'Completed', 'Dropped Out', 'On Hold')),
    completion_date DATE,
    attendance_rate DECIMAL(5, 2),
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id),
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);

CREATE INDEX IF NOT EXISTS idx_enrollment_beneficiary ON program_enrollments(beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_program ON program_enrollments(program_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_status ON program_enrollments(status);

CREATE TABLE IF NOT EXISTS program_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    session_number INTEGER,
    start_date DATE NOT NULL,
    end_date DATE,
    instructor_id INTEGER,
    location TEXT,
    session_type TEXT CHECK(session_type IN ('Workshop', 'Class', 'Consultation', 'Group Activity')),
    max_capacity INTEGER,
    material_topic TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES programs(program_id),
    FOREIGN KEY (instructor_id) REFERENCES staff_volunteers(person_id)
);

CREATE INDEX IF NOT EXISTS idx_session_program ON program_sessions(program_id);
CREATE INDEX IF NOT EXISTS idx_session_date ON program_sessions(start_date);

CREATE TABLE IF NOT EXISTS session_attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    beneficiary_id INTEGER NOT NULL,
    attended BOOLEAN,
    arrival_time TIME,
    departure_time TIME,
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES program_sessions(session_id),
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id)
);

CREATE INDEX IF NOT EXISTS idx_attendance_session ON session_attendance(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_beneficiary ON session_attendance(beneficiary_id);

-- ============================================
-- OUTCOMES & PROGRESS TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS outcomes (
    outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiary_id INTEGER NOT NULL,
    outcome_type TEXT NOT NULL,
    program_id INTEGER,
    metric_name TEXT,
    metric_value TEXT,
    metric_date DATE NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id),
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);

CREATE INDEX IF NOT EXISTS idx_outcome_beneficiary ON outcomes(beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_outcome_type ON outcomes(outcome_type);
CREATE INDEX IF NOT EXISTS idx_outcome_date ON outcomes(metric_date);

CREATE TABLE IF NOT EXISTS services_delivered (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiary_id INTEGER NOT NULL,
    service_type TEXT NOT NULL,
    provider_id INTEGER,
    service_date DATE NOT NULL,
    duration_minutes INTEGER,
    location TEXT,
    outcome_description TEXT,
    follow_up_needed BOOLEAN,
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id),
    FOREIGN KEY (provider_id) REFERENCES staff_volunteers(person_id)
);

CREATE INDEX IF NOT EXISTS idx_service_beneficiary ON services_delivered(beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_service_date ON services_delivered(service_date);

CREATE TABLE IF NOT EXISTS job_placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiary_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    employer_name TEXT NOT NULL,
    placement_date DATE NOT NULL,
    employment_type TEXT CHECK(employment_type IN ('Full-time', 'Part-time', 'Contract', 'Self-employed')),
    salary_range_start DECIMAL(10, 2),
    status TEXT CHECK(status IN ('Active', 'Completed - Left', 'Completed - Terminated')),
    end_date DATE,
    industry_sector TEXT,
    match_score DECIMAL(3, 2),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id)
);

CREATE INDEX IF NOT EXISTS idx_placement_beneficiary ON job_placements(beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_placement_date ON job_placements(placement_date);

CREATE TABLE IF NOT EXISTS settlement_milestones (
    milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiary_id INTEGER NOT NULL,
    milestone_type TEXT NOT NULL,
    milestone_date DATE NOT NULL,
    notes TEXT,
    supporting_staff_id INTEGER,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id),
    FOREIGN KEY (supporting_staff_id) REFERENCES staff_volunteers(person_id)
);

CREATE INDEX IF NOT EXISTS idx_milestone_beneficiary ON settlement_milestones(beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_milestone_type ON settlement_milestones(milestone_type);

-- ============================================
-- COMMUNICATION & SUPPORT
-- ============================================

CREATE TABLE IF NOT EXISTS communication_log (
    comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiary_id INTEGER NOT NULL,
    staff_id INTEGER,
    communication_type TEXT CHECK(communication_type IN ('Phone', 'Email', 'In-Person', 'SMS', 'Other')),
    subject TEXT NOT NULL,
    notes TEXT,
    outcome TEXT,
    next_action_required BOOLEAN,
    comm_date DATETIME NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id),
    FOREIGN KEY (staff_id) REFERENCES staff_volunteers(person_id)
);

CREATE INDEX IF NOT EXISTS idx_comm_beneficiary ON communication_log(beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_comm_date ON communication_log(comm_date);

-- ============================================
-- FUNDING & BUDGET
-- ============================================

CREATE TABLE IF NOT EXISTS donations (
    donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_name TEXT NOT NULL,
    donor_type TEXT CHECK(donor_type IN ('Individual', 'Corporate', 'Foundation', 'Anonymous')),
    donation_amount DECIMAL(10, 2),
    donation_date DATE NOT NULL,
    donation_type TEXT CHECK(donation_type IN ('Cash', 'In-kind', 'Pledge')),
    item_type TEXT,
    quantity INTEGER,
    purpose TEXT,
    tax_receipt_issued BOOLEAN DEFAULT 0,
    receipt_number TEXT,
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_donation_date ON donations(donation_date);
CREATE INDEX IF NOT EXISTS idx_donation_type ON donations(donor_type);

CREATE TABLE IF NOT EXISTS government_grants (
    grant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    grant_name TEXT NOT NULL,
    grant_number TEXT UNIQUE,
    funding_source TEXT CHECK(funding_source IN ('Federal', 'Provincial', 'Municipal')),
    program_id INTEGER,
    grant_amount DECIMAL(12, 2) NOT NULL,
    grant_year INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    reporting_requirements TEXT,
    amount_claimed_ytd DECIMAL(12, 2),
    amount_approved_ytd DECIMAL(12, 2),
    status TEXT CHECK(status IN ('Active', 'Completed', 'Pending Approval')),
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);

CREATE INDEX IF NOT EXISTS idx_grant_year ON government_grants(grant_year);
CREATE INDEX IF NOT EXISTS idx_grant_status ON government_grants(status);

CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date DATE NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    vendor_name TEXT,
    approval_status TEXT CHECK(approval_status IN ('Submitted', 'Approved', 'Rejected', 'Reimbursed')),
    approved_by INTEGER,
    program_id INTEGER,
    grant_id INTEGER,
    receipt_attached BOOLEAN DEFAULT 0,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (approved_by) REFERENCES staff_volunteers(person_id),
    FOREIGN KEY (program_id) REFERENCES programs(program_id),
    FOREIGN KEY (grant_id) REFERENCES government_grants(grant_id)
);

CREATE INDEX IF NOT EXISTS idx_expense_date ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_expense_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expense_status ON expenses(approval_status);

-- ============================================
-- SOURCE: BAMBOOHR - HR MANAGEMENT
-- ============================================

CREATE TABLE IF NOT EXISTS hr_departments (
    dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL,
    department_code TEXT UNIQUE NOT NULL,
    cost_center TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hr_employees (
    hr_employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER UNIQUE NOT NULL,
    employee_number TEXT UNIQUE NOT NULL,
    dept_id INTEGER,
    position_title TEXT,
    employment_type TEXT CHECK(employment_type IN ('Full-time', 'Part-time', 'Contract', 'Casual')),
    employment_status TEXT CHECK(employment_status IN ('Active', 'On Leave', 'Terminated')) DEFAULT 'Active',
    start_date DATE,
    end_date DATE,
    annual_salary DECIMAL(10, 2),
    hourly_rate DECIMAL(6, 2),
    manager_hr_employee_id INTEGER,
    city TEXT DEFAULT 'Vancouver',
    province TEXT DEFAULT 'BC',
    benefits_enrolled BOOLEAN DEFAULT 1,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES staff_volunteers(person_id),
    FOREIGN KEY (dept_id) REFERENCES hr_departments(dept_id),
    FOREIGN KEY (manager_hr_employee_id) REFERENCES hr_employees(hr_employee_id)
);

CREATE INDEX IF NOT EXISTS idx_hr_employee_person ON hr_employees(person_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_dept ON hr_employees(dept_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_status ON hr_employees(employment_status);

CREATE TABLE IF NOT EXISTS hr_leave_requests (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hr_employee_id INTEGER NOT NULL,
    leave_type TEXT CHECK(leave_type IN ('Vacation', 'Sick', 'Maternity', 'Paternity', 'Bereavement', 'Unpaid', 'Other')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days DECIMAL(4, 1),
    status TEXT CHECK(status IN ('Pending', 'Approved', 'Rejected', 'Cancelled')) DEFAULT 'Approved',
    approved_by_hr_employee_id INTEGER,
    reason TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_employee_id) REFERENCES hr_employees(hr_employee_id),
    FOREIGN KEY (approved_by_hr_employee_id) REFERENCES hr_employees(hr_employee_id)
);

CREATE INDEX IF NOT EXISTS idx_leave_employee ON hr_leave_requests(hr_employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_dates ON hr_leave_requests(start_date, end_date);

CREATE TABLE IF NOT EXISTS hr_performance_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hr_employee_id INTEGER NOT NULL,
    review_year INTEGER NOT NULL,
    review_period TEXT CHECK(review_period IN ('Annual', 'Mid-Year', 'Probation')) DEFAULT 'Annual',
    overall_rating INTEGER CHECK(overall_rating BETWEEN 1 AND 5),
    reviewer_hr_employee_id INTEGER,
    review_date DATE,
    goals_met TEXT,
    development_notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_employee_id) REFERENCES hr_employees(hr_employee_id),
    FOREIGN KEY (reviewer_hr_employee_id) REFERENCES hr_employees(hr_employee_id)
);

CREATE INDEX IF NOT EXISTS idx_review_employee ON hr_performance_reviews(hr_employee_id);
CREATE INDEX IF NOT EXISTS idx_review_year ON hr_performance_reviews(review_year);

-- ============================================
-- SOURCE: PAYWORK - PAYROLL
-- ============================================

CREATE TABLE IF NOT EXISTS payroll_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    pay_date DATE NOT NULL,
    run_type TEXT CHECK(run_type IN ('Regular', 'Bonus', 'Off-cycle')) DEFAULT 'Regular',
    status TEXT CHECK(status IN ('Draft', 'Processed', 'Paid')) DEFAULT 'Paid',
    total_gross DECIMAL(12, 2),
    total_deductions DECIMAL(12, 2),
    total_net DECIMAL(12, 2),
    employee_count INTEGER,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payroll_run_period ON payroll_runs(pay_period_start, pay_period_end);
CREATE INDEX IF NOT EXISTS idx_payroll_run_date ON payroll_runs(pay_date);

CREATE TABLE IF NOT EXISTS payroll_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    regular_hours DECIMAL(6, 2) DEFAULT 80,
    overtime_hours DECIMAL(6, 2) DEFAULT 0,
    gross_pay DECIMAL(10, 2),
    federal_tax DECIMAL(10, 2),
    provincial_tax DECIMAL(10, 2),
    cpp_deduction DECIMAL(10, 2),
    ei_deduction DECIMAL(10, 2),
    other_deductions DECIMAL(10, 2) DEFAULT 0,
    net_pay DECIMAL(10, 2),
    ytd_gross DECIMAL(12, 2),
    ytd_tax DECIMAL(12, 2),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES payroll_runs(run_id),
    FOREIGN KEY (person_id) REFERENCES staff_volunteers(person_id)
);

CREATE INDEX IF NOT EXISTS idx_payroll_record_run ON payroll_records(run_id);
CREATE INDEX IF NOT EXISTS idx_payroll_record_person ON payroll_records(person_id);

-- ============================================
-- SOURCE: BUSINESS CENTRAL - GL & BUDGET (EXTENDED)
-- ============================================

CREATE TABLE IF NOT EXISTS gl_accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_code TEXT NOT NULL UNIQUE,
    account_name TEXT NOT NULL,
    account_type TEXT CHECK(account_type IN ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense')) NOT NULL,
    account_category TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gl_account_type ON gl_accounts(account_type);
CREATE INDEX IF NOT EXISTS idx_gl_account_code ON gl_accounts(account_code);

CREATE TABLE IF NOT EXISTS gl_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NOT NULL,
    debit_amount DECIMAL(12, 2) DEFAULT 0,
    credit_amount DECIMAL(12, 2) DEFAULT 0,
    description TEXT,
    reference_number TEXT,
    source_module TEXT CHECK(source_module IN ('Donations', 'Grants', 'Expenses', 'Payroll', 'Manual', 'AR', 'AP')),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES gl_accounts(account_id)
);

CREATE INDEX IF NOT EXISTS idx_gl_trans_account ON gl_transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_gl_trans_date ON gl_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_gl_trans_period ON gl_transactions(fiscal_year, fiscal_period);

CREATE TABLE IF NOT EXISTS budget_lines (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiscal_year INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    program_id INTEGER,
    annual_budget DECIMAL(12, 2) NOT NULL,
    q1_budget DECIMAL(12, 2),
    q2_budget DECIMAL(12, 2),
    q3_budget DECIMAL(12, 2),
    q4_budget DECIMAL(12, 2),
    actual_ytd DECIMAL(12, 2) DEFAULT 0,
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES gl_accounts(account_id),
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);

CREATE INDEX IF NOT EXISTS idx_budget_year ON budget_lines(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_budget_account ON budget_lines(account_id);

-- ============================================
-- METADATA: DATA SOURCES
-- ============================================

CREATE TABLE IF NOT EXISTS data_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_system TEXT NOT NULL,
    table_name TEXT NOT NULL UNIQUE,
    description TEXT,
    sync_frequency TEXT CHECK(sync_frequency IN ('Real-time', 'Daily', 'Weekly', 'Monthly')),
    last_synced_at DATETIME,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SUMMARY: Total Tables = 28
-- ============================================
-- SOURCE: Newtract (CRM/D365)
--   beneficiaries, programs, program_enrollments, program_sessions,
--   session_attendance, outcomes, services_delivered, job_placements,
--   settlement_milestones, communication_log
-- SOURCE: Business Central (Finance)
--   donations, government_grants, expenses, gl_accounts, gl_transactions, budget_lines
-- SOURCE: BambooHR (HR)
--   staff_volunteers, hr_departments, hr_employees, hr_leave_requests, hr_performance_reviews
-- SOURCE: Paywork (Payroll)
--   payroll_runs, payroll_records
-- METADATA:
--   data_sources

-- ============================================
-- VERIFY TABLES CREATED
-- ============================================
-- Run this query to see all created tables:
-- SELECT name FROM sqlite_master WHERE type='table';
