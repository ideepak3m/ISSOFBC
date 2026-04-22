from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query
from api.models import ReportResponse, ChartSpec
from api.filters import DateFilter

router = APIRouter()


@router.get("/r04-donation-funding-trends", response_model=ReportResponse)
def r04_donation_funding_trends(f: DateFilter = Depends(DateFilter)):
    don_where, don_params = f.clause("donation_date")
    yr_where,  yr_params  = f.year_col_clause("grant_year")
    dp, yp = tuple(don_params), tuple(yr_params)

    monthly_data = query(f"""
        SELECT
            strftime('%Y-%m', donation_date)             AS month,
            SUM(CASE WHEN donation_type = 'Cash'    THEN donation_amount ELSE 0 END) AS cash,
            SUM(CASE WHEN donation_type = 'Pledge'  THEN donation_amount ELSE 0 END) AS pledges,
            SUM(CASE WHEN donation_type = 'In-kind' THEN donation_amount ELSE 0 END) AS in_kind,
            COUNT(*)                                                                  AS total_donations
        FROM donations
        WHERE {don_where}
        GROUP BY strftime('%Y-%m', donation_date)
        ORDER BY month
    """, dp)

    grants_data = query(f"""
        SELECT
            funding_source, grant_year,
            COUNT(*)                   AS grant_count,
            SUM(grant_amount)          AS total_awarded,
            SUM(amount_approved_ytd)   AS total_approved_ytd
        FROM government_grants
        WHERE {yr_where}
        GROUP BY funding_source, grant_year
        ORDER BY grant_year DESC, total_awarded DESC
    """, yp)

    summary_row = query(f"""
        SELECT
            ROUND(SUM(CASE WHEN donation_type='Cash'   THEN donation_amount ELSE 0 END), 2) AS total_cash_donations,
            ROUND(SUM(CASE WHEN donation_type='Pledge' THEN donation_amount ELSE 0 END), 2) AS total_pledges,
            COUNT(DISTINCT donor_name)                                                        AS unique_donors,
            ROUND(AVG(CASE WHEN donation_type='Cash' THEN donation_amount END), 2)           AS avg_cash_donation
        FROM donations WHERE {don_where}
    """, dp)[0]

    grant_summary = query(f"""
        SELECT
            COUNT(*)                                                                AS total_grants,
            ROUND(SUM(grant_amount), 2)                                             AS total_grant_value,
            ROUND(SUM(amount_approved_ytd), 2)                                      AS total_approved_ytd,
            SUM(CASE WHEN status='Active' THEN grant_amount ELSE 0 END)             AS active_grant_value
        FROM government_grants WHERE {yr_where}
    """, yp)[0]

    return ReportResponse(
        report_id="r04",
        report_name="Donation & Funding Trends",
        description="Monthly donation totals by type and government grant summary by source and year.",
        sources=["Business Central"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
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
