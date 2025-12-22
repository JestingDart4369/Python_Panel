from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import requests
from rich.table import Table


URL_WEATHER_HOURLY = "https://pro.openweathermap.org/data/2.5/forecast/hourly"
URL_WEATHER_DAILY = "https://api.openweathermap.org/data/2.5/forecast/daily"

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
    def __init__(self, api_key: str, units: str):
        self.api_key = api_key
        self.units = units  # "metric" or "imperial"

        self.temp_unit = "°C" if units == "metric" else "°F"
        self.wind_unit = "m/s" if units == "metric" else "mph"

        # state you can read from main/ui
        self.city = "—"
        self.country = "—"
        self.hourly_table = Table()
        self.weekly_table = Table()

    def _request_json(self, url: str) -> dict:
        headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            raise WeatherError(f"API Error ({r.status_code}): Unable to retrieve weather information")
        return r.json()

    def fetch_hourly(self, lat: float, lon: float, rows: int) -> tuple[Table, str, str]:
        url = f"{URL_WEATHER_HOURLY}?lat={lat}&lon={lon}&appid={self.api_key}&units={self.units}"
        data = self._request_json(url)

        city = data["city"]["name"]
        country = data["city"]["country"]

        table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
        table.add_column("Time", width=5, no_wrap=True)
        table.add_column("Weather", width=18, overflow="ellipsis")
        table.add_column("Data", width=18, justify="right", no_wrap=True, overflow="ellipsis")

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
        url = f"{URL_WEATHER_DAILY}?lat={lat}&lon={lon}&appid={self.api_key}&units={self.units}"
        data = self._request_json(url)

        city = data["city"]["name"]
        country = data["city"]["country"]

        table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
        table.add_column("Date", width=6, no_wrap=True)
        table.add_column("Weather", width=18, overflow="ellipsis")
        table.add_column("Data", width=18, justify="right", no_wrap=True, overflow="ellipsis")

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