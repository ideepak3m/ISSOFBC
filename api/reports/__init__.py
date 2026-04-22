from fastapi import APIRouter
from .r01_enrollment       import router as r01
from .r02_demographics     import router as r02
from .r03_placements       import router as r03
from .r04_donations        import router as r04
from .r05_budget           import router as r05
from .r06_cost_efficiency  import router as r06
from .r07_grant_compliance import router as r07
from .r08_staff_productivity import router as r08
from .r09_workforce        import router as r09
from .r10_executive_kpi    import router as r10

router = APIRouter()
for r in [r01, r02, r03, r04, r05, r06, r07, r08, r09, r10]:
    router.include_router(r)

REPORT_REGISTRY = [
    {"report_id": "r01", "name": "Program Enrollment Summary",      "sources": ["Newtract"],                                    "path": "/api/reports/r01-enrollment-summary"},
    {"report_id": "r02", "name": "Beneficiary Demographics",        "sources": ["Newtract"],                                    "path": "/api/reports/r02-beneficiary-demographics"},
    {"report_id": "r03", "name": "Job Placement Outcomes",          "sources": ["Newtract"],                                    "path": "/api/reports/r03-job-placement-outcomes"},
    {"report_id": "r04", "name": "Donation & Funding Trends",       "sources": ["Business Central"],                            "path": "/api/reports/r04-donation-funding-trends"},
    {"report_id": "r05", "name": "Budget vs Actuals",               "sources": ["Business Central"],                            "path": "/api/reports/r05-budget-vs-actuals"},
    {"report_id": "r06", "name": "Program Cost Efficiency",         "sources": ["Newtract", "Business Central"],                "path": "/api/reports/r06-program-cost-efficiency"},
    {"report_id": "r07", "name": "Grant Compliance Overview",       "sources": ["Business Central", "Newtract"],                "path": "/api/reports/r07-grant-compliance"},
    {"report_id": "r08", "name": "Staff Productivity vs Payroll",   "sources": ["Newtract", "BambooHR", "Paywork"],             "path": "/api/reports/r08-staff-productivity"},
    {"report_id": "r09", "name": "Workforce Snapshot",              "sources": ["BambooHR", "Paywork"],                        "path": "/api/reports/r09-workforce-snapshot"},
    {"report_id": "r10", "name": "Executive KPI Dashboard",         "sources": ["Newtract", "Business Central", "BambooHR", "Paywork"], "path": "/api/reports/r10-executive-kpi"},
]
