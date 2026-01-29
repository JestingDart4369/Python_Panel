from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta, timezone
import asyncio
from pathlib import Path
from typing import Optional
import sys
import os

import requests
from winrt.windows.devices.geolocation import Geolocator

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from requirements.gateway import GatewayClient
from requirements import apikey


class LocationError(RuntimeError):
    pass


@dataclass
class LocationResult:
    label: str
    coords: tuple[float, float]  # (lat, lon)


class LocationService:
    def __init__(
        self,
        *,
        use_winrt: bool,
        api_key_get_city: str,
        api_key_geo: str,
        ipregistry_url: str = "",
    ):
        self.use_winrt = use_winrt
        # Initialize gateway client
        self.gateway = GatewayClient(
            base_url=apikey.GATEWAY_URL,
            username=apikey.GATEWAY_USERNAME,
            password=apikey.GATEWAY_PASSWORD
        )

        # state you can read from main/ui
        self.label: str = "—"
        self.coords: tuple[float, float] = (0.0, 0.0)

    async def _winrt_get_lat_lon(self) -> tuple[float, float]:
        geo = Geolocator()
        pos = await geo.get_geoposition_async()
        point = pos.coordinate.point.position
        return float(point.latitude), float(point.longitude)

    def _detect_city_from_ip(self) -> str:
        try:
            data = self.gateway.get_location_from_ip()
            city = data.get("location", {}).get("city")
            if not city:
                raise LocationError("IPRegistry response did not contain a city.")
            return city
        except Exception as e:
            raise LocationError(f"Unable to retrieve city information from IPRegistry: {e}")

    def _geocode_city(self, city_name: str) -> tuple[float, float]:
        try:
            data = self.gateway.geocode(city_name)
            features = data.get("features") or []
            if not features:
                raise LocationError(f"Geoapify returned no results for city '{city_name}'.")

            props = features[0].get("properties", {})
            lat = props.get("lat")
            lon = props.get("lon")
            if lat is None or lon is None:
                raise LocationError("Geoapify response missing lat/lon.")

            return float(lat), float(lon)
        except Exception as e:
            raise LocationError(f"Unable to retrieve coordinates from Geoapify: {e}")

    def _fallback_ip_city_geo(self) -> LocationResult:
        city = self._detect_city_from_ip()
        lat, lon = self._geocode_city(city)
        return LocationResult(label=city, coords=(lat, lon))

    def get_coordinates(self) -> LocationResult:
        """
        Sync method that returns LocationResult.
        - If use_winrt is True, try WinRT first (if we can).
        - Otherwise fallback to IP → City → Geoapify.
        """
        if not self.use_winrt:
            return self._fallback_ip_city_geo()

        # If an event loop is already running, we cannot call asyncio.run().
        # In that case we fall back (simple + safe).
        try:
            asyncio.get_running_loop()
            # loop is running → avoid asyncio.run() here
            return self._fallback_ip_city_geo()
        except RuntimeError:
            pass  # no running loop, safe to use asyncio.run()

        try:
            lat, lon = asyncio.run(self._winrt_get_lat_lon())
            return LocationResult(label="Current Location", coords=(lat, lon))
        except Exception:
            return self._fallback_ip_city_geo()

    def update(self) -> None:
        result = self.get_coordinates()
        self.label = result.label
        self.coords = result.coords