import httpx
import json
from typing import Dict, Any
from app.adapters.base import BaseInverterAdapter

ISOLAR_API_HOST = "https://gateway.isolarcloud.com.hk"


async def _get_sungrow_token(api_key: str, api_secret: str, client: httpx.AsyncClient) -> str:
    """
    Authenticates with Sungrow iSolarCloud to obtain a session token.
    Ref: Sungrow iSolarCloud Open API documentation.
    """
    payload = {
        "appkey": api_key,
        "user_password": api_secret,
        "login_type": "0",
        "is_agree_policy": "1"
    }
    resp = await client.post(
        f"{ISOLAR_API_HOST}/openapi/login",
        json=payload,
        headers={"Content-Type": "application/json", "x-access-key": api_key},
        timeout=10.0
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("result_data", {}).get("token", "")


class SungrowAdapter(BaseInverterAdapter):

    async def get_live_status(self, device_id: str, credentials: dict) -> Dict[str, Any]:
        api_key = credentials.get("api_key", "")
        api_secret = credentials.get("api_secret", "")

        try:
            async with httpx.AsyncClient() as client:
                token = await _get_sungrow_token(api_key, api_secret, client)
                resp = await client.post(
                    f"{ISOLAR_API_HOST}/openapi/getDeviceRealTimeData",
                    json={"device_sn": device_id},
                    headers={"token": token, "x-access-key": api_key},
                    timeout=10.0
                )
                resp.raise_for_status()
                data = resp.json().get("result_data", {})
                return {
                    "vendor": "Sungrow",
                    "device_id": device_id,
                    "power_output_kw": data.get("p_ac", 0) / 1000,  # Sungrow returns watts
                    "daily_yield_kwh": data.get("daily_yield_energy", 0),
                    "status": "ONLINE" if data.get("run_state") == 1 else "OFFLINE",
                }
        except httpx.HTTPStatusError as e:
            return {"vendor": "Sungrow", "device_id": device_id, "error": f"API error: {e.response.status_code}", "status": "ERROR"}
        except httpx.RequestError as e:
            return {"vendor": "Sungrow", "device_id": device_id, "error": f"Network error: {str(e)}", "status": "UNREACHABLE"}

    async def get_monthly_yield(self, device_id: str, month: str, credentials: dict) -> Dict[str, Any]:
        api_key = credentials.get("api_key", "")
        api_secret = credentials.get("api_secret", "")
        year, mon = month.split("-")

        try:
            async with httpx.AsyncClient() as client:
                token = await _get_sungrow_token(api_key, api_secret, client)
                resp = await client.post(
                    f"{ISOLAR_API_HOST}/openapi/queryDeviceHistoryDataList",
                    json={"device_sn": device_id, "start_time": f"{year}{mon}01", "end_time": f"{year}{mon}31", "data_type": "month"},
                    headers={"token": token, "x-access-key": api_key},
                    timeout=10.0
                )
                resp.raise_for_status()
                data = resp.json().get("result_data", {})
                total_yield = sum(r.get("yield_energy", 0) for r in data.get("list", []))
                return {
                    "vendor": "Sungrow",
                    "device_id": device_id,
                    "month": month,
                    "yield_kwh": total_yield,
                }
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            return {"vendor": "Sungrow", "device_id": device_id, "month": month, "yield_kwh": 0.0, "error": str(e)}