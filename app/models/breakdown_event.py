from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class BreakdownEvent(Base):
    __tablename__ = "breakdown_events"

    id = Column(Integer, primary_key=True, index=True)
    inverter_id = Column(Integer, ForeignKey("inverters.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    loss_kwh = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inverter = relationship("Inverter", back_populates="breakdown_events")