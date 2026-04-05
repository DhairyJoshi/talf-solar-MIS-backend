from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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


class InverterResponse(InverterBase):
    id: int
    project_id: int
    module_build_id: Optional[int] = None

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

    class Config:
        from_attributes = True