import asyncio
from datetime import datetime
from app.worker.celery_app import celery_app


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_project(project_id: int):
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    from app.core.database import async_session_maker
    from app.core.security import decrypt_data
    from app.adapters.factory import get_inverter_adapter
    from app.models.project import Project
    from app.models.monthly_data import MonthlyData
    from app.services.calculation import compute_and_store_kpis
    import json

    current_month = datetime.now().strftime("%Y-%m")

    async with async_session_maker() as db:
        result = await db.execute(
            select(Project).where(Project.id == project_id).options(selectinload(Project.inverters))
        )
        project = result.scalar_one_or_none()
        if not project:
            return {"error": f"Project {project_id} not found"}

        total_yield = 0.0
        for inverter in project.inverters:
            try:
                credentials = json.loads(decrypt_data(inverter.encrypted_credentials))
                adapter = get_inverter_adapter(inverter.vendor_type)
                yield_data = await adapter.get_monthly_yield(inverter.serial_number, current_month, credentials)
                inverter_yield = yield_data.get("yield_kwh", 0.0)
                total_yield += inverter_yield
            except Exception as e:
                print(f"[Celery] Failed to sync inverter {inverter.serial_number}: {e}")
                continue

        existing = await db.execute(
            select(MonthlyData).where(
                MonthlyData.project_id == project_id,
                MonthlyData.month == current_month
            )
        )
        monthly_record = existing.scalar_one_or_none()

        if monthly_record:
            monthly_record.energy_kwh = total_yield
        else:
            monthly_record = MonthlyData(
                project_id=project_id,
                month=current_month,
                energy_kwh=total_yield,
            )
            db.add(monthly_record)

        await db.commit()
        await db.refresh(monthly_record)

        all_monthly = await db.execute(
            select(MonthlyData).where(MonthlyData.project_id == project_id)
        )
        await compute_and_store_kpis(project, all_monthly.scalars().all(), db)

        return {
            "project_id": project_id,
            "month": current_month,
            "total_yield_kwh": total_yield,
            "inverters_synced": len(project.inverters),
        }


@celery_app.task(name="sync_nightly_yield", bind=True, max_retries=3, default_retry_delay=300)
def sync_nightly_yield(self, project_id: int):
    try:
        result = _run_async(_sync_project(project_id))
        print(f"[Celery] Sync complete: {result}")
        return result
    except Exception as exc:
        print(f"[Celery] Sync failed for project {project_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(name="recalculate_project_kpis")
def recalculate_project_kpis(project_id: int):

    async def _recalc():
        from sqlalchemy.future import select
        from app.core.database import async_session_maker
        from app.models.project import Project
        from app.models.monthly_data import MonthlyData
        from app.services.calculation import compute_and_store_kpis

        async with async_session_maker() as db:
            project = await db.get(Project, project_id)
            if not project:
                return {"error": f"Project {project_id} not found"}
            result = await db.execute(select(MonthlyData).where(MonthlyData.project_id == project_id))
            monthly_data = result.scalars().all()
            count = await compute_and_store_kpis(project, monthly_data, db)
            return {"project_id": project_id, "months_updated": count}

    return _run_async(_recalc())