from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user, require_admin, require_operations
from app.models.breakdown_event import BreakdownEvent
from app.models.inverter import Inverter
from app.models.user import User
from app.schemas.breakdown_event import BreakdownEventCreate, BreakdownEventResponse

router = APIRouter()


@router.post("/{inverter_id}/breakdown-events", response_model=BreakdownEventResponse)
async def create_breakdown_event(
    inverter_id: int,
    event: BreakdownEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operations)
):
    inverter = await db.get(Inverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")

    db_event = BreakdownEvent(inverter_id=inverter_id, **event.model_dump())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event


@router.get("/{inverter_id}/breakdown-events", response_model=List[BreakdownEventResponse])
async def list_breakdown_events(
    inverter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inverter = await db.get(Inverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")

    result = await db.execute(
        select(BreakdownEvent)
        .where(BreakdownEvent.inverter_id == inverter_id)
        .order_by(BreakdownEvent.start_date.desc())
    )
    return result.scalars().all()


@router.delete("/breakdown-events/{event_id}", status_code=204)
async def delete_breakdown_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    event = await db.get(BreakdownEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Breakdown event not found")
    await db.delete(event)
    await db.commit()