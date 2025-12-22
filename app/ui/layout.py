from __future__ import annotations

from datetime import datetime
from os import name

from rich.layout import Layout
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
import pyfiglet

from app.ui.utils import clamp_text

def build_status_bar(
    *,
    location_label: str,
    city: str,
    country: str,
    coords: tuple[float, float],
    next_refresh_in_seconds: int,
) -> Text:
    now_local = datetime.now().strftime("%H:%M:%S")

    return Text.assemble(
        (" ● ", "label"),
        ("STATUS ", "table.header"),
        (now_local, "money.neutral"),
        (" | ", "label"),
        (clamp_text(city, 14), "money.good"),
        (" ", "label"),
        (f"{coords[0]:.2f},{coords[1]:.2f}", "money.neutral"),
        (" | ", "label"),
        ("Next ", "label"),
        (f"{max(0, next_refresh_in_seconds)}s", "money.neutral"),
    )

def build_banking_table(transactions: list[list[str]]) -> Table:
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

    return bank_table


def build_layout(
    *,
    location_label: str,
    coords: tuple[float, float],
    city: str,
    country: str,
    hourly_table: Table,
    weekly_table: Table,
    transactions: list[list[str]],
    balance: float,
    total_spent: float,
    total_received: float,
    next_refresh_in_seconds: int,
    refresh_minutes: int,
    units: str,
) -> Layout:
    layout = Layout(name="root")

    layout.split_column(
        Layout(name="root/spacer",ratio=2),
        Layout(name="root/status", size=1),
        Layout(name="root/weather", ratio=5),
        Layout(name="root/separator", size=1),
        Layout(name="root/banking", ratio=4),
    )
    layout["root/spacer"].update(Text(""))
    layout["root/status"].update(
        build_status_bar(
            location_label=location_label,
            city=city,
            country=country,
            coords=coords,
            next_refresh_in_seconds=next_refresh_in_seconds,
        )
    )

    layout["root/separator"].update(Rule(style="divider", characters="━"))

    # Weather section
    layout["root/weather"].split_column(
        Layout(name="root/weather/info", size=6),
        Layout(name="root/weather/forecast"),
    )

    layout["root/weather/info"].split(
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

    layout["root/weather/info/name"].update(Text(pyfiglet.figlet_format(city or "—"), style="title"))
    layout["root/weather/info/location"].update(
        Text(f"Lat| {coords[0]:.5f}  Lon| {coords[1]:.5f}  Country| {country}",
    no_wrap = True,
    overflow = "ellipsis")
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

    saldo_style = "money.good" if balance > 0 else "money.bad" if balance < 0 else "money.neutral"

    layout["root/banking/info/account"].update(
        Text.assemble(
            ("\nAusgegeben| ", "label"),
            (f"{total_spent:.2f}", "money.bad"),
            ("   Bekommen| ", "label"),
            (f"{total_received:.2f}", "money.good"),
            ("\nKontosumme| ", "label"),
            (f"{balance:.2f}", saldo_style),
            ("\n", "")
        )
    )

    layout["root/banking/table"].update(build_banking_table(transactions))
    return layout