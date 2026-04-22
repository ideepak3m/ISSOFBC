from datetime import datetime
from fastapi import APIRouter
from api.db import query, query_one
from api.models import ReportResponse

router = APIRouter()


def _scalar(sql: str) -> float | int | None:
    row = query_one(sql)
    return list(row.values())[0] if row else None


@router.get("/r10-executive-kpi", response_model=ReportResponse)
def r10_executive_kpi():
    # --- Newtract ---
    active_clients      = _scalar("SELECT COUNT(*) FROM beneficiaries WHERE status = 'Active'")
    active_enrollments  = _scalar("SELECT COUNT(*) FROM program_enrollments WHERE status = 'Active'")
    placements_ytd      = _scalar("SELECT COUNT(*) FROM job_placements WHERE strftime('%Y', placement_date) = strftime('%Y', 'now')")
    outcomes_ytd        = _scalar("SELECT COUNT(*) FROM outcomes WHERE strftime('%Y', metric_date) = strftime('%Y', 'now')")
    services_mtd        = _scalar("SELECT COUNT(*) FROM services_delivered WHERE strftime('%Y-%m', service_date) = strftime('%Y-%m', 'now')")
    countries_served    = _scalar("SELECT COUNT(DISTINCT country_of_origin) FROM beneficiaries WHERE status = 'Active'")

    # --- Business Central ---
    donations_ytd       = _scalar("SELECT ROUND(COALESCE(SUM(donation_amount),0),2) FROM donations WHERE strftime('%Y', donation_date)=strftime('%Y','now') AND donation_type='Cash'")
    active_grant_value  = _scalar("SELECT ROUND(COALESCE(SUM(grant_amount),0),2) FROM government_grants WHERE status='Active'")
    pending_expenses    = _scalar("SELECT COUNT(*) FROM expenses WHERE approval_status='Submitted'")
    budget_utilization  = _scalar("""
        SELECT ROUND(SUM(actual_ytd)*100.0/NULLIF(SUM(annual_budget),0),1)
        FROM budget_lines bl
        JOIN gl_accounts ga ON bl.account_id=ga.account_id
        WHERE bl.fiscal_year=strftime('%Y','now') AND ga.account_type='Expense'
    """)

    # --- BambooHR ---
    active_headcount    = _scalar("SELECT COUNT(*) FROM hr_employees WHERE employment_status='Active'")
    pending_leave       = _scalar("SELECT COUNT(*) FROM hr_leave_requests WHERE status='Pending'")

    # --- Paywork ---
    last_payroll_gross  = _scalar("SELECT total_gross FROM payroll_runs WHERE status='Paid' ORDER BY pay_date DESC LIMIT 1")
    last_payroll_date   = _scalar("SELECT pay_date   FROM payroll_runs WHERE status='Paid' ORDER BY pay_date DESC LIMIT 1")
    payroll_ytd         = _scalar("SELECT ROUND(COALESCE(SUM(total_gross),0),2) FROM payroll_runs WHERE status='Paid' AND strftime('%Y',pay_date)=strftime('%Y','now')")

    kpis = [
        # Newtract
        {"category": "Clients",   "kpi": "Active Beneficiaries",     "value": active_clients,     "source": "Newtract"},
        {"category": "Clients",   "kpi": "Active Enrollments",       "value": active_enrollments, "source": "Newtract"},
        {"category": "Clients",   "kpi": "Countries Represented",    "value": countries_served,   "source": "Newtract"},
        {"category": "Outcomes",  "kpi": "Job Placements (YTD)",     "value": placements_ytd,     "source": "Newtract"},
        {"category": "Outcomes",  "kpi": "Outcomes Achieved (YTD)",  "value": outcomes_ytd,       "source": "Newtract"},
        {"category": "Outcomes",  "kpi": "Services Delivered (MTD)", "value": services_mtd,       "source": "Newtract"},
        # Business Central
        {"category": "Finance",   "kpi": "Cash Donations (YTD)",     "value": donations_ytd,      "source": "Business Central"},
        {"category": "Finance",   "kpi": "Active Grant Funding",     "value": active_grant_value, "source": "Business Central"},
        {"category": "Finance",   "kpi": "Expense Budget Utilized (%)", "value": budget_utilization, "source": "Business Central"},
        {"category": "Finance",   "kpi": "Pending Expense Approvals","value": pending_expenses,   "source": "Business Central"},
        # BambooHR
        {"category": "People",    "kpi": "Active Staff Headcount",   "value": active_headcount,   "source": "BambooHR"},
        {"category": "People",    "kpi": "Pending Leave Requests",   "value": pending_leave,      "source": "BambooHR"},
        # Paywork
        {"category": "Payroll",   "kpi": "Last Payroll Gross",       "value": last_payroll_gross, "source": "Paywork"},
        {"category": "Payroll",   "kpi": "Last Pay Date",            "value": last_payroll_date,  "source": "Paywork"},
        {"category": "Payroll",   "kpi": "Payroll Cost (YTD)",       "value": payroll_ytd,        "source": "Paywork"},
    ]

    return ReportResponse(
        report_id="r10",
        report_name="Executive KPI Dashboard",
        description="Single-view KPI summary pulling live metrics from all four source systems: Newtract, Business Central, BambooHR, and Paywork.",
        sources=["Newtract", "Business Central", "BambooHR", "Paywork"],
        generated_at=datetime.now().isoformat(),
        summary={
            "active_clients":       active_clients,
            "active_grant_funding": active_grant_value,
            "active_headcount":     active_headcount,
            "outcomes_ytd":         outcomes_ytd,
            "payroll_ytd":          payroll_ytd,
            "donations_ytd":        donations_ytd,
        },
        data=kpis,
        chart=None,  # KPI tiles — chart type determined by frontend
    )
