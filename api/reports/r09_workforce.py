from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query
from api.models import ReportResponse, ChartSpec
from api.filters import DateFilter

router = APIRouter()


@router.get("/r09-workforce-snapshot", response_model=ReportResponse)
def r09_workforce_snapshot(f: DateFilter = Depends(DateFilter)):
    pay_where, pay_params = f.clause("pr.pay_date")
    lv_where,  lv_params  = f.clause("lr.start_date")
    pp, lp = tuple(pay_params), tuple(lv_params)

    headcount_data = query(f"""
        SELECT
            hd.department_name,
            COUNT(DISTINCT he.hr_employee_id)                                                AS headcount,
            SUM(CASE WHEN he.employment_type = 'Full-time' THEN 1 ELSE 0 END)               AS full_time,
            SUM(CASE WHEN he.employment_type = 'Part-time' THEN 1 ELSE 0 END)               AS part_time,
            SUM(CASE WHEN he.employment_type = 'Contract'  THEN 1 ELSE 0 END)               AS contract,
            ROUND(AVG(he.annual_salary), 0)                                                  AS avg_annual_salary,
            COALESCE(SUM(CASE WHEN lr.status='Approved' THEN lr.total_days ELSE 0 END), 0)  AS leave_days_taken
        FROM hr_departments hd
        LEFT JOIN hr_employees he ON hd.dept_id = he.dept_id AND he.employment_status = 'Active'
        LEFT JOIN hr_leave_requests lr ON he.hr_employee_id = lr.hr_employee_id AND {lv_where}
        GROUP BY hd.dept_id, hd.department_name
        ORDER BY headcount DESC
    """, lp)

    payroll_trend = query(f"""
        SELECT
            strftime('%Y-%m', pr.pay_date) AS month,
            ROUND(SUM(pr.total_gross), 2)  AS total_gross,
            ROUND(SUM(pr.total_net), 2)    AS total_net,
            MAX(pr.employee_count)         AS employee_count
        FROM payroll_runs pr
        WHERE pr.status = 'Paid' AND {pay_where}
        GROUP BY strftime('%Y-%m', pr.pay_date)
        ORDER BY month
    """, pp)

    summary_row = query("""
        SELECT
            COUNT(CASE WHEN he.employment_status='Active' THEN 1 END)  AS active_headcount,
            COUNT(CASE WHEN he.employment_type='Full-time' THEN 1 END)  AS full_time,
            COUNT(CASE WHEN he.employment_type='Part-time' THEN 1 END)  AS part_time,
            COUNT(CASE WHEN he.employment_type='Contract'  THEN 1 END)  AS contract,
            COUNT(CASE WHEN lr.status='Pending' THEN 1 END)             AS pending_leave_requests,
            ROUND(AVG(he.annual_salary), 0)                             AS avg_annual_salary
        FROM hr_employees he
        LEFT JOIN hr_leave_requests lr ON he.hr_employee_id = lr.hr_employee_id
    """)[0]

    last_payroll = query("""
        SELECT total_gross, total_net, pay_date, employee_count
        FROM payroll_runs WHERE status='Paid' ORDER BY pay_date DESC LIMIT 1
    """)

    return ReportResponse(
        report_id="r09",
        report_name="Workforce Snapshot",
        description="Headcount by department, leave utilization, and payroll trend (BambooHR + Paywork).",
        sources=["BambooHR", "Paywork"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
        summary={
            **summary_row,
            "last_payroll":  last_payroll[0] if last_payroll else {},
            "payroll_trend": payroll_trend,
        },
        data=headcount_data,
        chart=ChartSpec(
            type="bar",
            title="Headcount by Department",
            x_axis="department_name",
            y_axis=["full_time", "part_time", "contract"],
        ),
    )
