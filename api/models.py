from pydantic import BaseModel
from typing import Any, Optional


class ChartSpec(BaseModel):
    type: str           # bar | line | pie | grouped_bar | area
    title: str
    x_axis: str
    y_axis: str | list[str]


class ReportResponse(BaseModel):
    report_id: str
    report_name: str
    description: str
    sources: list[str]
    generated_at: str
    summary: dict[str, Any]
    data: list[dict[str, Any]]
    chart: Optional[ChartSpec] = None
