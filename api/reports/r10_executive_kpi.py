from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query, query_one
from api.models import ReportResponse
from api.filters import DateFilter

router = APIRouter()


def _scalar(sql: str, params: tuple = ()) -> float | int | None:
    row = query_one(sql, params)
    return list(row.values())[0] if row else None


@router.get("/r10-executive-kpi", response_model=ReportResponse)
def r10_executive_kpi(f: DateFilter = Depends(DateFilter)):
    # Each KPI uses the appropriate date column with kpi_clause (defaults to current year)
    cl_w, cl_p = f.kpi_clause("arrival_date")       # clients
    en_w, en_p = f.kpi_clause("enrollment_date")    # enrollments -- date not on this table directly
    jp_w, jp_p = f.kpi_clause("placement_date")     # placements
    oc_w, oc_p = f.kpi_clause("metric_date")        # outcomes
    sv_w, sv_p = f.kpi_clause("service_date")       # services
    dn_w, dn_p = f.kpi_clause("donation_date")      # donations
    pr_w, pr_p = f.kpi_clause("pay_date")           # payroll

    active_clients     = _scalar(f"SELECT COUNT(*) FROM beneficiaries WHERE status='Active' AND {cl_w}", tuple(cl_p))
    active_enrollments = _scalar("SELECT COUNT(*) FROM program_enrollments WHERE status='Active'")
    placements_ytd     = _scalar(f"SELECT COUNT(*) FROM job_placements WHERE {jp_w}", tuple(jp_p))
    outcomes_ytd       = _scalar(f"SELECT COUNT(*) FROM outcomes WHERE {oc_w}", tuple(oc_p))
    services_mtd       = _scalar(f"SELECT COUNT(*) FROM services_delivered WHERE {sv_w}", tuple(sv_p))
    countries_served   = _scalar("SELECT COUNT(DISTINCT country_of_origin) FROM beneficiaries WHERE status='Active'")
    donations_ytd      = _scalar(f"SELECT ROUND(COALESCE(SUM(donation_amount),0),2) FROM donations WHERE donation_type='Cash' AND {dn_w}", tuple(dn_p))
    active_grant_value = _scalar("SELECT ROUND(COALESCE(SUM(grant_amount),0),2) FROM government_grants WHERE status='Active'")
    pending_expenses   = _scalar("SELECT COUNT(*) FROM expenses WHERE approval_status='Submitted'")
    budget_utilization = _scalar("""
        SELECT ROUND(SUM(actual_ytd)*100.0/NULLIF(SUM(annual_budget),0),1)
        FROM budget_lines bl JOIN gl_accounts ga ON bl.account_id=ga.account_id
        WHERE ga.account_type='Expense'
    """)
    active_headcount   = _scalar("SELECT COUNT(*) FROM hr_employees WHERE employment_status='Active'")
    pending_leave      = _scalar("SELECT COUNT(*) FROM hr_leave_requests WHERE status='Pending'")
    last_payroll_gross = _scalar(f"SELECT total_gross FROM payroll_runs WHERE status='Paid' AND {pr_w} ORDER BY pay_date DESC LIMIT 1", tuple(pr_p))
    last_payroll_date  = _scalar(f"SELECT pay_date   FROM payroll_runs WHERE status='Paid' AND {pr_w} ORDER BY pay_date DESC LIMIT 1", tuple(pr_p))
    payroll_ytd        = _scalar(f"SELECT ROUND(COALESCE(SUM(total_gross),0),2) FROM payroll_runs WHERE status='Paid' AND {pr_w}", tuple(pr_p))

    kpis = [
        {"category": "Clients",  "kpi": "Active Beneficiaries",        "value": active_clients,     "source": "Newtract"},
        {"category": "Clients",  "kpi": "Active Enrollments",          "value": active_enrollments, "source": "Newtract"},
        {"category": "Clients",  "kpi": "Countries Represented",       "value": countries_served,   "source": "Newtract"},
        {"category": "Outcomes", "kpi": "Job Placements",              "value": placements_ytd,     "source": "Newtract"},
        {"category": "Outcomes", "kpi": "Outcomes Achieved",           "value": outcomes_ytd,       "source": "Newtract"},
        {"category": "Outcomes", "kpi": "Services Delivered",          "value": services_mtd,       "source": "Newtract"},
        {"category": "Finance",  "kpi": "Cash Donations",              "value": donations_ytd,      "source": "Business Central"},
        {"category": "Finance",  "kpi": "Active Grant Funding",        "value": active_grant_value, "source": "Business Central"},
        {"category": "Finance",  "kpi": "Expense Budget Utilized (%)", "value": budget_utilization, "source": "Business Central"},
        {"category": "Finance",  "kpi": "Pending Expense Approvals",   "value": pending_expenses,   "source": "Business Central"},
        {"category": "People",   "kpi": "Active Staff Headcount",      "value": active_headcount,   "source": "BambooHR"},
        {"category": "People",   "kpi": "Pending Leave Requests",      "value": pending_leave,      "source": "BambooHR"},
        {"category": "Payroll",  "kpi": "Last Payroll Gross",          "value": last_payroll_gross, "source": "Paywork"},
        {"category": "Payroll",  "kpi": "Last Pay Date",               "value": last_payroll_date,  "source": "Paywork"},
        {"category": "Payroll",  "kpi": "Payroll Cost (Period)",       "value": payroll_ytd,        "source": "Paywork"},
    ]

    return ReportResponse(
        report_id="r10",
        report_name="Executive KPI Dashboard",
        description="Single-view KPI summary from all four source systems.",
        sources=["Newtract", "Business Central", "BambooHR", "Paywork"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
        summary={
            "active_clients":       active_clients,
            "active_grant_funding": active_grant_value,
            "active_headcount":     active_headcount,
            "outcomes_ytd":         outcomes_ytd,
            "payroll_period":       payroll_ytd,
            "donations_period":     donations_ytd,
        },
        data=kpis,
        chart=None,
    )
