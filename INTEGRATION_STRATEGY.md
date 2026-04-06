# Integration Strategy: Adding New Inverter Vendors

This document outlines the process for integrating a new third-party inverter API (e.g., Huawei FusionSolar) into the Talf Solar MIS backend without modifying the core business logic.

## 1. Overview of the Adapter Pattern

The system uses the **Adapter Design Pattern** to standardize communication with disparate vendor APIs. Each vendor has a dedicated adapter class that translates standard system requests (e.g., Get Live Status) into vendor-specific API calls and formats.

This approach ensures that the core application remains decoupled from external API changes and allows for rapid scaling to new hardware providers.

## 2. Implementation Steps

To add a new vendor like **Huawei**, follow these four steps:

### Step 1: Create the Adapter Class
Create a new file `app/adapters/huawei.py` and implement the `BaseInverterAdapter` interface.

```python
from app.adapters.base import BaseInverterAdapter
from typing import Dict, Any

class HuaweiAdapter(BaseInverterAdapter):
    async def get_live_status(self, device_id: str, credentials: dict) -> Dict[str, Any]:
        # Implementation for Huawei FusionSolar API
        # 1. Authenticate using credentials (API Key/Secret)
        # 2. Fetch real-time data for device_id
        # 3. Return standardized dictionary: {"power_output_kw": ..., "status": ...}
        pass

    async def get_monthly_yield(self, device_id: str, month: str, credentials: dict) -> Dict[str, Any]:
        # Fetch accumulated energy for the specified month
        pass

    async def get_day_curve(self, device_id: str, date: str, credentials: dict) -> Dict[str, Any]:
        # Fetch 5-minute interval power data for the specified date
        pass
```

### Step 2: Register the Adapter in the Factory
Update `app/adapters/factory.py` to include the new provider.

```python
from app.adapters.huawei import HuaweiAdapter

def get_inverter_adapter(vendor_name: str) -> BaseInverterAdapter:
    normalized_name = vendor_name.strip().upper()
    # ... existing logic ...
    if normalized_name == "HUAWEI":
        return HuaweiAdapter()
```

### Step 3: Update API Validation
Add the new vendor type to the Pydantic schemas in `app/schemas/project.py` or wherever vendor validation is performed. This ensures the frontend and API level recognize "HUAWEI" as a valid input.

### Step 4: Background Sync Integration
The Celery worker in `app/worker/tasks.py` automatically uses the `get_inverter_adapter` factory. Once the adapter and factory are updated, the nightly synchronization job will support Huawei inverters without further changes.

## 3. Huawei Integration Example (Mock Implementation)

Below is an illustrative example of how the `get_live_status` method might be implemented for Huawei:

```python
import httpx
from app.adapters.base import BaseInverterAdapter

class HuaweiAdapter(BaseInverterAdapter):
    async def get_live_status(self, device_id: str, credentials: dict):
        url = "https://intl.fusionsolar.huawei.com/thirdData/getDevRealKpi"
        headers = {"X-HW-ID": credentials["api_key"], "X-HW-KEY": credentials["api_secret"]}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"devIds": device_id}, headers=headers)
            data = response.json()
            
            # Standardizing vendor-specific response to system-wide format
            return {
                "vendor": "HUAWEI",
                "power_output_kw": data["data"][0]["activePower"],
                "status": "ONLINE" if data["data"][0]["status"] == 1 else "OFFLINE"
            }
```

## 4. Benefits of this Strategy

- **Core Stability**: Adding Huawei does not require changing the KPI Calculation Engine or User Management logic.
- **Security**: The new adapter automatically benefits from the AES-256 credential decryption handled in the `Proxy` and `Task` layers.
- **Robustness**: Error handling implemented in the base adapter or factory ensures that one vendor's API failure does not crash the entire sync process.
