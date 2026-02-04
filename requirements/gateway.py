"""
API Gateway Client for Python_Panel
Handles authentication and requests to the centralized API gateway.
"""
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class GatewayClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    def _get_token(self) -> str:
        """Get or refresh JWT token."""
        # Check if we have a valid token
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token

        # Login to get new token
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": self.username, "password": self.password},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        self.token = data["access_token"]
        # Token expires in 1 hour, refresh 5 minutes early
        self.token_expiry = datetime.now() + timedelta(minutes=55)

        return self.token

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make authenticated request to gateway."""
        token = self._get_token()
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {token}'

        response = requests.request(
            method,
            f"{self.base_url}{endpoint}",
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """GET request to gateway."""
        return self._request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """POST request to gateway."""
        return self._request('POST', endpoint, **kwargs)

    # Convenience methods for specific APIs

    def get_hourly_forecast(self, lat: float, lon: float, units: str = "metric") -> Dict[Any, Any]:
        """Get hourly weather forecast (48 hours)."""
        return self.get(f"/weather/forecast/hourly", params={"lat": lat, "lon": lon, "units": units})

    def get_daily_forecast(self, lat: float, lon: float, days: int = 7, units: str = "metric") -> Dict[Any, Any]:
        """Get daily weather forecast."""
        return self.get(f"/weather/forecast/daily", params={"lat": lat, "lon": lon, "cnt": days, "units": units})

    def geocode(self, city: str) -> Dict[Any, Any]:
        """Get coordinates for a city name."""
        return self.get(f"/geo/geocode", params={"text": city})

    def get_location_from_ip(self, ip: Optional[str] = None) -> Dict[Any, Any]:
        """Get location information from IP address."""
        params = {"ip": ip} if ip else {}
        return self.get(f"/geo/ip", params=params)

    def send_email(self, to: list, subject: str, html: str, from_email: Optional[str] = None) -> Dict[Any, Any]:
        """Send an email via Resend API."""
        payload = {
            "to": to if isinstance(to, list) else [to],
            "subject": subject,
            "html": html
        }
        if from_email:
            payload["from_email"] = from_email
        return self.post("/email/send", json=payload)

    # Software & Hardware health monitoring

    def list_software(self) -> Dict[Any, Any]:
        """List all registered software with health status."""
        return self.get("/software")

    def get_software(self, name: str) -> Dict[Any, Any]:
        """Get health status for one software (includes stale flag)."""
        return self.get(f"/software/{name}")

    def push_software_heartbeat(self, name: str, health: str, details: Optional[Dict] = None) -> Dict[Any, Any]:
        """Push a heartbeat for a software. health: 'ok' | 'warning' | 'error'."""
        payload: Dict[str, Any] = {"health": health}
        if details is not None:
            payload["details"] = details
        return self.post(f"/software/{name}/heartbeat", json=payload)

    def list_hardware(self) -> Dict[Any, Any]:
        """List all registered hardware with health + config."""
        return self.get("/hardware")

    def get_hardware(self, name: str) -> Dict[Any, Any]:
        """Get health + config for one hardware device (includes stale flag)."""
        return self.get(f"/hardware/{name}")

    def push_hardware_heartbeat(self, name: str, health: str, config: Optional[Dict] = None, details: Optional[Dict] = None) -> Dict[Any, Any]:
        """Push a heartbeat for a hardware device. health: 'ok' | 'warning' | 'error'."""
        payload: Dict[str, Any] = {"health": health}
        if config is not None:
            payload["config"] = config
        if details is not None:
            payload["details"] = details
        return self.post(f"/hardware/{name}/heartbeat", json=payload)
