# =========================
# Imports
# =========================
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import asyncio
import csv
import json
import os
import sys
import time

import requests
import pyfiglet

from winrt.windows.devices.geolocation import Geolocator

from rich.console import Console
from rich.layout import Layout
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.live import Live


# =========================
# Paths / Project setup
# =========================
os.makedirs("../02_Bankauszüge", exist_ok=True)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

CONFIG_PATH = Path(project_root) / "requirements" / "config.json"

# Local import (after sys.path manipulation)
from requirements import apikey  # noqa: E402

api_key_geo = apikey.api_key_geo
api_key_weather = apikey.api_key_weather
api_key_get_city = apikey.api_key_getcity


# =========================
# Config
# =========================
DEFAULT_CONFIG = {
    "theme": "classic",
    "refresh_minutes": 15,
    "units": "metric",            # "metric" or "imperial"
    "use_winrt_location": True,   # True/False

    # UI limits
    "bank_rows": 2,               # show last N transactions
    "max_hourly_forecast": 12,    # upper bound
    "max_weekly_forecast": 7,     # upper bound

    # Live "screen" mode:
    # True  -> full screen (no scrollback, looks clean)
    # False -> normal terminal buffer (scroll works)
    # (We support both keys: live_screen and screen)
    "live_screen": False,
}


def load_config() -> dict:
    """Load requirements/config.json, falling back to defaults if missing/invalid."""
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_cfg = json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()

    cfg = DEFAULT_CONFIG.copy()
    cfg.update(user_cfg)
    return cfg


app_config = load_config()


# =========================
# API URLs
# =========================
URL_WEATHER_HOURLY = "https://pro.openweathermap.org/data/2.5/forecast/hourly?"
URL_WEATHER_DAILY = "https://api.openweathermap.org/data/2.5/forecast/daily?"
URL_IPREGISTRY = "https://api.ipregistry.co"


# =========================
# Styling / Themes
# =========================
STYLES = {
    "classic": Theme({
        "rule": "gold3",
        "divider": "gold3",
        "label": "gold3",
        "table.header": "bold gold3",
        "table.title": "bold gold3",
        "table.border": "gold3",
        "app.title": "bold gold3",
        "title": "bold orange3",
        "app.weather": "bold green3",
        "money.good": "bold green3",
        "money.bad": "bold red3",
        "money.neutral": "bold khaki3",
        "panel.border": "gold3",
    }),
    "midnight": Theme({
        "rule": "bright_cyan",
        "divider": "bright_cyan",
        "label": "bright_cyan",
        "table.header": "bold bright_cyan",
        "table.title": "bold bright_cyan",
        "table.border": "bright_cyan",
        "app.title": "bold bright_cyan",
        "title": "bold orange1",
        "app.weather": "cyan",
        "money.good": "bold bright_green",
        "money.bad": "bold bright_red",
        "money.neutral": "bold bright_cyan",
        "panel.border": "bright_cyan",
    }),
    "forest": Theme({
        "rule": "green3",
        "divider": "green3",
        "label": "green3",
        "table.header": "bold green3",
        "table.title": "bold green3",
        "table.border": "green3",
        "app.title": "bold green3",
        "title": "bold dark_orange3",
        "app.weather": "green",
        "money.good": "bold green3",
        "money.bad": "bold red3",
        "money.neutral": "bold green3",
        "panel.border": "green3",
    }),
    "sunset": Theme({
        "rule": "magenta3",
        "divider": "magenta3",
        "label": "magenta3",
        "table.header": "bold magenta3",
        "table.title": "bold magenta3",
        "table.border": "magenta3",
        "app.title": "bold magenta3",
        "title": "bold orange3",
        "app.weather": "bold yellow3",
        "money.good": "bold green3",
        "money.bad": "bold red3",
        "money.neutral": "bold magenta3",
        "panel.border": "magenta3",
    }),
    "high_contrast": Theme({
        "rule": "white",
        "divider": "white",
        "label": "bold white",
        "table.header": "bold white on black",
        "table.title": "bold white",
        "table.border": "white",
        "app.title": "bold white",
        "title": "bold bright_white",
        "app.weather": "bold bright_white",
        "money.good": "bold bright_green",
        "money.bad": "bold bright_red",
        "money.neutral": "bold bright_white",
        "panel.border": "white",
    }),
}

ACTIVE_THEME = app_config.get("theme", "classic")
console = Console(theme=STYLES.get(ACTIVE_THEME, STYLES["classic"]))


# =========================
# Smart sizing helpers
# =========================
def compute_forecast_limits(c: Console) -> tuple[int, int]:
    """
    Dynamically decide how many forecast rows fit on screen.
    Keeps it readable on small terminals.
    """
    height = c.size.height
    usable = height - 20  # rough overhead for title + headers + banking

    if usable <= 10:
        hourly, weekly = 4, 3
    elif usable <= 16:
        hourly, weekly = 6, 4
    elif usable <= 22:
        hourly, weekly = 8, 5
    else:
        hourly = int(app_config.get("max_hourly_forecast", 12))
        weekly = int(app_config.get("max_weekly_forecast", 7))

    hourly = max(1, min(hourly, int(app_config.get("max_hourly_forecast", 12))))
    weekly = max(1, min(weekly, int(app_config.get("max_weekly_forecast", 7))))
    return hourly, weekly


def clamp_text(value: str, max_len: int) -> str:
    if value is None:
        return ""
    value = str(value)
    return value if len(value) <= max_len else value[: max_len - 1] + "…"


# =========================
# Banking "latest N" helper
# =========================
def _parse_bank_date(d: str):
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime((d or "").strip(), fmt)
        except ValueError:
            pass
    return None


def pick_latest_transactions(transactions: list[list[str]], n: int) -> list[list[str]]:
    """
    Returns the newest N transactions even if the CSV is:
    - newest -> oldest  (newest at top)
    - oldest -> newest  (newest at bottom)
    We try to detect order using the first column date.
    """
    if not transactions:
        return []

    first_date = _parse_bank_date(transactions[0][0] if transactions[0] else "")
    last_date = _parse_bank_date(transactions[-1][0] if transactions[-1] else "")

    if first_date and last_date:
        # ascending => newest at end
        if first_date <= last_date:
            return transactions[-n:]
        # descending => newest at start
        return transactions[:n]

    # fallback: many exports are newest-first
    return transactions[:n]


# =========================
# Location
# =========================
async def winrt_get_lat_lon():
    geo = Geolocator()
    pos = await geo.get_geoposition_async()
    point = pos.coordinate.point.position
    return point.latitude, point.longitude


def detect_city_from_ip() -> str:
    url = f"{URL_IPREGISTRY}/?key={api_key_get_city}&fields=location.city,connection"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        console.print("[bold red]Error:[/] Unable to retrieve city information")
        raise SystemExit(1)
    data = r.json()
    return data["location"]["city"]


def geocode_city(city_name: str) -> tuple[float, float]:
    url = f"https://api.geoapify.com/v1/geocode/search?text={city_name}&apiKey={api_key_geo}"
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}

    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        console.print("[bold red]Error:[/] Unable to retrieve coordinates information")
        raise SystemExit(1)

    data = r.json()
    lon = data["features"][0]["properties"]["lon"]
    lat = data["features"][0]["properties"]["lat"]
    return lat, lon


def get_weather_coordinates() -> tuple[str, tuple[float, float]]:
    """Return (label, (lat, lon)) using WinRT if enabled & possible, else fallback IP->city->geo."""
    if not app_config.get("use_winrt_location", True):
        city = detect_city_from_ip()
        return city, geocode_city(city)

    try:
        asyncio.get_running_loop()
        city = detect_city_from_ip()
        return city, geocode_city(city)
    except RuntimeError:
        pass

    try:
        lat, lon = asyncio.run(winrt_get_lat_lon())
        return "Current Location", (lat, lon)
    except Exception as e:
        console.print(f"[bold yellow]WinRT location not available, falling back to IP-city geo.[/] ({e})")
        city = detect_city_from_ip()
        return city, geocode_city(city)


# =========================
# Weather
# =========================
WEATHER_ICONS = {
    "01d": "☀️", "02d": "⛅", "03d": "☁️", "04d": "☁️☁️", "09d": "🌧️",
    "10d": "🌦️", "11d": "🌩️", "13d": "🌨️", "50d": "🌫️",
    "01n": "🌙", "02n": "🌙☁️", "03n": "☁️", "04n": "☁️☁️", "09n": "🌧️",
    "10n": "🌙🌧️", "11n": "🌩️", "13n": "🌨️", "50n": "🌫️",
}

WEATHER_UNITS = app_config.get("units", "metric")
TEMP_UNIT = "°C" if WEATHER_UNITS == "metric" else "°F"
WIND_UNIT = "m/s" if WEATHER_UNITS == "metric" else "mph"


def fetch_hourly_weather(latitude: float, longitude: float, rows: int):
    url = f"{URL_WEATHER_HOURLY}lat={latitude}&lon={longitude}&appid={api_key_weather}&units={WEATHER_UNITS}"
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}

    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code != 200:
        console.print("[bold red]Error:[/] Unable to retrieve weather information")
        raise SystemExit(1)

    data = r.json()
    city = data["city"]["name"]
    land = data["city"]["country"]

    table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
    table.add_column("Time", width=5, no_wrap=True)
    table.add_column("Weather", width=18, overflow="ellipsis")
    table.add_column("Data", width=18, justify="right")

    items = data.get("list", [])
    for i in range(min(rows, len(items))):
        icon = items[i]["weather"][0]["icon"]
        weather_icon = WEATHER_ICONS.get(icon, "")
        description = items[i]["weather"][0]["description"]

        temperature = items[i]["main"]["temp"]
        wind_speed = items[i]["wind"]["speed"]
        wind_gust = items[i]["wind"].get("gust", None)

        unix_time = items[i]["dt"]
        tz_offset = data["city"]["timezone"]
        local_time = datetime.fromtimestamp(unix_time, tz=timezone(timedelta(seconds=tz_offset)))
        formatted = local_time.strftime("%H:%M")

        gust_part = f" {wind_gust:.1f}{WIND_UNIT}" if isinstance(wind_gust, (int, float)) else ""
        table.add_row(
            formatted,
            f"{weather_icon} {description}",
            f"{temperature:.1f}{TEMP_UNIT} {wind_speed:.1f}{WIND_UNIT}{gust_part}",
        )

    return table, city, land


def fetch_weekly_weather(latitude: float, longitude: float, rows: int):
    url = f"{URL_WEATHER_DAILY}lat={latitude}&lon={longitude}&appid={api_key_weather}&units={WEATHER_UNITS}"
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}

    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code != 200:
        console.print("[bold red]Error:[/] Unable to retrieve weather information")
        raise SystemExit(1)

    data = r.json()
    city = data["city"]["name"]
    land = data["city"]["country"]

    table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
    table.add_column("Date", width=6, no_wrap=True)
    table.add_column("Weather", width=18, overflow="ellipsis")
    table.add_column("Data", width=18, justify="right")

    items = data.get("list", [])
    for i in range(min(rows, len(items))):
        icon = items[i]["weather"][0]["icon"]
        weather_icon = WEATHER_ICONS.get(icon, "")
        description = items[i]["weather"][0]["description"]

        temperature = items[i]["temp"]["day"]
        wind_speed = items[i]["speed"]
        wind_gust = items[i].get("gust", None)

        unix_time = items[i]["dt"]
        date = datetime.fromtimestamp(unix_time).strftime("%d/%m")

        gust_part = f" {wind_gust:.1f}{WIND_UNIT}" if isinstance(wind_gust, (int, float)) else ""
        table.add_row(
            date,
            f"{weather_icon} {description}",
            f"{temperature:.1f}{TEMP_UNIT} {wind_speed:.1f}{WIND_UNIT}{gust_part}",
        )

    return table, city, land


# =========================
# Banking
# =========================
def load_latest_bank_csv():
    base_dir = "../02_Bankauszüge"
    csv_files = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if f.lower().endswith(".csv")]

    if not csv_files:
        console.print("[bold red]Error:[/] Keine CSV-Dateien gefunden!")
        raise SystemExit(1)

    latest_csv_path = max(csv_files, key=os.path.getmtime)

    transactions = []
    total_spent = 0.0
    total_received = 0.0

    with open(latest_csv_path, "r", encoding="utf-8", errors="replace") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=";")
        next(csv_reader, None)

        for line in csv_reader:
            transactions.append(line)

            spent_str = (line[3] or "").replace("'", "")
            try:
                total_spent += float(spent_str) if spent_str else 0.0
            except ValueError:
                pass

            recv_str = (line[4] or "").replace("'", "")
            try:
                total_received += float(recv_str) if recv_str else 0.0
            except ValueError:
                pass

    account_balance = total_received - total_spent
    return transactions, account_balance, total_spent, total_received


# =========================
# UI / Layout building
# =========================
def build_status_bar(
    location_label: str,
    city: str,
    land: str,
    coordinates: tuple[float, float],
    next_refresh_in_seconds: int,
) -> Text:
    now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    refresh_minutes = app_config.get("refresh_minutes", 15)
    units = app_config.get("units", "metric")

    return Text.assemble(
        (" ● ", "label"),
        ("STATUS ", "table.header"),
        (now_local, "money.neutral"),
        ("  |  ", "label"),
        ("Src: ", "label"),
        (clamp_text(location_label, 18), "money.good"),
        ("  |  ", "label"),
        ("City: ", "label"),
        (clamp_text(f"{city}, {land}", 22), "money.good"),
        ("  |  ", "label"),
        ("Lat/Lon: ", "label"),
        (f"{coordinates[0]:.3f},{coordinates[1]:.3f}", "money.neutral"),
        ("  |  ", "label"),
        ("Next: ", "label"),
        (f"{max(0, next_refresh_in_seconds)}s", "money.neutral"),
        ("  |  ", "label"),
        ("Units: ", "label"),
        (clamp_text(units, 8), "money.neutral"),
        ("  |  ", "label"),
        ("Every: ", "label"),
        (f"{refresh_minutes}m", "money.neutral"),
    )


def build_layout(
    location_label: str,
    city: str,
    land: str,
    coordinates: tuple[float, float],
    hourly_table: Table,
    weekly_table: Table,
    transactions: list,
    account_balance: float,
    total_spent: float,
    total_received: float,
    next_refresh_in_seconds: int,
) -> Layout:
    layout = Layout(name="root")

    layout.split_column(
        Layout(name="root/status", size=1),
        Layout(name="root/weather", ratio=3),
        Layout(name="root/separator", size=1),
        Layout(name="root/banking", ratio=2),
    )

    layout["root/status"].update(
        build_status_bar(
            location_label=location_label,
            city=city,
            land=land,
            coordinates=coordinates,
            next_refresh_in_seconds=next_refresh_in_seconds,
        )
    )

    layout["root/separator"].update(Rule(style="divider", characters="━"))

    # Weather section
    layout["root/weather"].split_column(
        Layout(name="root/weather/info", size=6),
        Layout(name="root/weather/forecast", ratio=1),
    )

    layout["root/weather/info"].split_row(
        Layout(name="root/weather/info/name"),
        Layout(name="root/weather/info/location", size=1),
    )

    layout["root/weather/forecast"].split_row(
        Layout(name="root/weather/forecast/hourly"),
        Layout(name="root/weather/forecast/weekly"),
    )

    layout["root/weather/forecast/hourly"].split_column(
        Layout(name="root/weather/forecast/hourly/title", size=1),
        Layout(name="root/weather/forecast/hourly/data"),
    )

    layout["root/weather/forecast/weekly"].split_column(
        Layout(name="root/weather/forecast/weekly/title", size=1),
        Layout(name="root/weather/forecast/weekly/data"),
    )

    layout["root/weather/info/name"].update(Text(pyfiglet.figlet_format(city), style="title"))
    layout["root/weather/info/location"].update(
        f"Lat| {coordinates[0]:.5f}  Lon| {coordinates[1]:.5f}  Country| {land}"
    )

    layout["root/weather/forecast/hourly/title"].update(Text("Hourly Forecast", style="label"))
    layout["root/weather/forecast/weekly/title"].update(Text("Weekly Forecast", style="label"))

    layout["root/weather/forecast/hourly/data"].update(hourly_table)
    layout["root/weather/forecast/weekly/data"].update(weekly_table)

    # Banking section
    layout["root/banking"].split_row(
        Layout(name="root/banking/info"),
        Layout(name="root/banking/table"),
    )

    layout["root/banking/info"].split_column(
        Layout(name="root/banking/info/title", size=6),
        Layout(name="root/banking/info/account"),
    )

    layout["root/banking/info/title"].update(Text(pyfiglet.figlet_format("Banking"), style="title"))

    saldo_style = (
        "money.good" if account_balance > 0
        else "money.bad" if account_balance < 0
        else "money.neutral"
    )

    layout["root/banking/info/account"].update(
        Text.assemble(
            ("\nAusgegeben| ", "label"),
            (f"{total_spent:.2f}", "money.bad"),
            ("   Bekommen| ", "label"),
            (f"{total_received:.2f}", "money.good"),
            ("\nKontosumme| ", "label"),
            (f"{account_balance:.2f}", saldo_style),
            ("\n", "")
        )
    )

    bank_table = Table(
        title=f"Letzte {len(transactions)} Transaktionen",
        show_header=True,
        header_style="table.header",
        title_style="table.title",
    )
    bank_table.add_column("Buchung", no_wrap=True, width=10)
    bank_table.add_column("Valuta", no_wrap=True, width=10)
    bank_table.add_column("Buchungstext", width=26, overflow="ellipsis")
    bank_table.add_column("Belastung", justify="right", no_wrap=True, width=10)
    bank_table.add_column("Gutschrift", justify="right", no_wrap=True, width=10)
    bank_table.add_column("Saldo", justify="right", no_wrap=True, width=10)

    for tx in transactions:
        row = (tx + ["", "", "", "", "", ""])[:6]
        bank_table.add_row(row[0], row[1], row[2], row[3], row[4], row[5])

    layout["root/banking/table"].update(bank_table)
    return layout


# =========================
# Main (Live refresh without breaking layout)
# =========================
def main():
    refresh_seconds = int(app_config.get("refresh_minutes", 15) * 60)
    refresh_seconds = max(10, refresh_seconds)  # safety: never hammer the APIs

    last_fetch_at = 0.0

    cached_location_label = "—"
    cached_coordinates = (0.0, 0.0)
    cached_city = "—"
    cached_land = "—"
    cached_hourly_table = Table()
    cached_weekly_table = Table()
    cached_transactions: list = []
    cached_account_balance = 0.0
    cached_total_spent = 0.0
    cached_total_received = 0.0

    # Prefer "live_screen", but allow "screen" as an alias (your config uses it)
    if "live_screen" in app_config:
        live_screen = bool(app_config.get("live_screen"))
    else:
        live_screen = bool(app_config.get("screen", False))

    with Live(console=console, screen=live_screen, auto_refresh=False, transient=False) as live:
        while True:
            now = time.time()
            elapsed = now - last_fetch_at
            remaining = int(refresh_seconds - elapsed)

            if last_fetch_at == 0.0 or elapsed >= refresh_seconds:
                last_fetch_at = now

                hourly_rows, weekly_rows = compute_forecast_limits(console)

                cached_location_label, cached_coordinates = get_weather_coordinates()

                cached_hourly_table, cached_city, cached_land = fetch_hourly_weather(
                    cached_coordinates[0], cached_coordinates[1], hourly_rows
                )
                cached_weekly_table, _, _ = fetch_weekly_weather(
                    cached_coordinates[0], cached_coordinates[1], weekly_rows
                )

                all_tx, cached_account_balance, cached_total_spent, cached_total_received = load_latest_bank_csv()

                bank_rows = int(app_config.get("bank_rows", 2))
                bank_rows = max(1, min(bank_rows, 50))

                cached_transactions = pick_latest_transactions(all_tx, bank_rows)

            layout = build_layout(
                location_label=cached_location_label,
                city=cached_city,
                land=cached_land,
                coordinates=cached_coordinates,
                hourly_table=cached_hourly_table,
                weekly_table=cached_weekly_table,
                transactions=cached_transactions,
                account_balance=cached_account_balance,
                total_spent=cached_total_spent,
                total_received=cached_total_received,
                next_refresh_in_seconds=max(0, remaining),
            )

            live.update(layout, refresh=True)
            time.sleep(1)


if __name__ == "__main__":
    main()