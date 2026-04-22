from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query
from api.models import ReportResponse, ChartSpec
from api.filters import DateFilter

router = APIRouter()


@router.get("/r02-beneficiary-demographics", response_model=ReportResponse)
def r02_beneficiary_demographics(f: DateFilter = Depends(DateFilter)):
    where, params = f.clause("b.arrival_date")
    p = tuple(params)

    status_data = query(f"""
        SELECT immigration_status,
               COUNT(*) AS count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM beneficiaries WHERE {where}), 1) AS percentage
        FROM beneficiaries b
        WHERE {where}
        GROUP BY immigration_status ORDER BY count DESC
    """, p + p)

    country_data = query(f"""
        SELECT country_of_origin AS country, COUNT(*) AS count
        FROM beneficiaries b WHERE {where}
        GROUP BY country_of_origin ORDER BY count DESC LIMIT 10
    """, p)

    language_data = query(f"""
        SELECT primary_language AS language, COUNT(*) AS count
        FROM beneficiaries b WHERE {where}
        GROUP BY primary_language ORDER BY count DESC LIMIT 10
    """, p)

    summary_row = query(f"""
        SELECT
            COUNT(*)                                                                 AS total_beneficiaries,
            SUM(CASE WHEN status = 'Active'    THEN 1 ELSE 0 END)                   AS active,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END)                   AS completed,
            COUNT(DISTINCT country_of_origin)                                        AS countries_represented,
            COUNT(DISTINCT primary_language)                                         AS languages_spoken,
            ROUND(AVG(household_size), 1)                                            AS avg_household_size,
            ROUND(
                SUM(CASE WHEN immigration_status = 'Refugee' THEN 1 ELSE 0 END)
                * 100.0 / NULLIF(COUNT(*), 0), 1
            )                                                                        AS refugee_pct
        FROM beneficiaries b WHERE {where}
    """, p)[0]

    return ReportResponse(
        report_id="r02",
        report_name="Beneficiary Demographics",
        description="Immigration status, country of origin, and language breakdown of beneficiaries.",
        sources=["Newtract"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
        summary={
            **summary_row,
            "top_countries":  country_data,
            "top_languages":  language_data,
        },
        data=status_data,
        chart=ChartSpec(
            type="pie",
            title="Beneficiaries by Immigration Status",
            x_axis="immigration_status",
            y_axis="count",
        ),
    )
