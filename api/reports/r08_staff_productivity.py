from datetime import datetime
from fastapi import APIRouter
from api.db import query
from api.models import ReportResponse, ChartSpec

router = APIRouter()

SQL = """
    SELECT
        sv.first_name || ' ' || sv.last_name                                    AS staff_name,
        sv.person_type,
        COALESCE(hd.department_name, sv.department)                             AS department,
        COUNT(DISTINCT sd.service_id)                                           AS services_delivered,
        ROUND(SUM(sd.duration_minutes) / 60.0, 1)                              AS hours_of_service,
        COUNT(DISTINCT sd.beneficiary_id)                                       AS unique_clients,
        ROUND(COALESCE(SUM(pr.gross_pay), 0), 2)                               AS total_gross_pay,
        CASE
            WHEN COUNT(DISTINCT sd.service_id) > 0 AND SUM(pr.gross_pay) > 0
            THEN ROUND(SUM(pr.gross_pay) / COUNT(DISTINCT sd.service_id), 2)
            ELSE NULL
        END                                                                     AS cost_per_service
    FROM staff_volunteers sv
    LEFT JOIN hr_employees  he ON sv.person_id = he.person_id
    LEFT JOIN hr_departments hd ON he.dept_id  = hd.dept_id
    LEFT JOIN services_delivered sd ON sv.person_id = sd.provider_id
    LEFT JOIN payroll_records    pr ON sv.person_id = pr.person_id
    WHERE sv.employment_status = 'Active'
    GROUP BY sv.person_id
    ORDER BY services_delivered DESC
"""


@router.get("/r08-staff-productivity", response_model=ReportResponse)
def r08_staff_productivity():
    data = query(SQL)

    total_services  = sum(r["services_delivered"] or 0 for r in data)
    total_hours     = round(sum(r["hours_of_service"] or 0 for r in data), 1)
    total_payroll   = round(sum(r["total_gross_pay"]  or 0 for r in data), 2)
    total_clients   = len({r["unique_clients"] for r in data if r["unique_clients"]})

    return ReportResponse(
        report_id="r08",
        report_name="Staff Productivity vs Payroll Cost",
        description="Services delivered, hours served, and unique clients per staff member, measured against their total payroll cost. Draws from Newtract, BambooHR, and Paywork.",
        sources=["Newtract", "BambooHR", "Paywork"],
        generated_at=datetime.now().isoformat(),
        summary={
            "total_active_staff":    len(data),
            "total_services":        total_services,
            "total_hours_of_service": total_hours,
            "total_payroll_cost":    total_payroll,
            "blended_cost_per_service": round(total_payroll / total_services, 2) if total_services else 0,
        },
        data=data,
        chart=ChartSpec(
            type="bar",
            title="Services Delivered per Staff Member",
            x_axis="staff_name",
            y_axis="services_delivered",
        ),
    )
