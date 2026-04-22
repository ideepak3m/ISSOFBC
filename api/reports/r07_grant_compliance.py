from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query
from api.models import ReportResponse, ChartSpec
from api.filters import DateFilter

router = APIRouter()


@router.get("/r07-grant-compliance", response_model=ReportResponse)
def r07_grant_compliance(f: DateFilter = Depends(DateFilter)):
    where, params = f.year_col_clause("gg.grant_year")
    p = tuple(params)

    data = query(f"""
        SELECT
            gg.grant_name, gg.grant_number, gg.funding_source, gg.grant_year,
            gg.grant_amount, gg.amount_approved_ytd,
            ROUND(gg.amount_approved_ytd * 100.0 / NULLIF(gg.grant_amount, 0), 1) AS utilization_pct,
            gg.status, p.program_name,
            COUNT(DISTINCT pe.beneficiary_id)                                       AS beneficiaries_served,
            COUNT(DISTINCT o.outcome_id)                                            AS outcomes_achieved,
            ROUND(gg.grant_amount / NULLIF(COUNT(DISTINCT pe.beneficiary_id), 0), 2) AS grant_cost_per_client
        FROM government_grants gg
        LEFT JOIN programs p ON gg.program_id = p.program_id
        LEFT JOIN program_enrollments pe ON p.program_id = pe.program_id
        LEFT JOIN outcomes o ON pe.beneficiary_id = o.beneficiary_id AND o.program_id = p.program_id
        WHERE {where}
        GROUP BY gg.grant_id
        ORDER BY gg.grant_year DESC, gg.grant_amount DESC
    """, p)

    summary_row = query(f"""
        SELECT
            COUNT(*)                                                                    AS total_grants,
            COUNT(CASE WHEN status = 'Active' THEN 1 END)                              AS active_grants,
            ROUND(SUM(grant_amount), 2)                                                 AS total_awarded,
            ROUND(SUM(amount_approved_ytd), 2)                                          AS total_approved_ytd,
            ROUND(SUM(amount_approved_ytd)*100.0/NULLIF(SUM(grant_amount),0),1)         AS overall_utilization_pct
        FROM government_grants gg WHERE {where}
    """, p)[0]

    return ReportResponse(
        report_id="r07",
        report_name="Grant Compliance Overview",
        description="Grant utilization rates, clients served per grant, and outcomes achieved.",
        sources=["Business Central", "Newtract"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
        summary={
            **summary_row,
            "total_clients_funded":  sum(r["beneficiaries_served"] or 0 for r in data),
            "total_outcomes_funded": sum(r["outcomes_achieved"]    or 0 for r in data),
        },
        data=data,
        chart=ChartSpec(
            type="grouped_bar",
            title="Grant Awarded vs Approved YTD",
            x_axis="grant_name",
            y_axis=["grant_amount", "amount_approved_ytd"],
        ),
    )
