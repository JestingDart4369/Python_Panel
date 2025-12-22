from __future__ import annotations

import time
from rich.console import Console
from rich.live import Live

from app.paths import BANK_DIR, LOG_DIR, CONFIG_DIR, CONFIG_PATH
from app.config import Config
from app.ui.theme import STYLES
from app.ui.utils import compute_forecast_limits
from app.ui.layout import build_layout

from app.banking import Banking
from app.location import LocationService
from app.weather import WeatherService

from requirements import apikey


def main():
    BANK_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = Config(CONFIG_PATH)

    console = Console(theme=STYLES.get(config.data["theme"], STYLES["classic"]))

    refresh_seconds = max(10, int(config.data["refresh_minutes"]) * 60)
    last_fetch_at = 0.0

    bank = Banking(BANK_DIR)
    location = LocationService(
        use_winrt=bool(config.data["use_winrt_location"]),
        api_key_get_city=apikey.api_key_getcity,
        api_key_geo=apikey.api_key_geo,
    )
    weather = WeatherService(api_key=apikey.api_key_weather, units=config.data["units"])

    live_screen = bool(config.data.get("live_screen", False))

    try:
        with Live(console=console, screen=live_screen, auto_refresh=False) as live:
            while True:
                now = time.time()
                elapsed = now - last_fetch_at
                remaining = int(refresh_seconds - elapsed)

                if last_fetch_at == 0.0 or elapsed >= refresh_seconds:
                    last_fetch_at = now

                    hourly_rows, weekly_rows = compute_forecast_limits(
                        console,
                        max_hourly=int(config.data["max_hourly_forecast"]),
                        max_weekly=int(config.data["max_weekly_forecast"]),
                    )

                    location.update()
                    weather.update(location.coords, hourly_rows, weekly_rows)

                    bank_rows = max(1, min(int(config.data["bank_rows"]), 50))
                    bank.update(rows=bank_rows)

                layout = build_layout(
                    location_label=location.label,
                    coords=location.coords,
                    city=weather.city,
                    country=weather.country,
                    hourly_table=weather.hourly_table,
                    weekly_table=weather.weekly_table,
                    transactions=bank.transactions,
                    balance=bank.balance,
                    total_spent=bank.total_spent,
                    total_received=bank.total_received,
                    next_refresh_in_seconds=max(0, remaining),
                    refresh_minutes=int(config.data["refresh_minutes"]),
                    units=config.data["units"],
                )
                console.clear()
                live.update(layout, refresh=True)
                time.sleep(1)

    except KeyboardInterrupt:
        if not config.data["live_screen"]:
            console.clear()
        print("Dashboard stopped.")


if __name__ == "__main__":
    main()