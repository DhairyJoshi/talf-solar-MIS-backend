import hashlib
import hmac
import base64
import json
import time
import httpx
from typing import Dict, Any
from app.adapters.base import BaseInverterAdapter

SOLIS_API_HOST = "https://www.soliscloud.com:13333"


def _build_solis_auth_header(method: str, path: str, api_key: str, api_secret: str, body: str) -> dict:
    """
    Generates the HMAC-SHA1 Authorization header required by the Solis v2 API.
    Ref: https://oss.soliscloud.com/doc/SolisCloud%20Platform%20API%20Vendor%20access%20document%20V2.0.pdf
    """
    content_md5 = base64.b64encode(
        hashlib.md5(body.encode("utf-8")).digest()
    ).decode("utf-8")
    content_type = "application/json"
    date_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

    string_to_sign = f"{method}\n{content_md5}\n{content_type}\n{date_str}\n{path}"
    hmac_sig = base64.b64encode(
        hmac.new(api_secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")

    return {
        "Content-Type": content_type,
        "Content-MD5": content_md5,
        "Date": date_str,
        "Authorization": f"API {api_key}:{hmac_sig}",
    }


class SolisAdapter(BaseInverterAdapter):

    async def get_live_status(self, device_id: str, credentials: dict) -> Dict[str, Any]:
        api_key = credentials.get("api_key", "")
        api_secret = credentials.get("api_secret", "")
        path = "/v1/api/inverterDetail"
        body = json.dumps({"sn": device_id})

        try:
            headers = _build_solis_auth_header("POST", path, api_key, api_secret, body)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(f"{SOLIS_API_HOST}{path}", content=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                inverter_data = data.get("data", {})
                return {
                    "vendor": "Solis",
                    "device_id": device_id,
                    "power_output_kw": inverter_data.get("pac", 0),
                    "daily_yield_kwh": inverter_data.get("eToday", 0),
                    "status": "ONLINE" if inverter_data.get("state") == 1 else "OFFLINE",
                }
        except httpx.HTTPStatusError as e:
            return {"vendor": "Solis", "device_id": device_id, "error": f"API error: {e.response.status_code}", "status": "ERROR"}
        except httpx.RequestError as e:
            return {"vendor": "Solis", "device_id": device_id, "error": f"Network error: {str(e)}", "status": "UNREACHABLE"}

    async def get_monthly_yield(self, device_id: str, month: str, credentials: dict) -> Dict[str, Any]:
        """month format: YYYY-MM"""
        api_key = credentials.get("api_key", "")
        api_secret = credentials.get("api_secret", "")
        year, mon = month.split("-")
        path = "/v1/api/inverterMonth"
        body = json.dumps({"sn": device_id, "month": f"{year}-{mon}"})

        try:
            headers = _build_solis_auth_header("POST", path, api_key, api_secret, body)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(f"{SOLIS_API_HOST}{path}", content=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                records = data.get("data", {}).get("records", [])
                total_yield = sum(r.get("energy", 0) for r in records)
                return {
                    "vendor": "Solis",
                    "device_id": device_id,
                    "month": month,
                    "yield_kwh": total_yield,
                }
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            return {"vendor": "Solis", "device_id": device_id, "month": month, "yield_kwh": 0.0, "error": str(e)}

    async def get_day_curve(self, device_id: str, date: str, credentials: dict) -> Dict[str, Any]:
        """date format: YYYY-MM-DD"""
        api_key = credentials.get("api_key", "")
        api_secret = credentials.get("api_secret", "")
        path = "/v1/api/inverterDay"
        body = json.dumps({"sn": device_id, "time": date})

        try:
            headers = _build_solis_auth_header("POST", path, api_key, api_secret, body)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(f"{SOLIS_API_HOST}{path}", content=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                # Solis day curve usually returns power points throughout the day
                records = data.get("data", [])
                curve = [{"timestamp": r.get("timeStr"), "value": r.get("pac", 0)} for r in records]
                return {
                    "vendor": "Solis",
                    "device_id": device_id,
                    "date": date,
                    "data_points": curve
                }
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            return {"vendor": "Solis", "device_id": device_id, "date": date, "data_points": [], "error": str(e)}