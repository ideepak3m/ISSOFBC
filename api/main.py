from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.reports import router as reports_router, REPORT_REGISTRY
from api.adhoc import router as adhoc_router
from api.chatbot import router as chatbot_router

app = FastAPI(
    title="IISofBC Analytics API",
    description="Predefined and ad-hoc analytics for IISofBC — powered by Newtract, Business Central, BambooHR, and Paywork data.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router, prefix="/api/reports", tags=["Predefined Reports"])
app.include_router(adhoc_router,  prefix="/api",          tags=["AI Query"])
app.include_router(chatbot_router, prefix="/api",         tags=["Knowledge Assistant"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "IISofBC Analytics API", "version": "1.0.0"}


@app.get("/api/reports", tags=["Predefined Reports"])
def list_reports():
    """List all available predefined reports."""
    return {"total": len(REPORT_REGISTRY), "reports": REPORT_REGISTRY}
