"""
Heartbeat – background thread that pushes health to the API Gateway.

Works for both software and hardware entries.  If the gateway disables
or removes the entry the kill-switch fires and the host process exits.
Network errors are logged but do NOT trigger a shutdown — only an
explicit 503 (disabled) or 404 (not registered) does.

Usage:
    from gateway   import GatewayClient
    from heartbeat import Heartbeat

    gw = GatewayClient(url, username, password)

    hb = Heartbeat(gw, kind="software", name="my-app")
    hb.start()                                      # first beat + background loop
    hb.set_health("warning", {"disk": "full"})      # update anytime
"""

import os
import sys
import threading
from typing import Optional, Dict

import requests

HEARTBEAT_INTERVAL = 30  # seconds


class Heartbeat:
    def __init__(self, client, *, kind: str, name: str):
        """
        client  – a GatewayClient instance
        kind    – "software"  or  "hardware"
        name    – the name registered on the gateway (must already exist
                  in /settings/software  or  /settings/hardware)
        """
        if kind not in ("software", "hardware"):
            raise ValueError('kind must be "software" or "hardware"')

        self._client = client
        self._kind = kind
        self._name = name

        # current health — updated via set_health(), read on every beat
        self._health: str = "ok"
        self._details: Optional[Dict] = {"status": "running"}

        self._stop = threading.Event()
        self.killed = threading.Event()   # set the moment the gateway says "off"

    # ── public helpers ──────────────────────────────────────────────

    def set_health(self, health: str, details: Optional[Dict] = None):
        """Update health from anywhere in your code.  Picked up on next beat."""
        if health not in ("ok", "warning", "error"):
            raise ValueError('health must be "ok", "warning", or "error"')
        self._health = health
        if details is not None:
            self._details = details

    # ── single beat ─────────────────────────────────────────────────

    def _beat(self) -> bool:
        """POST one heartbeat.  Returns False when the app must shut down."""
        try:
            if self._kind == "software":
                self._client.push_software_heartbeat(self._name, self._health, self._details)
            else:
                self._client.push_hardware_heartbeat(self._name, self._health, details=self._details)
            return True

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code in (503, 404):
                return False          # explicit disable / not registered → kill
            print(f"[HEARTBEAT] warning: {e}", flush=True)
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
                    f"\n[HEARTBEAT] '{self._name}' has been disabled"
                    " on the gateway — shutting down\n",
                    flush=True,
                )
                self._stop.wait(1)   # 1 s grace period
                os._exit(1)

    # ── lifecycle ───────────────────────────────────────────────────

    def start(self):
        """Run the first beat immediately, then start the background thread.

        Calls sys.exit(1) right away if the entry is already disabled."""
        if not self._beat():
            print(
                f"[HEARTBEAT] '{self._name}' is disabled or not registered"
                " on the gateway. Exiting.",
                flush=True,
            )
            sys.exit(1)

        self._stop.clear()
        self.killed.clear()
        threading.Thread(target=self._loop, daemon=True).start()
        print(f"[HEARTBEAT] Started — reporting as {self._kind} '{self._name}'", flush=True)

    def stop(self):
        """Signal the background thread to stop."""
        self._stop.set()
