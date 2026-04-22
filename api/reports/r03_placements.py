from datetime import datetime
from fastapi import APIRouter
from api.db import query
from api.models import ReportResponse, ChartSpec

router = APIRouter()

SQL_BY_PROGRAM = """
    SELECT
        p.program_name,
        COUNT(DISTINCT pe.beneficiary_id)                                              AS total_completers,
        COUNT(DISTINCT jp.beneficiary_id)                                              AS placed,
        ROUND(
            COUNT(DISTINCT jp.beneficiary_id) * 100.0
            / NULLIF(COUNT(DISTINCT pe.beneficiary_id), 0), 1
        )                                                                              AS placement_rate_pct,
        ROUND(AVG(jp.salary_range_start), 0)                                           AS avg_starting_salary
    FROM programs p
    LEFT JOIN program_enrollments pe
           ON p.program_id = pe.program_id AND pe.status = 'Completed'
    LEFT JOIN job_placements jp
           ON pe.beneficiary_id = jp.beneficiary_id
    GROUP BY p.program_id, p.program_name
    ORDER BY placement_rate_pct DESC
"""

SQL_BY_INDUSTRY = """
    SELECT industry_sector, COUNT(*) AS placements
    FROM job_placements
    GROUP BY industry_sector
    ORDER BY placements DESC
"""

SQL_SUMMARY = """
    SELECT
        COUNT(DISTINCT pe.beneficiary_id)                                    AS total_completers,
        COUNT(DISTINCT jp.beneficiary_id)                                    AS total_placed,
        ROUND(AVG(jp.salary_range_start), 0)                                 AS avg_starting_salary,
        SUM(CASE WHEN jp.employment_type = 'Full-time' THEN 1 ELSE 0 END)   AS full_time_placements,
        SUM(CASE WHEN jp.employment_type = 'Part-time' THEN 1 ELSE 0 END)   AS part_time_placements
    FROM program_enrollments pe
    LEFT JOIN job_placements jp ON pe.beneficiary_id = jp.beneficiary_id
    WHERE pe.status = 'Completed'
"""


@router.get("/r03-job-placement-outcomes", response_model=ReportResponse)
def r03_job_placement_outcomes():
    data          = query(SQL_BY_PROGRAM)
    industry_data = query(SQL_BY_INDUSTRY)
    summary_row   = query(SQL_SUMMARY)[0]

    overall_rate = round(
        (summary_row["total_placed"] or 0) * 100
        / (summary_row["total_completers"] or 1), 1
    )

    return ReportResponse(
        report_id="r03",
        report_name="Job Placement Outcomes",
        description="Placement rates by program, employment type breakdown, and industry distribution.",
        sources=["Newtract"],
        generated_at=datetime.now().isoformat(),
        summary={
            **summary_row,
            "overall_placement_rate_pct": overall_rate,
            "placements_by_industry":     industry_data,
        },
        data=data,
        chart=ChartSpec(
            type="bar",
            title="Job Placement Rate by Program (%)",
            x_axis="program_name",
            y_axis="placement_rate_pct",
        ),
    )
