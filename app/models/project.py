from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    capacity_kw = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    inverters = relationship("Inverter", back_populates="project", cascade="all, delete-orphan")
    monthly_data = relationship("MonthlyData", back_populates="project", cascade="all, delete-orphan")
    monthly_kpis = relationship("MonthlyKPI", back_populates="project", cascade="all, delete-orphan")