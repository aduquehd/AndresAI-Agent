import logfire
import requests

from config import settings


def get_geographic_data(ip_address: str) -> dict:
    """Get geographic information from IP address using ipapi.co (free tier)."""
    if (
        ip_address in ["unknown", "127.0.0.1", "::1"]
        or ip_address.startswith("192.168.")
        or ip_address.startswith("10.")
    ):
        return {"country": None, "region": None, "city": None}

    try:
        url = f"https://ipapi.co/{ip_address}/json/"
        if settings.ipapi_secret_key:
            url += f"?key={settings.ipapi_secret_key}"

        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country_code"),
                "region": data.get("region"),
                "city": data.get("city"),
            }
    except Exception as e:
        logfire.warn("Failed to get geographic data", ip=ip_address, error=str(e))

    return {"country": None, "region": None, "city": None}
