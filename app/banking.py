from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv


class Banking:
    def __init__(self, bank_dir: Path | None = None):
        self.bank_dir: Path | None = bank_dir
        self.error: str | None = None

        self.exists: bool = bool(bank_dir and bank_dir.exists() and bank_dir.is_dir())

        # Current “state” you probably want to keep:
        self.transactions: list[list[str]] = []
        self.balance: float = 0.0
        self.total_spent: float = 0.0
        self.total_received: float = 0.0

        if not self.exists:
            self.error = "Bank directory does not exist (or is not a directory)."

    def _parse_bank_date(self, d: str):
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime((d or "").strip(), fmt)
            except ValueError:
                continue
        return None

    def pick_latest_transactions(self, transactions: list[list[str]], n: int) -> list[list[str]]:
        if not transactions:
            return []

        first_date = self._parse_bank_date(transactions[0][0] if transactions[0] else "")
        last_date = self._parse_bank_date(transactions[-1][0] if transactions[-1] else "")

        if first_date and last_date:
            # ascending => newest at end
            if first_date <= last_date:
                return transactions[-n:]
            # descending => newest at start
            return transactions[:n]

        # fallback: many exports are newest-first
        return transactions[:n]

    def load_latest_bank_csv(self) -> tuple[list[list[str]], float, float, float]:
        if not self.exists or self.bank_dir is None:
            raise FileNotFoundError("Bank directory not found.")

        csv_files = sorted(self.bank_dir.glob("*.csv"), key=lambda p: p.stat().st_mtime)
        if not csv_files:
            raise FileNotFoundError("Keine CSV-Dateien gefunden!")

        latest_csv_path = csv_files[-1]

        transactions: list[list[str]] = []
        total_spent = 0.0
        total_received = 0.0

        with latest_csv_path.open("r", encoding="utf-8", errors="replace") as f:
            csv_reader = csv.reader(f, delimiter=";")
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

        balance = total_received - total_spent
        return transactions, balance, total_spent, total_received

    def update(self, rows: int) -> None:
        """Refresh object state from latest CSV and keep only the newest `rows` transactions."""
        tx, bal, spent, received = self.load_latest_bank_csv()
        self.total_spent = spent
        self.total_received = received
        self.balance = bal
        self.transactions = self.pick_latest_transactions(tx, rows)
