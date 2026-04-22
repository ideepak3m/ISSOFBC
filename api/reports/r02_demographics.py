from datetime import datetime
from fastapi import APIRouter
from api.db import query
from api.models import ReportResponse, ChartSpec

router = APIRouter()

SQL_STATUS = """
    SELECT immigration_status,
           COUNT(*)                                                       AS count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM beneficiaries), 1) AS percentage
    FROM beneficiaries
    GROUP BY immigration_status
    ORDER BY count DESC
"""

SQL_COUNTRY = """
    SELECT country_of_origin AS country, COUNT(*) AS count
    FROM beneficiaries
    GROUP BY country_of_origin
    ORDER BY count DESC
    LIMIT 10
"""

SQL_LANGUAGE = """
    SELECT primary_language AS language, COUNT(*) AS count
    FROM beneficiaries
    GROUP BY primary_language
    ORDER BY count DESC
    LIMIT 10
"""

SQL_SUMMARY = """
    SELECT
        COUNT(*)                                                                 AS total_beneficiaries,
        SUM(CASE WHEN status = 'Active'    THEN 1 ELSE 0 END)                   AS active,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END)                   AS completed,
        COUNT(DISTINCT country_of_origin)                                        AS countries_represented,
        COUNT(DISTINCT primary_language)                                         AS languages_spoken,
        ROUND(AVG(household_size), 1)                                            AS avg_household_size,
        ROUND(
            SUM(CASE WHEN immigration_status = 'Refugee' THEN 1 ELSE 0 END)
            * 100.0 / COUNT(*), 1
        )                                                                        AS refugee_pct
    FROM beneficiaries
"""


@router.get("/r02-beneficiary-demographics", response_model=ReportResponse)
def r02_beneficiary_demographics():
    summary_row   = query(SQL_SUMMARY)[0]
    status_data   = query(SQL_STATUS)
    country_data  = query(SQL_COUNTRY)
    language_data = query(SQL_LANGUAGE)

    # Main data = immigration status breakdown (most analytically useful)
    # Secondary breakdowns embedded in summary for frontend flexibility
    return ReportResponse(
        report_id="r02",
        report_name="Beneficiary Demographics",
        description="Immigration status, country of origin, and language breakdown of all beneficiaries.",
        sources=["Newtract"],
        generated_at=datetime.now().isoformat(),
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
