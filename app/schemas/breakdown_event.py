from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BreakdownEventBase(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    loss_kwh: Optional[float] = None


class BreakdownEventCreate(BreakdownEventBase):
    pass


class BreakdownEventUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    loss_kwh: Optional[float] = None



class BreakdownEventResponse(BreakdownEventBase):
    id: int
    inverter_id: int
    created_at: datetime

    class Config:
        from_attributes = True