from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class ModuleBuild(Base):
    __tablename__ = "module_builds"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    rated_power_wp = Column(Float, nullable=False)
    degradation_rate_pct = Column(Float, default=0.5, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inverters = relationship("Inverter", back_populates="module_build")