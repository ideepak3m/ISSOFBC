from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query
from api.models import ReportResponse, ChartSpec
from api.filters import DateFilter

router = APIRouter()

SQL = """
    SELECT
        p.program_name,
        p.program_code,
        p.max_capacity,
        COUNT(pe.enrollment_id)                                                          AS total_enrollments,
        SUM(CASE WHEN pe.status = 'Active'      THEN 1 ELSE 0 END)                      AS active,
        SUM(CASE WHEN pe.status = 'Completed'   THEN 1 ELSE 0 END)                      AS completed,
        SUM(CASE WHEN pe.status = 'Dropped Out' THEN 1 ELSE 0 END)                      AS dropped_out,
        SUM(CASE WHEN pe.status = 'On Hold'     THEN 1 ELSE 0 END)                      AS on_hold,
        ROUND(AVG(pe.attendance_rate), 1)                                                AS avg_attendance_pct,
        ROUND(
            SUM(CASE WHEN pe.status = 'Completed' THEN 1 ELSE 0 END) * 100.0
            / NULLIF(COUNT(pe.enrollment_id), 0), 1
        )                                                                                AS completion_rate_pct
    FROM programs p
    LEFT JOIN program_enrollments pe ON p.program_id = pe.program_id
    WHERE {where}
    GROUP BY p.program_id
    ORDER BY total_enrollments DESC
"""


@router.get("/r01-enrollment-summary", response_model=ReportResponse)
def r01_enrollment_summary(f: DateFilter = Depends(DateFilter)):
    where, params = f.clause("pe.enrollment_date")
    data = query(SQL.format(where=where), tuple(params))

    total_enrollments = sum(r["total_enrollments"] or 0 for r in data)
    total_completed   = sum(r["completed"]         or 0 for r in data)
    total_active      = sum(r["active"]            or 0 for r in data)
    avg_attendance    = round(
        sum((r["avg_attendance_pct"] or 0) for r in data) / len(data), 1
    ) if data else 0

    return ReportResponse(
        report_id="r01",
        report_name="Program Enrollment Summary",
        description="Enrollment counts, status breakdown, and attendance rates per program.",
        sources=["Newtract"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
        summary={
            "total_programs":          len(data),
            "total_enrollments":       total_enrollments,
            "total_active":            total_active,
            "total_completed":         total_completed,
            "overall_completion_rate": round(total_completed * 100 / total_enrollments, 1) if total_enrollments else 0,
            "overall_avg_attendance":  avg_attendance,
        },
        data=data,
        chart=ChartSpec(
            type="bar",
            title="Enrollments by Program",
            x_axis="program_name",
            y_axis=["active", "completed", "dropped_out", "on_hold"],
        ),
    )
