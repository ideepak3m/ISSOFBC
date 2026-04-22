"""
Sample Data Generator for ISSOFBC Analytics Database
Generates realistic test data using Faker library

Usage:
    python generate_sample_data.py --rows 1000 --seed 42 --database issofbc_analytics

This script will:
1. Create a connection to MySQL
2. Insert sample data for all tables
3. Maintain referential integrity
4. Generate realistic distributions
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

# Requires: pip install faker mysql-connector-python

try:
    from faker import Faker
    import mysql.connector
except ImportError:
    print("Please install required packages:")
    print("  pip install faker mysql-connector-python")
    exit(1)


class SampleDataGenerator:
    def __init__(self, host='localhost', user='root', password='', database='issofbc_analytics', seed=42):
        """Initialize the data generator"""
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
        # Caches for generated IDs
        self.organization_ids = []
        self.department_ids = []
        self.employee_ids = []
        self.contact_ids = []
        self.product_ids = []
        self.opportunity_ids = []
        
        # Connection
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to MySQL database"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            print(f"✓ Connected to {self.database}")
        except mysql.connector.Error as err:
            print(f"✗ Error connecting to database: {err}")
            raise

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Connection closed")

    def clear_tables(self):
        """Clear all tables (for fresh start)"""
        tables = [
            'crm_activities',
            'crm_opportunities',
            'hr_leave_requests',
            'payroll_deductions',
            'payroll_records',
            'gl_transactions',
            'purchase_line_items',
            'purchase_transactions',
            'sales_line_items',
            'sales_transactions',
            'products',
            'contacts',
            'employees',
            'departments',
            'organizations'
        ]
        
        self.cursor.execute('SET FOREIGN_KEY_CHECKS=0')
        for table in tables:
            try:
                self.cursor.execute(f'TRUNCATE TABLE {table}')
                print(f"  ✓ Cleared {table}")
            except Exception as e:
                print(f"  ⚠ Could not clear {table}: {e}")
        self.cursor.execute('SET FOREIGN_KEY_CHECKS=1')
        self.conn.commit()

    # ========== GENERATION METHODS ==========

    def generate_organizations(self, count=5):
        """Generate organizations"""
        print(f"\n📊 Generating {count} organizations...")
        
        organizations = [
            ('ORG001', 'IISofBC Inc.', None, 'Company', 'Canada'),
            ('ORG002', 'Operations Division', 1, 'Division', 'Canada'),
            ('ORG003', 'Sales Division', 1, 'Division', 'Canada'),
            ('ORG004', 'Finance Division', 1, 'Division', 'Canada'),
            ('ORG005', 'HR Division', 1, 'Division', 'Canada'),
        ]
        
        for org_code, org_name, parent_id, org_type, country in organizations[:count]:
            sql = """
            INSERT INTO organizations (organization_code, organization_name, parent_organization_id, organization_type, country)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_code, org_name, parent_id, org_type, country))
            self.organization_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"  ✓ Inserted {len(self.organization_ids)} organizations")

    def generate_departments(self, per_org=3):
        """Generate departments"""
        print(f"\n🏢 Generating departments...")
        
        dept_names = [
            ('ACC', 'Accounting'),
            ('SAL', 'Sales'),
            ('MKT', 'Marketing'),
            ('OPS', 'Operations'),
            ('HR', 'Human Resources'),
            ('IT', 'Information Technology'),
        ]
        
        for org_id in self.organization_ids:
            for code, name in dept_names[:per_org]:
                sql = """
                INSERT INTO departments (organization_id, department_code, department_name, cost_center)
                VALUES (%s, %s, %s, %s)
                """
                cost_center = f"{code}-{org_id:03d}"
                self.cursor.execute(sql, (org_id, code, name, cost_center))
                self.department_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"  ✓ Inserted {len(self.department_ids)} departments")

    def generate_employees(self, count=150):
        """Generate employees"""
        print(f"\n👥 Generating {count} employees...")
        
        employment_types = ['Full-time', 'Part-time', 'Contract', 'Intern']
        roles = ['Manager', 'Analyst', 'Developer', 'Coordinator', 'Specialist', 'Director', 'Associate']
        
        # First, generate managers
        managers = {}
        for dept_id in random.sample(self.department_ids, min(len(self.department_ids), 5)):
            emp_code = f"EMP{len(self.employee_ids) + 1:04d}"
            sql = """
            INSERT INTO employees 
            (organization_id, department_id, employee_code, first_name, last_name, email, 
             job_title, employment_type, employment_status, hire_date, manager_id, salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            org_id = self.organization_ids[0]  # Default org
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@issbc.org"
            job_title = "Manager"
            hire_date = self.fake.date_between(start_date='-5y')
            salary = random.randint(80000, 120000)
            
            self.cursor.execute(sql, (org_id, dept_id, emp_code, first_name, last_name, email, 
                                     job_title, 'Full-time', 'Active', hire_date, None, salary))
            emp_id = self.cursor.lastrowid
            self.employee_ids.append(emp_id)
            managers[dept_id] = emp_id
        
        # Update departments with managers
        for dept_id, manager_id in managers.items():
            self.cursor.execute(f"UPDATE departments SET manager_employee_id = {manager_id} WHERE department_id = {dept_id}")
        
        self.conn.commit()
        
        # Generate regular employees
        for i in range(count - len(self.employee_ids)):
            emp_code = f"EMP{len(self.employee_ids) + 1:04d}"
            org_id = random.choice(self.organization_ids)
            dept_id = random.choice(self.department_ids)
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@issbc.org"
            job_title = random.choice(roles)
            employment_type = random.choice(employment_types)
            hire_date = self.fake.date_between(start_date='-7y', end_date='today')
            manager_id = random.choice(list(managers.values())) if managers else None
            salary = random.randint(40000, 100000)
            
            sql = """
            INSERT INTO employees 
            (organization_id, department_id, employee_code, first_name, last_name, email, 
             job_title, employment_type, employment_status, hire_date, manager_id, salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_id, dept_id, emp_code, first_name, last_name, email, 
                                     job_title, employment_type, 'Active', hire_date, manager_id, salary))
            self.employee_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"  ✓ Inserted {len(self.employee_ids)} employees")

    def generate_contacts(self, count=100):
        """Generate contacts (customers, vendors, etc.)"""
        print(f"\n📇 Generating {count} contacts...")
        
        contact_types = ['Customer', 'Vendor', 'Prospect', 'Partner']
        industries = ['Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing', 'Education', 'Energy']
        
        for i in range(count):
            contact_code = f"CON{i + 1:04d}"
            org_id = random.choice(self.organization_ids)
            contact_type = random.choice(contact_types)
            first_name = self.fake.first_name() if random.random() > 0.5 else ""
            last_name = self.fake.last_name() if random.random() > 0.5 else ""
            company_name = self.fake.company() if contact_type in ['Customer', 'Vendor'] else None
            email = self.fake.email()
            phone = self.fake.phone_number()
            country = random.choice(['Canada', 'USA', 'UK', 'Australia'])
            industry = random.choice(industries) if contact_type != 'Internal' else None
            credit_limit = random.randint(10000, 500000) if contact_type == 'Customer' else None
            
            sql = """
            INSERT INTO contacts 
            (organization_id, contact_code, contact_type, first_name, last_name, company_name, 
             email, phone, country, industry, credit_limit, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_id, contact_code, contact_type, first_name, last_name, 
                                     company_name, email, phone, country, industry, credit_limit, True))
            self.contact_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"  ✓ Inserted {len(self.contact_ids)} contacts")

    def generate_products(self, count=50):
        """Generate products"""
        print(f"\n📦 Generating {count} products...")
        
        categories = ['Software', 'Hardware', 'Consulting', 'Support', 'Training', 'Licensing']
        
        for i in range(count):
            product_code = f"PRD{i + 1:04d}"
            org_id = random.choice(self.organization_ids)
            product_name = self.fake.word().title() + " " + random.choice(['Suite', 'Package', 'Service', 'License'])
            category = random.choice(categories)
            unit_price = random.randint(100, 50000)
            cost_price = unit_price * random.uniform(0.3, 0.7)
            
            sql = """
            INSERT INTO products 
            (organization_id, product_code, product_name, category, unit_price, cost_price, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_id, product_code, product_name, category, unit_price, cost_price, True))
            self.product_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"  ✓ Inserted {len(self.product_ids)} products")

    def generate_sales_transactions(self, count=500):
        """Generate sales transactions"""
        print(f"\n💰 Generating {count} sales transactions...")
        
        transaction_types = ['Order', 'Invoice', 'Quote']
        statuses = ['Posted', 'Partially Paid', 'Paid', 'Cancelled']
        
        for i in range(count):
            trans_num = f"INV{datetime.now().year}{i + 1:06d}"
            org_id = random.choice(self.organization_ids)
            customer_id = random.choice(self.contact_ids)
            employee_id = random.choice(self.employee_ids)
            trans_type = random.choice(transaction_types)
            trans_date = self.fake.date_between(start_date='-1y')
            due_date = trans_date + timedelta(days=30)
            status = random.choice(statuses)
            
            # Generate line items
            num_items = random.randint(1, 5)
            subtotal = 0
            for _ in range(num_items):
                qty = random.randint(1, 10)
                unit_price = random.choice([p[0] for p in [(random.randint(100, 5000), None)]])
                subtotal += qty * unit_price
            
            tax_amount = subtotal * 0.13  # 13% tax for Ontario
            total_amount = subtotal + tax_amount
            paid_amount = total_amount if status == 'Paid' else (total_amount * random.uniform(0, 1) if status == 'Partially Paid' else 0)
            
            sql = """
            INSERT INTO sales_transactions 
            (transaction_number, organization_id, customer_id, sales_employee_id, transaction_type, 
             transaction_date, due_date, status, subtotal_amount, tax_amount, total_amount, paid_amount, currency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (trans_num, org_id, customer_id, employee_id, trans_type, 
                                     trans_date, due_date, status, subtotal, tax_amount, total_amount, paid_amount, 'USD'))
            trans_id = self.cursor.lastrowid
            
            # Insert line items
            for _ in range(num_items):
                product_id = random.choice(self.product_ids)
                qty = random.randint(1, 10)
                unit_price = random.randint(100, 5000)
                discount = random.uniform(0, 20)
                line_total = (qty * unit_price) * (1 - discount / 100)
                
                sql_item = """
                INSERT INTO sales_line_items (transaction_id, product_id, quantity, unit_price, discount_percent, line_total)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql_item, (trans_id, product_id, qty, unit_price, discount, line_total))
        
        self.conn.commit()
        print(f"  ✓ Inserted {count} sales transactions")

    def generate_payroll_records(self, count=300):
        """Generate payroll records"""
        print(f"\n💳 Generating {count} payroll records...")
        
        for i in range(count):
            employee_id = random.choice(self.employee_ids)
            org_id = self.organization_ids[0]  # Simplified
            period_start = self.fake.date_between(start_date='-1y')
            period_end = period_start + timedelta(days=14)
            
            # Get employee salary
            self.cursor.execute(f"SELECT salary FROM employees WHERE employee_id = {employee_id}")
            result = self.cursor.fetchone()
            employee_salary = result[0] if result else 50000
            
            gross_salary = employee_salary / 26  # Bi-weekly
            taxable_income = gross_salary
            tax_amount = gross_salary * 0.25
            deductions_total = random.randint(100, 500)
            net_pay = gross_salary - tax_amount - deductions_total
            
            payment_date = period_end +timedelta(days=3)
            
            sql = """
            INSERT INTO payroll_records 
            (organization_id, employee_id, payroll_period_start, payroll_period_end, 
             gross_salary, taxable_income, tax_amount, deductions_total, net_pay, payment_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_id, employee_id, period_start, period_end, 
                                     gross_salary, taxable_income, tax_amount, deductions_total, net_pay, payment_date, 'Paid'))
            payroll_id = self.cursor.lastrowid
            
            # Add deductions
            deduction_types = ['Tax', 'Health Insurance', 'Pension']
            for ded_type in random.sample(deduction_types, random.randint(1, 2)):
                amount = random.uniform(50, 300)
                sql_ded = "INSERT INTO payroll_deductions (payroll_id, deduction_type, amount) VALUES (%s, %s, %s)"
                self.cursor.execute(sql_ded, (payroll_id, ded_type, amount))
        
        self.conn.commit()
        print(f"  ✓ Inserted {count} payroll records")

    def generate_crm_opportunities(self, count=100):
        """Generate CRM opportunities"""
        print(f"\n🎯 Generating {count} CRM opportunities...")
        
        stages = ['Prospect', 'Qualification', 'Proposal', 'Negotiation', 'Won', 'Lost']
        
        for i in range(count):
            org_id = random.choice(self.organization_ids)
            contact_id = random.choice(self.contact_ids)
            owner_id = random.choice(self.employee_ids)
            opp_name = self.fake.word().title() + " - " + self.fake.company()
            stage = random.choice(stages)
            est_value = random.randint(10000, 500000)
            probability = random.randint(0, 100)
            expected_close = self.fake.date_between(start_date='-1m', end_date='+6m')
            actual_close = expected_close if stage in ['Won', 'Lost'] else None
            activity_status = 'Closed' if stage in ['Won', 'Lost'] else 'Active'
            
            sql = """
            INSERT INTO crm_opportunities 
            (organization_id, contact_id, owner_employee_id, opportunity_name, stage, 
             estimated_value, probability_percent, expected_close_date, actual_close_date, activity_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_id, contact_id, owner_id, opp_name, stage, 
                                     est_value, probability, expected_close, actual_close, activity_status))
            self.opportunity_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"  ✓ Inserted {count} opportunities")

    def generate_crm_activities(self, count=500):
        """Generate CRM activities"""
        print(f"\n📞 Generating {count} CRM activities...")
        
        activity_types = ['Call', 'Email', 'Meeting', 'Task', 'Note']
        statuses = ['Planned', 'Completed', 'Cancelled']
        
        for i in range(count):
            org_id = random.choice(self.organization_ids)
            contact_id = random.choice(self.contact_ids)
            employee_id = random.choice(self.employee_ids)
            opportunity_id = random.choice(self.opportunity_ids) if self.opportunity_ids else None
            activity_type = random.choice(activity_types)
            activity_date = self.fake.date_between(start_date='-6m')
            duration = random.randint(15, 120) if activity_type in ['Call', 'Meeting'] else None
            subject = self.fake.sentence()
            status = random.choice(statuses)
            
            sql = """
            INSERT INTO crm_activities 
            (organization_id, contact_id, employee_id, opportunity_id, activity_type, 
             activity_date, duration_minutes, subject, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_id, contact_id, employee_id, opportunity_id, activity_type, 
                                     activity_date, duration, subject, status))
        
        self.conn.commit()
        print(f"  ✓ Inserted {count} activities")

    def generate_hr_leave_requests(self, count=100):
        """Generate HR leave requests"""
        print(f"\n🏖️  Generating {count} leave requests...")
        
        leave_types = ['Vacation', 'Sick', 'Unpaid', 'Maternity', 'Bereavement']
        statuses = ['Requested', 'Approved', 'Rejected', 'Cancelled']
        
        for i in range(count):
            org_id = random.choice(self.organization_ids)
            employee_id = random.choice(self.employee_ids)
            approver_id = random.choice(self.employee_ids)
            leave_type = random.choice(leave_types)
            start_date = self.fake.date_between(start_date='-1y', end_date='+6m')
            duration = random.randint(1, 20)
            end_date = start_date + timedelta(days=duration)
            status = random.choice(statuses)
            
            sql = """
            INSERT INTO hr_leave_requests 
            (organization_id, employee_id, leave_type, start_date, end_date, total_days, status, approver_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (org_id, employee_id, leave_type, start_date, end_date, duration, status, approver_id))
        
        self.conn.commit()
        print(f"  ✓ Inserted {count} leave requests")

    def generate_all(self, org_count=5, emp_count=150, con_count=100, prod_count=50, 
                    sales_count=500, payroll_count=300, opp_count=100, activities_count=500, leaves_count=100):
        """Generate all sample data"""
        print("\n" + "="*60)
        print("ISSOFBC Analytics Database - Sample Data Generator")
        print("="*60)
        
        try:
            self.connect()
            self.clear_tables()
            
            self.generate_organizations(org_count)
            self.generate_departments(per_org=3)
            self.generate_employees(emp_count)
            self.generate_contacts(con_count)
            self.generate_products(prod_count)
            self.generate_sales_transactions(sales_count)
            self.generate_payroll_records(payroll_count)
            self.generate_crm_opportunities(opp_count)
            self.generate_crm_activities(activities_count)
            self.generate_hr_leave_requests(leaves_count)
            
            print("\n" + "="*60)
            print("✓ Sample data generation completed successfully!")
            print("="*60)
            print(f"Generated:")
            print(f"  - {org_count} organizations")
            print(f"  - {len(self.department_ids)} departments")
            print(f"  -  {len(self.employee_ids)} employees")
            print(f"  - {con_count} contacts")
            print(f"  - {prod_count} products")
            print(f"  - {sales_count} sales transactions")
            print(f"  - {payroll_count} payroll records")
            print(f"  - {opp_count} opportunities")
            print(f"  - {activities_count} activities")
            print(f"  - {leaves_count} leave requests")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"✗ Error during data generation: {e}")
            raise
        finally:
            self.close()


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample data for ISSOFBC Analytics')
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', default='', help='MySQL password')
    parser.add_argument('--database', default='issofbc_analytics', help='Database name')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    parser.add_argument('--employees', type=int, default=150, help='Number of employees')
    parser.add_argument('--contacts', type=int, default=100, help='Number of contacts')
    parser.add_argument('--sales', type=int, default=500, help='Number of sales transactions')
    
    args = parser.parse_args()
    
    generator = SampleDataGenerator(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database,
        seed=args.seed
    )
    
    generator.generate_all(
        emp_count=args.employees,
        con_count=args.contacts,
        sales_count=args.sales
    )

