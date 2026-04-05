from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


def calculate_pr(yield_kwh: float, irradiation_kwh_m2: float, capacity_kw: float, panel_efficiency: float = 0.16) -> Optional[float]:
    if irradiation_kwh_m2 <= 0 or capacity_kw <= 0:
        return None
    theoretical_yield = irradiation_kwh_m2 * capacity_kw
    return round((yield_kwh / theoretical_yield) * 100, 2)


def calculate_cuf(yield_kwh: float, capacity_kw: float, days_in_month: int = 30) -> Optional[float]:
    if capacity_kw <= 0:
        return None
    total_hours = days_in_month * 24
    return round((yield_kwh / (capacity_kw * total_hours)) * 100, 2)


def calculate_target_p50(irradiation_kwh_m2: float, capacity_kw: float, efficiency: float = 0.80) -> Optional[float]:
    if irradiation_kwh_m2 is None or irradiation_kwh_m2 <= 0 or capacity_kw <= 0:
        return None
    return round(irradiation_kwh_m2 * capacity_kw * efficiency, 2)


def calculate_revenue(yield_kwh: float, tariff_rate: Optional[float]) -> Optional[float]:
    if tariff_rate is None or tariff_rate <= 0:
        return None
    return round(yield_kwh * tariff_rate, 2)


import calendar
from datetime import datetime


async def compute_and_store_kpis(project, monthly_data_list: list, db: AsyncSession) -> int:
    from app.models.monthly_kpi import MonthlyKPI

    count = 0
    for data in monthly_data_list:
        year, mon = int(data.month[:4]), int(data.month[5:7])
        days_in_month = calendar.monthrange(year, mon)[1]

        pr = calculate_pr(data.energy_kwh, data.irradiation_kwh_m2, project.capacity_kw) if data.irradiation_kwh_m2 else None
        cuf = calculate_cuf(data.energy_kwh, project.capacity_kw, days_in_month)
        target_p50 = calculate_target_p50(data.irradiation_kwh_m2, project.capacity_kw) if data.irradiation_kwh_m2 else None
        revenue = data.revenue if data.revenue is not None else calculate_revenue(data.energy_kwh, data.tariff_rate)

        existing = await db.execute(
            select(MonthlyKPI).where(
                MonthlyKPI.project_id == project.id,
                MonthlyKPI.month == data.month
            )
        )
        kpi = existing.scalar_one_or_none()

        if kpi:
            kpi.total_yield_kwh = data.energy_kwh
            kpi.pr_percentage = pr
            kpi.cuf_percentage = cuf
            kpi.target_p50_kwh = target_p50
            kpi.revenue = revenue
            kpi.irradiation_kwh_m2 = data.irradiation_kwh_m2
        else:
            kpi = MonthlyKPI(
                project_id=project.id,
                month=data.month,
                total_yield_kwh=data.energy_kwh,
                pr_percentage=pr,
                cuf_percentage=cuf,
                target_p50_kwh=target_p50,
                revenue=revenue,
                irradiation_kwh_m2=data.irradiation_kwh_m2,
            )
            db.add(kpi)

        count += 1

    await db.commit()
    return count