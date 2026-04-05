from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.inverter import Inverter
from app.models.user import User
from app.api.dependencies import get_current_user
from app.adapters.factory import get_inverter_adapter
from app.core.security import decrypt_data
import json

router = APIRouter()

@router.get("/inverters/{inverter_id}/live-status")
async def fetch_proxy_data(inverter_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    inverter = await db.get(Inverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")
        
    try:
        decrypted_str = decrypt_data(inverter.encrypted_credentials)
        credentials = json.loads(decrypted_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Decryption failure or invalid credential format")
    
    try:
        adapter = get_inverter_adapter(inverter.vendor_type)
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
         
    live_data = await adapter.get_live_status(inverter.serial_number, credentials)
    
    return live_data

@router.get("/inverters/{inverter_id}/day-curve")
async def fetch_day_curve(inverter_id: int, date: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    inverter = await db.get(Inverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail="Inverter not found")
        
    try:
        decrypted_str = decrypt_data(inverter.encrypted_credentials)
        credentials = json.loads(decrypted_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Decryption failure or invalid credential format")
    
    try:
        adapter = get_inverter_adapter(inverter.vendor_type)
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
         
    curve_data = await adapter.get_day_curve(inverter.serial_number, date, credentials)
    
    return curve_data