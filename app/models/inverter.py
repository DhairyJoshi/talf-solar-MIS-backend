from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Inverter(Base):
    __tablename__ = "inverters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    module_build_id = Column(Integer, ForeignKey("module_builds.id", ondelete="SET NULL"), nullable=True)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    vendor_type = Column(String(50), nullable=False)

    encrypted_credentials = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="inverters")
    module_build = relationship("ModuleBuild", back_populates="inverters")
    breakdown_events = relationship("BreakdownEvent", back_populates="inverter", cascade="all, delete-orphan")