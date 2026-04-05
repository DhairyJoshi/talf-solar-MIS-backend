from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseInverterAdapter(ABC):
    @abstractmethod
    async def get_live_status(self, device_id: str, credentials: dict) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_monthly_yield(self, device_id: str, month: str, credentials: dict) -> Dict[str, Any]:
        pass