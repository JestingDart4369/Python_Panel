"""
Heartbeat – reports python-panel's health to the API Gateway every 30 s.
If the gateway disables this software entry the dashboard shuts down
(kill switch).  Network errors are logged but do NOT trigger a shutdown —
only an explicit 503 (disabled) or 404 (not registered) does.
"""
import os
import sys
import threading

import requests
from datetime import datetime, timedelta

GATEWAY_URL = "https://api.homeasistant-homelab.uk"
HEARTBEAT_INTERVAL = 30  # seconds between heartbeats


class Heartbeat:
    def __init__(self, software_name: str, username: str, password: str):
        self.software_name = software_name
        self._username = username
        self._password = password

        self._token: str | None = None
        self._token_expiry: datetime | None = None

        self._stop = threading.Event()
        self.killed = threading.Event()   # set the moment the gateway says "off"

    # ── auth ────────────────────────────────────────────────────────

    def _get_token(self) -> str:
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._token

        r = requests.post(
            f"{GATEWAY_URL}/auth/login",
            json={"username": self._username, "password": self._password},
            timeout=10,
        )
        r.raise_for_status()

        self._token = r.json()["access_token"]
        self._token_expiry = datetime.now() + timedelta(minutes=55)
        return self._token

    # ── single beat ─────────────────────────────────────────────────

    def _beat(self) -> bool:
        """POST one heartbeat.  Returns False when the app must shut down."""
        try:
            token = self._get_token()
            r = requests.post(
                f"{GATEWAY_URL}/software/{self.software_name}/heartbeat",
                json={"health": "ok", "details": {"status": "running"}},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )

            # 503 = disabled in gateway, 404 = not registered
            if r.status_code in (503, 404):
                return False

            r.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            # network problems → warn but keep running
            print(f"[HEARTBEAT] network warning: {e}", flush=True)
            return True

    # ── background loop ─────────────────────────────────────────────

    def _loop(self):
        while not self._stop.wait(HEARTBEAT_INTERVAL):
            if not self._beat():
                self.killed.set()
                print(
                    f"\n[HEARTBEAT] '{self.software_name}' has been disabled"
                    " on the gateway — shutting down\n",
                    flush=True,
                )
                # 1 s grace: main loop checks killed every second and can
                # exit cleanly (Rich Live teardown).  If it doesn't, force.
                self._stop.wait(1)
                os._exit(1)

    # ── public API ──────────────────────────────────────────────────

    def start(self):
        """First beat + background thread.  sys.exit(1) if already disabled."""
        if not self._beat():
            print(
                f"[HEARTBEAT] '{self.software_name}' is disabled or not"
                " registered on the gateway. Exiting.",
                flush=True,
            )
            sys.exit(1)

        self._stop.clear()
        self.killed.clear()
        threading.Thread(target=self._loop, daemon=True).start()
        print(f"[HEARTBEAT] Started — reporting as '{self.software_name}'", flush=True)

    def stop(self):
        self._stop.set()
