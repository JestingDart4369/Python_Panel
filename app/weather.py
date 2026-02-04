from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import requests
from rich.table import Table

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from requirements.gateway import GatewayClient
from requirements import config

WEATHER_ICONS = {
    "01d": "☀️", "02d": "⛅", "03d": "☁️", "04d": "☁️☁️", "09d": "🌧️",
    "10d": "🌦️", "11d": "🌩️", "13d": "🌨️", "50d": "🌫️",
    "01n": "🌙", "02n": "🌙☁️", "03n": "☁️", "04n": "☁️☁️", "09n": "🌧️",
    "10n": "🌙🌧️", "11n": "🌩️", "13n": "🌨️", "50n": "🌫️",
}


class WeatherError(RuntimeError):
    pass


@dataclass
class WeatherResult:
    hourly_table: Table
    weekly_table: Table
    city: str
    country: str


class WeatherService:
    def __init__(self, units: str):
        self.gateway = GatewayClient(
            base_url=config.GATEWAY_URL,
            username=config.GATEWAY_USERNAME,
            password=config.GATEWAY_PASSWORD
        )
        self.units = units  # "metric" or "imperial"

        self.temp_unit = "°C" if units == "metric" else "°F"
        self.wind_unit = "m/s" if units == "metric" else "mph"

        # state you can read from main/ui
        self.city = "—"
        self.country = "—"
        self.hourly_table = Table()
        self.weekly_table = Table()

    def fetch_hourly(self, lat: float, lon: float, rows: int) -> tuple[Table, str, str]:
        try:
            data = self.gateway.get_hourly_forecast(lat, lon, self.units)
        except Exception as e:
            raise WeatherError(f"API Error: Unable to retrieve hourly forecast: {e}")

        city = data["city"]["name"]
        country = data["city"]["country"]

        table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
        table.add_column("Time", width=5, no_wrap=True,style="app.weather.data")
        table.add_column("Weather", width=18, overflow="ellipsis",style="app.weather.data")
        table.add_column("Data", width=18, justify="right", no_wrap=True, overflow="ellipsis",style="app.weather.data")

        items = data.get("list", [])
        for i in range(min(rows, len(items))):
            icon_code = items[i]["weather"][0]["icon"]
            icon = WEATHER_ICONS.get(icon_code, "")
            desc = items[i]["weather"][0]["description"]

            temp = items[i]["main"]["temp"]
            wind = items[i]["wind"]["speed"]
            gust = items[i]["wind"].get("gust", None)

            unix_time = items[i]["dt"]
            tz_offset = data["city"]["timezone"]
            local_time = datetime.fromtimestamp(unix_time, tz=timezone(timedelta(seconds=tz_offset)))
            hhmm = local_time.strftime("%H:%M")

            gust_part = f" {gust:.1f}{self.wind_unit}" if isinstance(gust, (int, float)) else ""
            table.add_row(
                hhmm,
                f"{icon} {desc}",
                f"{temp:.1f}{self.temp_unit} {wind:.1f}{self.wind_unit}{gust_part}",
            )

        return table, city, country

    def fetch_weekly(self, lat: float, lon: float, rows: int) -> tuple[Table, str, str]:
        try:
            data = self.gateway.get_daily_forecast(lat, lon, days=rows, units=self.units)
        except Exception as e:
            raise WeatherError(f"API Error: Unable to retrieve daily forecast: {e}")

        city = data["city"]["name"]
        country = data["city"]["country"]

        table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
        table.add_column("Date", width=6, no_wrap=True,style="app.weather.data")
        table.add_column("Weather", width=18, overflow="ellipsis",style="app.weather.data")
        table.add_column("Data", width=18, justify="right", no_wrap=True, overflow="ellipsis",style="app.weather.data")

        items = data.get("list", [])
        for i in range(min(rows, len(items))):
            icon_code = items[i]["weather"][0]["icon"]
            icon = WEATHER_ICONS.get(icon_code, "")
            desc = items[i]["weather"][0]["description"]

            temp = items[i]["temp"]["day"]
            wind = items[i]["speed"]
            gust = items[i].get("gust", None)

            unix_time = items[i]["dt"]
            date = datetime.fromtimestamp(unix_time).strftime("%d/%m")

            gust_part = f" {gust:.1f}{self.wind_unit}" if isinstance(gust, (int, float)) else ""
            table.add_row(
                date,
                f"{icon} {desc}",
                f"{temp:.1f}{self.temp_unit} {wind:.1f}{self.wind_unit}{gust_part}",
            )

        return table, city, country

    def update(self, coords: tuple[float, float], hourly_rows: int, weekly_rows: int) -> None:
        lat, lon = coords
        self.hourly_table, self.city, self.country = self.fetch_hourly(lat, lon, hourly_rows)
        self.weekly_table, _, _ = self.fetch_weekly(lat, lon, weekly_rows)