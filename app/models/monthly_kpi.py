from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class MonthlyKPI(Base):
    __tablename__ = "monthly_kpis"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(String(7), nullable=False)

    total_yield_kwh = Column(Float, nullable=True)
    pr_percentage = Column(Float, nullable=True)
    cuf_percentage = Column(Float, nullable=True)
    target_p50_kwh = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)
    irradiation_kwh_m2 = Column(Float, nullable=True)

    computed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="monthly_kpis")