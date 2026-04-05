from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user, require_operations
from app.models.monthly_kpi import MonthlyKPI
from app.models.monthly_data import MonthlyData
from app.models.project import Project
from app.models.user import User
from app.schemas.monthly_kpi import MonthlyKPIResponse
from app.services.calculation import compute_and_store_kpis

router = APIRouter()


@router.get("/{project_id}/kpis", response_model=List[MonthlyKPIResponse])
async def get_project_kpis(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(MonthlyKPI)
        .where(MonthlyKPI.project_id == project_id)
        .order_by(MonthlyKPI.month)
    )
    return result.scalars().all()


@router.post("/{project_id}/kpis/recalculate")
async def recalculate_kpis(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operations)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    monthly_data_result = await db.execute(
        select(MonthlyData).where(MonthlyData.project_id == project_id)
    )
    monthly_data = monthly_data_result.scalars().all()

    if not monthly_data:
        raise HTTPException(status_code=400, detail="No monthly data found for this project. Upload data first.")

    computed = await compute_and_store_kpis(project, monthly_data, db)
    return {"message": f"KPIs recalculated. {computed} months updated.", "project_id": project_id}