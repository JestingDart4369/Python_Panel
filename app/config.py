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

DEFAULT_CONFIG = {
    "theme": "classic",
    "refresh_minutes": 15,
    "units": "metric",            # "metric" or "imperial"
    "use_winrt_location": True,   # True/False

    # UI limits
    "bank_rows": 2,               # show last N transactions
    "max_hourly_forecast": 12,    # upper bound
    "max_weekly_forecast": 7,
    "live_screen": False,
}

class Config:
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path
        self.data = DEFAULT_CONFIG.copy()
        self.exists = False

        if config_path is not None and config_path.exists():
            self.exists = True
            self._load()

    def _load(self):
        with self.config_path.open("r", encoding="utf-8") as f:
            self.data = json.load(f)