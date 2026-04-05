from app.adapters.base import BaseInverterAdapter
from app.adapters.solis import SolisAdapter
from app.adapters.sungrow import SungrowAdapter
from app.adapters.trackso import TrackSOAdapter


def get_inverter_adapter(vendor_name: str) -> BaseInverterAdapter:
    normalized_name = vendor_name.strip().upper()
    if normalized_name == "SOLIS" or normalized_name == "SOLISCLOUD":
        return SolisAdapter()
    elif normalized_name == "SUNGROW":
        return SungrowAdapter()
    elif normalized_name == "TRACKSO":
        return TrackSOAdapter()
    raise ValueError(f"Provider '{vendor_name}' is not supported. Supported: SOLIS, SOLISCLOUD, SUNGROW, TRACKSO.")