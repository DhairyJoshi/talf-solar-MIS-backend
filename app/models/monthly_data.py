from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class MonthlyData(Base):
    __tablename__ = "monthly_data"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(String(7), nullable=False)
    energy_kwh = Column(Float, nullable=False, default=0.0)
    irradiation_kwh_m2 = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)
    tariff_rate = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="monthly_data")