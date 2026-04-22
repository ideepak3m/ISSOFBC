from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query
from api.models import ReportResponse, ChartSpec
from api.filters import DateFilter

router = APIRouter()


@router.get("/r08-staff-productivity", response_model=ReportResponse)
def r08_staff_productivity(f: DateFilter = Depends(DateFilter)):
    svc_where, svc_params = f.clause("sd.service_date")
    pay_where, pay_params = f.clause("pr.created_date")
    sp, pp = tuple(svc_params), tuple(pay_params)

    data = query(f"""
        SELECT
            sv.first_name || ' ' || sv.last_name                                AS staff_name,
            sv.person_type,
            COALESCE(hd.department_name, sv.department)                         AS department,
            COUNT(DISTINCT sd.service_id)                                       AS services_delivered,
            ROUND(SUM(sd.duration_minutes) / 60.0, 1)                          AS hours_of_service,
            COUNT(DISTINCT sd.beneficiary_id)                                   AS unique_clients,
            ROUND(COALESCE(SUM(pr.gross_pay), 0), 2)                           AS total_gross_pay,
            CASE
                WHEN COUNT(DISTINCT sd.service_id) > 0 AND SUM(pr.gross_pay) > 0
                THEN ROUND(SUM(pr.gross_pay) / COUNT(DISTINCT sd.service_id), 2)
                ELSE NULL
            END                                                                 AS cost_per_service
        FROM staff_volunteers sv
        LEFT JOIN hr_employees   he ON sv.person_id = he.person_id
        LEFT JOIN hr_departments hd ON he.dept_id   = hd.dept_id
        LEFT JOIN services_delivered sd ON sv.person_id = sd.provider_id AND {svc_where}
        LEFT JOIN payroll_records    pr ON sv.person_id = pr.person_id   AND {pay_where}
        WHERE sv.employment_status = 'Active'
        GROUP BY sv.person_id
        ORDER BY services_delivered DESC
    """, sp + pp)

    total_services = sum(r["services_delivered"] or 0 for r in data)
    total_hours    = round(sum(r["hours_of_service"] or 0 for r in data), 1)
    total_payroll  = round(sum(r["total_gross_pay"]  or 0 for r in data), 2)

    return ReportResponse(
        report_id="r08",
        report_name="Staff Productivity vs Payroll Cost",
        description="Services delivered and payroll cost per staff member (Newtract + BambooHR + Paywork).",
        sources=["Newtract", "BambooHR", "Paywork"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
        summary={
            "total_active_staff":        len(data),
            "total_services":            total_services,
            "total_hours_of_service":    total_hours,
            "total_payroll_cost":        total_payroll,
            "blended_cost_per_service":  round(total_payroll / total_services, 2) if total_services else 0,
        },
        data=data,
        chart=ChartSpec(
            type="bar",
            title="Services Delivered per Staff Member",
            x_axis="staff_name",
            y_axis="services_delivered",
        ),
    )
