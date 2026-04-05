from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
import json
from app.core.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models.project import Project
from app.models.inverter import Inverter
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, InverterCreate, InverterUpdate, InverterResponse
from app.core.security import encrypt_data
from app.worker.tasks import sync_nightly_yield

router = APIRouter()


async def _get_project_with_inverters(project_id: int, db: AsyncSession) -> Project:
    """Helper to eagerly load project with its inverters, monthly data, and kpis."""
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.inverters),
            selectinload(Project.monthly_data),
            selectinload(Project.monthly_kpis)
        )
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_project = Project(**project.model_dump())
    db.add(db_project)
    await db.commit()
    return await _get_project_with_inverters(db_project.id, db)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Project).options(
        selectinload(Project.inverters),
        selectinload(Project.monthly_data),
        selectinload(Project.monthly_kpis)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await _get_project_with_inverters(project_id, db)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_project = await _get_project_with_inverters(project_id, db)
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    await db.commit()
    return await _get_project_with_inverters(project_id, db)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_project = await db.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(db_project)
    await db.commit()


@router.post("/{project_id}/inverters", response_model=InverterResponse)
async def add_inverter(
    project_id: int,
    inverter: InverterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_project = await db.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    credentials = {"api_key": inverter.api_key, "api_secret": inverter.api_secret}
    encrypted_creds = encrypt_data(json.dumps(credentials))

    db_inverter = Inverter(
        project_id=project_id,
        serial_number=inverter.serial_number,
        vendor_type=inverter.vendor_type,
        module_build_id=inverter.module_build_id,
        encrypted_credentials=encrypted_creds
    )
    db.add(db_inverter)
    await db.commit()
    await db.refresh(db_inverter)
    return db_inverter


@router.post("/{project_id}/sync")
def trigger_sync(project_id: int, current_user: User = Depends(require_admin)):
    task = sync_nightly_yield.delay(project_id)
    return {"message": "Sync queued.", "task_id": task.id}