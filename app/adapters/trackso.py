import httpx
from typing import Dict, Any
from app.adapters.base import BaseInverterAdapter

TRACKSO_API_HOST = "https://api.trackso.in"


class TrackSOAdapter(BaseInverterAdapter):
    """
    Adapter for TrackSO IoT loggers.
    TrackSO uses a simple API key in the Authorization header.
    Ref: https://trackso.in/api-docs
    """

    async def get_live_status(self, device_id: str, credentials: dict) -> Dict[str, Any]:
        api_key = credentials.get("api_key", "")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{TRACKSO_API_HOST}/devices/{device_id}/live",
                    headers={"Authorization": f"Token {api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "vendor": "TrackSO",
                    "device_id": device_id,
                    "power_output_kw": data.get("power_kw", 0),
                    "daily_yield_kwh": data.get("energy_today_kwh", 0),
                    "status": data.get("status", "UNKNOWN").upper(),
                }
        except httpx.HTTPStatusError as e:
            return {"vendor": "TrackSO", "device_id": device_id, "error": f"API error: {e.response.status_code}", "status": "ERROR"}
        except httpx.RequestError as e:
            return {"vendor": "TrackSO", "device_id": device_id, "error": f"Network error: {str(e)}", "status": "UNREACHABLE"}

    async def get_monthly_yield(self, device_id: str, month: str, credentials: dict) -> Dict[str, Any]:
        """month format: YYYY-MM"""
        api_key = credentials.get("api_key", "")
        year, mon = month.split("-")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{TRACKSO_API_HOST}/devices/{device_id}/energy",
                    params={"year": year, "month": mon, "interval": "monthly"},
                    headers={"Authorization": f"Token {api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "vendor": "TrackSO",
                    "device_id": device_id,
                    "month": month,
                    "yield_kwh": data.get("energy_kwh", 0),
                }
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            return {"vendor": "TrackSO", "device_id": device_id, "month": month, "yield_kwh": 0.0, "error": str(e)}

    async def get_day_curve(self, device_id: str, date: str, credentials: dict) -> Dict[str, Any]:
        """date format: YYYY-MM-DD"""
        api_key = credentials.get("api_key", "")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # TrackSO might use an 'hourly' or 'timeline' endpoint for a single day
                resp = await client.get(
                    f"{TRACKSO_API_HOST}/devices/{device_id}/timeline",
                    params={"date": date},
                    headers={"Authorization": f"Token {api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
                curve = [{"timestamp": r.get("time"), "value": r.get("power_kw", 0)} for r in data.get("points", [])]
                return {
                    "vendor": "TrackSO",
                    "device_id": device_id,
                    "date": date,
                    "data_points": curve
                }
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            return {"vendor": "TrackSO", "device_id": device_id, "date": date, "data_points": [], "error": str(e)}