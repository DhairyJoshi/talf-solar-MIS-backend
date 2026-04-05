from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ModuleBuildBase(BaseModel):
    manufacturer: str
    model_name: str
    rated_power_wp: float
    degradation_rate_pct: float = 0.5


class ModuleBuildCreate(ModuleBuildBase):
    pass


class ModuleBuildResponse(ModuleBuildBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True