from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.monthly_data import MonthlyDataResponse
from app.schemas.monthly_kpi import MonthlyKPIResponse


class InverterBase(BaseModel):
    serial_number: str
    vendor_type: str


class InverterCreate(InverterBase):
    api_key: str
    api_secret: str
    module_build_id: Optional[int] = None


class InverterUpdate(BaseModel):
    serial_number: Optional[str] = None
    vendor_type: Optional[str] = None
    module_build_id: Optional[int] = None


class LiveStatusResponse(BaseModel):
    vendor: str
    device_id: str
    power_output_kw: float
    daily_yield_kwh: float
    status: str


class InverterResponse(InverterBase):
    id: int
    project_id: int
    module_build_id: Optional[int] = None
    live_data: Optional[LiveStatusResponse] = None

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    location: Optional[str] = None
    capacity_kw: float


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity_kw: Optional[float] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    inverters: List[InverterResponse] = []
    monthly_data: List[MonthlyDataResponse] = []
    monthly_kpis: List[MonthlyKPIResponse] = []

    class Config:
        from_attributes = True