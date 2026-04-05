from fastapi import APIRouter
from app.api.v1 import auth, projects, proxy, inverters, module_builds, monthly_data, breakdown_events, kpis

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(inverters.router, prefix="/inverters", tags=["Inverters"])
api_router.include_router(module_builds.router, prefix="/module-builds", tags=["Module Builds"])
api_router.include_router(monthly_data.router, prefix="/projects", tags=["Monthly Data"])
api_router.include_router(breakdown_events.router, prefix="/inverters", tags=["Breakdown Events"])
api_router.include_router(kpis.router, prefix="/projects", tags=["KPIs"])
api_router.include_router(proxy.router, prefix="/proxy", tags=["Proxy Inverter Integration"])