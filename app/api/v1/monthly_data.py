import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user, require_operations
from app.models.monthly_data import MonthlyData
from app.models.project import Project
from app.models.user import User
from app.schemas.monthly_data import MonthlyDataCreate, MonthlyDataResponse

router = APIRouter()


@router.post("/{project_id}/monthly-data", response_model=MonthlyDataResponse)
async def create_monthly_data(
    project_id: int,
    data: MonthlyDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operations)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_data = MonthlyData(project_id=project_id, **data.model_dump())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data


@router.post("/{project_id}/monthly-data/csv", summary="Bulk upload monthly data via CSV")
async def upload_monthly_data_csv(
    project_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operations)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    reader = csv.DictReader(io.StringIO(contents.decode("utf-8")))

    required_columns = {"month", "energy_kwh"}
    if not required_columns.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            status_code=422,
            detail=f"CSV must contain columns: {required_columns}. Found: {reader.fieldnames}"
        )

    records_created = 0
    errors = []
    for i, row in enumerate(reader, start=2):
        try:
            entry = MonthlyData(
                project_id=project_id,
                month=row["month"].strip(),
                energy_kwh=float(row["energy_kwh"]),
                irradiation_kwh_m2=float(row["irradiation_kwh_m2"]) if row.get("irradiation_kwh_m2") else None,
                revenue=float(row["revenue"]) if row.get("revenue") else None,
                tariff_rate=float(row["tariff_rate"]) if row.get("tariff_rate") else None,
            )
            db.add(entry)
            records_created += 1
        except (ValueError, KeyError) as e:
            errors.append({"row": i, "error": str(e)})

    await db.commit()
    return {
        "message": f"CSV processed. {records_created} records created.",
        "errors": errors
    }


@router.get("/{project_id}/monthly-data", response_model=List[MonthlyDataResponse])
async def list_monthly_data(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(MonthlyData).where(MonthlyData.project_id == project_id).order_by(MonthlyData.month)
    )
    return result.scalars().all()