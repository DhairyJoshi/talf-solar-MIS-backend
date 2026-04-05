from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MonthlyKPIResponse(BaseModel):
    id: int
    project_id: int
    month: str
    total_yield_kwh: Optional[float] = None
    pr_percentage: Optional[float] = None
    cuf_percentage: Optional[float] = None
    target_p50_kwh: Optional[float] = None
    revenue: Optional[float] = None
    irradiation_kwh_m2: Optional[float] = None
    computed_at: datetime

    class Config:
        from_attributes = True