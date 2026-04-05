from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re


class MonthlyDataBase(BaseModel):
    month: str  # YYYY-MM
    energy_kwh: float
    irradiation_kwh_m2: Optional[float] = None
    revenue: Optional[float] = None
    tariff_rate: Optional[float] = None

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("month must be in YYYY-MM format")
        return v


class MonthlyDataCreate(MonthlyDataBase):
    pass


class MonthlyDataResponse(MonthlyDataBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True