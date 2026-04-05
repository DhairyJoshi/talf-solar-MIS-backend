from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models.module_build import ModuleBuild
from app.models.user import User
from app.schemas.module_build import ModuleBuildCreate, ModuleBuildResponse

router = APIRouter()


@router.post("/", response_model=ModuleBuildResponse)
async def create_module_build(
    module: ModuleBuildCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_module = ModuleBuild(**module.model_dump())
    db.add(db_module)
    await db.commit()
    await db.refresh(db_module)
    return db_module


@router.get("/", response_model=List[ModuleBuildResponse])
async def list_module_builds(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(ModuleBuild))
    return result.scalars().all()


@router.get("/{module_id}", response_model=ModuleBuildResponse)
async def get_module_build(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    module = await db.get(ModuleBuild, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module build not found")
    return module