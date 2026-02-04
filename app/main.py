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

from requirements import config as gw_config
from requirements.gateway import GatewayClient
from app.heartbeat import Heartbeat


def main():
    BANK_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = Config(CONFIG_PATH)

    console = Console(theme=STYLES.get(config.data["theme"], STYLES["autumn"]))

    refresh_seconds = max(10, int(config.data["refresh_minutes"]) * 60)
    last_fetch_at = 0.0

    bank = Banking(BANK_DIR)
    location = LocationService(
        use_winrt=bool(config.data["use_winrt_location"]),
    )
    weather = WeatherService(units=config.data["units"])

    # ── kill-switch heartbeat ─────────────────────────────────────
    # Disable "python-panel" in /settings/software on the gateway to
    # shut the dashboard down remotely.
    _gw = GatewayClient(gw_config.GATEWAY_URL, gw_config.GATEWAY_USERNAME, gw_config.GATEWAY_PASSWORD)
    heartbeat = Heartbeat(_gw, kind="software", name="python-panel")
    heartbeat.start()

    live_screen = bool(config.data.get("live_screen", False))

    try:
        with Live(console=console, screen=live_screen, auto_refresh=False) as live:
            while True:
                if heartbeat.killed.is_set():
                    break
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

        # Live block exited via heartbeat kill
        console.clear()
        print("[HEARTBEAT] Dashboard shut down — disabled on gateway.")

    except KeyboardInterrupt:
        if not config.data["live_screen"]:
            console.clear()
        print("Dashboard stopped.")


if __name__ == "__main__":
    main()