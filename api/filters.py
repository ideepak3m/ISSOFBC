from fastapi import Query
from typing import Optional


class DateFilter:
    def __init__(
        self,
        year:       Optional[int] = Query(None, description="Filter by calendar/fiscal year"),
        start_date: Optional[str] = Query(None, description="Custom range start (YYYY-MM-DD)"),
        end_date:   Optional[str] = Query(None, description="Custom range end   (YYYY-MM-DD)"),
    ):
        self.year       = year
        self.start_date = start_date
        self.end_date   = end_date

    def clause(self, col: str) -> tuple[str, list]:
        """WHERE fragment for a DATE/DATETIME column."""
        if self.year:
            return f"strftime('%Y', {col}) = ?", [str(self.year)]
        if self.start_date and self.end_date:
            return f"{col} BETWEEN ? AND ?", [self.start_date, self.end_date]
        if self.start_date:
            return f"{col} >= ?", [self.start_date]
        if self.end_date:
            return f"{col} <= ?", [self.end_date]
        return "1=1", []

    def year_col_clause(self, col: str) -> tuple[str, list]:
        """WHERE fragment for an INTEGER year column (e.g. fiscal_year)."""
        if self.year:
            return f"{col} = ?", [self.year]
        if self.start_date and self.end_date:
            return f"{col} BETWEEN ? AND ?", [int(self.start_date[:4]), int(self.end_date[:4])]
        if self.start_date:
            return f"{col} >= ?", [int(self.start_date[:4])]
        if self.end_date:
            return f"{col} <= ?", [int(self.end_date[:4])]
        return "1=1", []

    def kpi_clause(self, col: str) -> tuple[str, list]:
        """Like clause() but defaults to current year when no filter given."""
        if self.year:
            return f"strftime('%Y', {col}) = ?", [str(self.year)]
        if self.start_date and self.end_date:
            return f"{col} BETWEEN ? AND ?", [self.start_date, self.end_date]
        if self.start_date:
            return f"{col} >= ?", [self.start_date]
        if self.end_date:
            return f"{col} <= ?", [self.end_date]
        return f"strftime('%Y', {col}) = strftime('%Y', 'now')", []

    @property
    def label(self) -> str:
        if self.year:
            return str(self.year)
        if self.start_date and self.end_date:
            return f"{self.start_date} to {self.end_date}"
        if self.start_date:
            return f"From {self.start_date}"
        if self.end_date:
            return f"Until {self.end_date}"
        return "All Time"
