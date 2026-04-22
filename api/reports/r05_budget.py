from datetime import datetime
from fastapi import APIRouter
from api.db import query
from api.models import ReportResponse, ChartSpec

router = APIRouter()

SQL = """
    SELECT
        bl.fiscal_year,
        ga.account_type,
        ga.account_category,
        ga.account_name,
        ROUND(SUM(bl.annual_budget), 2)  AS annual_budget,
        ROUND(SUM(bl.actual_ytd), 2)     AS actual_ytd,
        ROUND(
            SUM(bl.actual_ytd) * 100.0 / NULLIF(SUM(bl.annual_budget), 0), 1
        )                                AS utilization_pct,
        ROUND(SUM(bl.annual_budget) - SUM(bl.actual_ytd), 2) AS variance
    FROM budget_lines bl
    JOIN gl_accounts ga ON bl.account_id = ga.account_id
    GROUP BY bl.fiscal_year, ga.account_id
    ORDER BY bl.fiscal_year, ga.account_type, ga.account_code
"""

SQL_SUMMARY = """
    SELECT
        bl.fiscal_year,
        ROUND(SUM(bl.annual_budget), 2)   AS total_budget,
        ROUND(SUM(bl.actual_ytd), 2)      AS total_actual,
        ROUND(
            SUM(bl.actual_ytd) * 100.0 / NULLIF(SUM(bl.annual_budget), 0), 1
        )                                  AS overall_utilization_pct,
        SUM(CASE WHEN bl.actual_ytd > bl.annual_budget THEN 1 ELSE 0 END) AS over_budget_lines
    FROM budget_lines bl
    GROUP BY bl.fiscal_year
    ORDER BY bl.fiscal_year
"""


@router.get("/r05-budget-vs-actuals", response_model=ReportResponse)
def r05_budget_vs_actuals():
    data        = query(SQL)
    summary_raw = query(SQL_SUMMARY)

    # Use most recent fiscal year for top-level summary
    latest = summary_raw[-1] if summary_raw else {}

    return ReportResponse(
        report_id="r05",
        report_name="Budget vs Actuals",
        description="Budgeted vs actual spend per GL account and program for each fiscal year.",
        sources=["Business Central"],
        generated_at=datetime.now().isoformat(),
        summary={
            **latest,
            "by_year": summary_raw,
        },
        data=data,
        chart=ChartSpec(
            type="grouped_bar",
            title="Budget vs Actuals by Account",
            x_axis="account_name",
            y_axis=["annual_budget", "actual_ytd"],
        ),
    )
