from datetime import datetime
from fastapi import APIRouter
from api.db import query
from api.models import ReportResponse, ChartSpec

router = APIRouter()

SQL_MONTHLY = """
    SELECT
        strftime('%Y-%m', donation_date)             AS month,
        SUM(CASE WHEN donation_type = 'Cash'    THEN donation_amount ELSE 0 END) AS cash,
        SUM(CASE WHEN donation_type = 'Pledge'  THEN donation_amount ELSE 0 END) AS pledges,
        SUM(CASE WHEN donation_type = 'In-kind' THEN donation_amount ELSE 0 END) AS in_kind,
        COUNT(*)                                                                  AS total_donations
    FROM donations
    GROUP BY strftime('%Y-%m', donation_date)
    ORDER BY month
"""

SQL_GRANTS_BY_SOURCE = """
    SELECT
        funding_source,
        grant_year,
        COUNT(*)                        AS grant_count,
        SUM(grant_amount)               AS total_awarded,
        SUM(amount_approved_ytd)        AS total_approved_ytd
    FROM government_grants
    GROUP BY funding_source, grant_year
    ORDER BY grant_year DESC, total_awarded DESC
"""

SQL_SUMMARY = """
    SELECT
        ROUND(SUM(CASE WHEN donation_type = 'Cash' THEN donation_amount ELSE 0 END), 2)   AS total_cash_donations,
        ROUND(SUM(CASE WHEN donation_type = 'Pledge' THEN donation_amount ELSE 0 END), 2) AS total_pledges,
        COUNT(DISTINCT donor_name)                                                          AS unique_donors,
        ROUND(AVG(CASE WHEN donation_type = 'Cash' THEN donation_amount END), 2)           AS avg_cash_donation,
        ROUND(SUM(CASE WHEN strftime('%Y', donation_date) = strftime('%Y', 'now')
                  AND donation_type = 'Cash' THEN donation_amount ELSE 0 END), 2)           AS cash_ytd
    FROM donations
"""

SQL_GRANT_SUMMARY = """
    SELECT
        COUNT(*)                           AS total_grants,
        SUM(grant_amount)                  AS total_grant_value,
        SUM(amount_approved_ytd)           AS total_approved_ytd,
        SUM(CASE WHEN status = 'Active' THEN grant_amount ELSE 0 END) AS active_grant_value
    FROM government_grants
"""


@router.get("/r04-donation-funding-trends", response_model=ReportResponse)
def r04_donation_funding_trends():
    monthly_data   = query(SQL_MONTHLY)
    grants_data    = query(SQL_GRANTS_BY_SOURCE)
    summary_row    = query(SQL_SUMMARY)[0]
    grant_summary  = query(SQL_GRANT_SUMMARY)[0]

    return ReportResponse(
        report_id="r04",
        report_name="Donation & Funding Trends",
        description="Monthly donation totals by type and government grant summary by source and year.",
        sources=["Business Central"],
        generated_at=datetime.now().isoformat(),
        summary={
            **summary_row,
            **grant_summary,
            "total_funding": round(
                (summary_row["total_cash_donations"] or 0)
                + (grant_summary["total_grant_value"] or 0), 2
            ),
            "grants_by_source": grants_data,
        },
        data=monthly_data,
        chart=ChartSpec(
            type="line",
            title="Monthly Cash Donations Over Time",
            x_axis="month",
            y_axis="cash",
        ),
    )
