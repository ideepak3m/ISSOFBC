from datetime import datetime
from fastapi import APIRouter
from api.db import query
from api.models import ReportResponse, ChartSpec

router = APIRouter()

SQL_HEADCOUNT = """
    SELECT
        hd.department_name,
        COUNT(DISTINCT he.hr_employee_id)                                                AS headcount,
        SUM(CASE WHEN he.employment_type = 'Full-time' THEN 1 ELSE 0 END)               AS full_time,
        SUM(CASE WHEN he.employment_type = 'Part-time' THEN 1 ELSE 0 END)               AS part_time,
        SUM(CASE WHEN he.employment_type = 'Contract'  THEN 1 ELSE 0 END)               AS contract,
        ROUND(AVG(he.annual_salary), 0)                                                  AS avg_annual_salary,
        COALESCE(SUM(CASE WHEN lr.status = 'Approved'
                          THEN lr.total_days ELSE 0 END), 0)                             AS leave_days_taken_ytd
    FROM hr_departments hd
    LEFT JOIN hr_employees he
           ON hd.dept_id = he.dept_id AND he.employment_status = 'Active'
    LEFT JOIN hr_leave_requests lr
           ON he.hr_employee_id = lr.hr_employee_id
          AND lr.start_date >= date('now', '-1 year')
    GROUP BY hd.dept_id, hd.department_name
    ORDER BY headcount DESC
"""

SQL_PAYROLL_TREND = """
    SELECT
        strftime('%Y-%m', pay_date)  AS month,
        ROUND(SUM(total_gross), 2)   AS total_gross,
        ROUND(SUM(total_net), 2)     AS total_net,
        ROUND(SUM(total_deductions), 2) AS total_deductions,
        MAX(employee_count)          AS employee_count
    FROM payroll_runs
    WHERE status = 'Paid'
    GROUP BY strftime('%Y-%m', pay_date)
    ORDER BY month
"""

SQL_SUMMARY = """
    SELECT
        COUNT(CASE WHEN he.employment_status = 'Active' THEN 1 END)      AS active_headcount,
        COUNT(CASE WHEN he.employment_type = 'Full-time' THEN 1 END)     AS full_time,
        COUNT(CASE WHEN he.employment_type = 'Part-time' THEN 1 END)     AS part_time,
        COUNT(CASE WHEN he.employment_type = 'Contract'  THEN 1 END)     AS contract,
        COUNT(CASE WHEN lr.status = 'Pending' THEN 1 END)                AS pending_leave_requests,
        ROUND(AVG(he.annual_salary), 0)                                   AS avg_annual_salary
    FROM hr_employees he
    LEFT JOIN hr_leave_requests lr ON he.hr_employee_id = lr.hr_employee_id
"""

SQL_LAST_PAYROLL = """
    SELECT total_gross, total_net, pay_date, employee_count
    FROM payroll_runs
    WHERE status = 'Paid'
    ORDER BY pay_date DESC
    LIMIT 1
"""


@router.get("/r09-workforce-snapshot", response_model=ReportResponse)
def r09_workforce_snapshot():
    headcount_data  = query(SQL_HEADCOUNT)
    payroll_trend   = query(SQL_PAYROLL_TREND)
    summary_row     = query(SQL_SUMMARY)[0]
    last_payroll    = query(SQL_LAST_PAYROLL)

    return ReportResponse(
        report_id="r09",
        report_name="Workforce Snapshot",
        description="Headcount by department, employment type, leave utilization, and payroll trend. Combines BambooHR and Paywork data.",
        sources=["BambooHR", "Paywork"],
        generated_at=datetime.now().isoformat(),
        summary={
            **summary_row,
            "last_payroll":   last_payroll[0] if last_payroll else {},
            "payroll_trend":  payroll_trend,
        },
        data=headcount_data,
        chart=ChartSpec(
            type="bar",
            title="Headcount by Department",
            x_axis="department_name",
            y_axis=["full_time", "part_time", "contract"],
        ),
    )
