from datetime import datetime
from fastapi import APIRouter, Depends
from api.db import query
from api.models import ReportResponse, ChartSpec
from api.filters import DateFilter

router = APIRouter()


@router.get("/r06-program-cost-efficiency", response_model=ReportResponse)
def r06_program_cost_efficiency(f: DateFilter = Depends(DateFilter)):
    where, params = f.clause("e.expense_date")
    p = tuple(params)

    data = query(f"""
        SELECT
            p.program_name,
            COUNT(DISTINCT pe.beneficiary_id)                                          AS beneficiaries_served,
            COUNT(DISTINCT CASE WHEN pe.status = 'Completed'
                                THEN pe.beneficiary_id END)                            AS completers,
            COUNT(DISTINCT o.outcome_id)                                               AS outcomes_achieved,
            ROUND(COALESCE(SUM(e.amount), 0), 2)                                       AS total_expenses,
            ROUND(COALESCE(SUM(e.amount), 0)
                / NULLIF(COUNT(DISTINCT pe.beneficiary_id), 0), 2)                     AS cost_per_beneficiary,
            ROUND(COALESCE(SUM(e.amount), 0)
                / NULLIF(COUNT(DISTINCT o.outcome_id), 0), 2)                          AS cost_per_outcome
        FROM programs p
        LEFT JOIN program_enrollments pe ON p.program_id = pe.program_id
        LEFT JOIN outcomes o
               ON pe.beneficiary_id = o.beneficiary_id AND o.program_id = p.program_id
        LEFT JOIN expenses e
               ON e.program_id = p.program_id
              AND e.approval_status IN ('Approved', 'Reimbursed')
              AND {where}
        GROUP BY p.program_id, p.program_name
        ORDER BY cost_per_beneficiary ASC
    """, p)

    total_expenses      = sum(r["total_expenses"]       or 0 for r in data)
    total_beneficiaries = sum(r["beneficiaries_served"] or 0 for r in data)
    total_outcomes      = sum(r["outcomes_achieved"]    or 0 for r in data)

    return ReportResponse(
        report_id="r06",
        report_name="Program Cost Efficiency",
        description="Cost per beneficiary and cost per outcome per program (Newtract + Business Central).",
        sources=["Newtract", "Business Central"],
        generated_at=datetime.now().isoformat(),
        filter_applied=f.label,
        summary={
            "total_program_expenses":       round(total_expenses, 2),
            "total_beneficiaries_served":   total_beneficiaries,
            "total_outcomes_achieved":      total_outcomes,
            "blended_cost_per_beneficiary": round(total_expenses / total_beneficiaries, 2) if total_beneficiaries else 0,
            "blended_cost_per_outcome":     round(total_expenses / total_outcomes, 2)      if total_outcomes      else 0,
        },
        data=data,
        chart=ChartSpec(
            type="bar",
            title="Cost per Beneficiary by Program",
            x_axis="program_name",
            y_axis="cost_per_beneficiary",
        ),
    )
