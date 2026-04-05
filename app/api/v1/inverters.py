from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from app.core.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models.inverter import Inverter
from app.models.user import User
from app.schemas.project import InverterResponse, InverterUpdate

router = APIRouter()


@router.get("/{inverter_id}", response_model=InverterResponse)
async def get_inverter(
    inverter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inverter = await db.get(Inverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")
    return inverter


@router.put("/{inverter_id}", response_model=InverterResponse)
async def update_inverter(
    inverter_id: int,
    inverter_update: InverterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    inverter = await db.get(Inverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")
    update_data = inverter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inverter, field, value)
    await db.commit()
    await db.refresh(inverter)
    return inverter


@router.delete("/{inverter_id}", status_code=204)
async def delete_inverter(
    inverter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    inverter = await db.get(Inverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")
    await db.delete(inverter)
    await db.commit()