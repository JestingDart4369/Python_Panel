from datetime import datetime, timedelta, timezone
from rich.layout import Layout
from rich.table import Table
from rich.console import Console
from rich.theme import Theme
from rich.text import Text
from rich.rule import Rule
from rich.prompt import Prompt
from rich.panel import Panel
import requests
import pyfiglet
import sys
import os
import csv


os.makedirs("./02_Bankauszüge", exist_ok=True)

# Go to the project root folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Now import from /requirements
from requirements import apikey
api_key_geo = apikey.api_key_geo
api_key_weather = apikey.api_key_weather


# =========================================================
# STYLE SYSTEM (change your whole look here)
# =========================================================
STYLES = {
    # ===== Classic (warm gold, no neon) =====
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

    # ===== Midnight (modern cyan/blue) =====
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

    # ===== Forest (soft, low eye strain) =====
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

    # ===== Sunset (warm purple/orange) =====
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

    # ===== High Contrast (maximum readability) =====
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


def preview_theme(theme_name: str) -> None:
    """Print a quick preview using the selected theme."""
    preview_console = Console(theme=STYLES[theme_name])

    preview_console.print(Rule("Preview", style="rule", characters="━"))
    preview_console.print(Text("City Title Example", style="title"))
    preview_console.print(Text("Banking Title Example", style="title"))
    preview_console.print(Text("Labels look like this", style="label"))

    money_line = Text.assemble(
        ("Ausgegeben| ", "label"), ("12.50", "money.bad"),
        ("   Bekommen| ", "label"), ("25.00", "money.good"),
        ("   Kontosumme| ", "label"), ("12.50", "money.neutral"),
    )

    demo_table = Table(
        title="Table Title Example",
        show_header=True,
        header_style="table.header",
        title_style="table.title",
        border_style="table.border",
    )

    demo_table.add_column("Col A")
    demo_table.add_column("Col B")
    demo_table.add_row("hello", "world")

    preview_console.print(Panel(money_line, title="Money Styles", border_style="panel.border"))
    preview_console.print(demo_table)
    preview_console.print(Rule(style="rule", characters="━"))


def choose_theme(default: str = "classic") -> str:
    """Theme selector menu + preview. Lets you cancel or try another theme."""
    plain = Console()

    keys = list(STYLES.keys())
    descriptions = {
        "classic": "Warm + soft gold (not neon)",
        "midnight": "Modern cyan/blue",
        "forest": "Calm green, low eye strain",
        "sunset": "Warm magenta/orange",
        "high_contrast": "Maximum readability (white/black)",
    }

    while True:
        menu = Table(title="Theme Selector", show_header=True, header_style="bold")
        menu.add_column("#", justify="right")
        menu.add_column("Theme")
        menu.add_column("Description")

        for i, k in enumerate(keys, start=1):
            menu.add_row(str(i), k, descriptions.get(k, ""))

        plain.print(menu)

        choice = Prompt.ask(
            "Pick a theme number ([bold]q[/bold] to cancel)",
            default="1",
        ).strip().lower()

        if choice in {"q", "quit", "exit"}:
            plain.print(f"\nCancelled. Using default: [bold]{default}[/bold]\n")
            return default

        if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
            plain.print("[bold red]Invalid choice.[/] Try again.\n")
            continue

        theme_name = keys[int(choice) - 1]

        plain.print(f"\nSelected: [bold]{theme_name}[/bold]\n")
        preview_theme(theme_name)

        action = Prompt.ask(
            "Use this theme? ([bold]y[/bold]es / [bold]n[/bold]o / [bold]q[/bold] cancel)",
            default="y",
            choices=["y", "n", "q"],
        )

        if action == "y":
            return theme_name
        if action == "q":
            plain.print(f"\nCancelled. Using default: [bold]{default}[/bold]\n")
            return default

        plain.print("\nOk—pick another theme.\n")
ACTIVE_STYLE = choose_theme()
console = Console(theme=STYLES[ACTIVE_STYLE])
# =========================================================


# Forecast
default_url_weather_forcast_day = "https://pro.openweathermap.org/data/2.5/forecast/hourly?"
default_url_weather_forcast_weak = "https://api.openweathermap.org/data/2.5/forecast/daily?"

Weather_icons_lib = {
    "01d": "☀️", "02d": "⛅", "03d": "☁️", "04d": "☁️☁️", "09d": "🌧️",
    "10d": "🌦️", "11d": "🌩️", "13d": "🌨️", "50d": "🌫️",
    "01n": "🌙", "02n": "🌙☁️", "03n": "☁️", "04n": "☁️☁️", "09n": "🌧️",
    "10n": "🌙🌧️", "11n": "🌩️", "13n": "🌨️", "50n": "🌫️",
}


def location_api(place: str):
    url_geo = f"https://api.geoapify.com/v1/geocode/search?text={place}&apiKey={api_key_geo}"
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}

    response_geo = requests.get(url_geo, headers=headers)
    if response_geo.status_code != 200:
        console.print("[bold red]Error:[/] Unable to retrieve Coordinates information")
        raise SystemExit(1)

    data_geo = response_geo.json()
    longitude = data_geo["features"][0]["properties"]["lon"]
    latitude = data_geo["features"][0]["properties"]["lat"]
    return latitude, longitude


def weather_api_day(latitude, longitude):
    url = f"{default_url_weather_forcast_day}lat={latitude}&lon={longitude}&appid={api_key_weather}&units=metric"
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        console.print("[bold red]Error:[/] Unable to retrieve Weather information")
        raise SystemExit(1)

    data = r.json()
    city = data["city"]["name"]
    land = data["city"]["country"]

    table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
    table.add_column("Time", width=5, no_wrap=True)
    table.add_column("Weather", no_wrap=True, overflow="ellipsis")
    table.add_column("Temp", overflow="ellipsis", no_wrap=True)

    for i in range(12):
        icon = data["list"][i]["weather"][0]["icon"]
        weather_icon = Weather_icons_lib.get(icon, "")
        description = data["list"][i]["weather"][0]["description"]
        temperature = data["list"][i]["main"]["temp"]
        wind_speed = data["list"][i]["wind"]["speed"]
        wind_gust = data["list"][i]["wind"].get("gust", "N/A")
        unix_time = data["list"][i]["dt"]
        tz_offset = data["city"]["timezone"]

        local_time = datetime.fromtimestamp(unix_time, tz=timezone(timedelta(seconds=tz_offset)))
        formatted = local_time.strftime('%H:%M')

        table.add_row(
            formatted,
            f"{weather_icon} {description}",
            f"{temperature}°C {wind_speed} Km/h  {wind_gust} Km/h"
        )

    return table, city, land


def weather_api_weak(latitude, longitude):
    url = f"{default_url_weather_forcast_weak}lat={latitude}&lon={longitude}&appid={api_key_weather}&units=metric"
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        console.print("[bold red]Error:[/] Unable to retrieve Weather information")
        raise SystemExit(1)

    data = r.json()
    city = data["city"]["name"]
    land = data["city"]["country"]

    table = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
    table.add_column("Time", width=5, no_wrap=True)
    table.add_column("Weather", no_wrap=True, overflow="ellipsis")
    table.add_column("Temp", overflow="ellipsis", no_wrap=True)

    for i in range(7):
        icon = data["list"][i]["weather"][0]["icon"]
        weather_icon = Weather_icons_lib.get(icon, "")
        description = data["list"][i]["weather"][0]["description"]
        temperature = data["list"][i]["temp"]["day"]
        wind_speed = data["list"][i]["speed"]
        wind_gust = data["list"][i].get("gust", "N/A")
        unix_time = data["list"][i]["dt"]

        date = datetime.fromtimestamp(unix_time).strftime('%d/%m')
        table.add_row(
            date,
            f"{weather_icon} {description}",
            f"{temperature}°C {wind_speed} Km/h  {wind_gust} Km/h"
        )

    return table, city, land


def Banking_csv():
    base_dir = "./02_Bankauszüge"
    csv_files = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if f.lower().endswith(".csv")]

    if not csv_files:
        console.print("[bold red]Error:[/] Keine CSV-Dateien gefunden!")
        raise SystemExit(1)

    file_csv = max(csv_files, key=os.path.getmtime)

    summary = []
    cost = 0.0
    received = 0.0

    with open(file_csv, "r", encoding="utf-8", errors="replace") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';')
        next(csv_reader, None)  # skip header

        for line in csv_reader:
            summary.append(line)

            spent_str = (line[3] or "").replace("'", "")
            try:
                cost += float(spent_str) if spent_str else 0.0
            except ValueError:
                pass

            recv_str = (line[4] or "").replace("'", "")
            try:
                received += float(recv_str) if recv_str else 0.0
            except ValueError:
                pass

    current_konto_summ = received - cost
    return summary, current_konto_summ, cost, received


# =========================
# Program
# =========================
console.print(pyfiglet.figlet_format("Dashboard"), style="app.title")
console.print("Enter the place to check", style="app.weather")
Location = input("> ")

location = location_api(Location)
output_day, city, land = weather_api_day(location[0], location[1])
output_weak = weather_api_weak(location[0], location[1])[0]
banking_summary, current_konto_summ, cost, received = Banking_csv()

layout = Layout(name="Main")
layout["Main"].split_column(
    Layout(name="Weather"),
    Layout(name="seperator"),
    Layout(name="Bank")
)

layout["seperator"].size = 1
layout["seperator"].update(Rule(style="divider", characters="━"))

# Weather
layout["Weather"].split_column(
    Layout(name="Weather_Info"),
    Layout(name="Weather_Forcast")
)
layout["Weather_Info"].split(
    Layout(name="Weather_Info_Name"),
    Layout(name="Weather_Info_Location")
)
layout["Weather_Info_Location"].size = 1
layout["Weather_Info"].size = 7

layout["Weather_Forcast"].split_row(
    Layout(name="Weather_Forcast_Hour", minimum_size=68),
    Layout(name="Weather_Forcast_Days", minimum_size=68)
)

layout["Weather_Forcast_Hour"].split(
    Layout(name="Weather_Forcast_Hour_Infos"),
    Layout(name="Weather_Forcast_Hour_Data")
)
layout["Weather_Forcast_Days"].split(
    Layout(name="Weather_Forcast_Days_Infos"),
    Layout(name="Weather_Forcast_Days_Data")
)

layout["Weather_Forcast_Hour_Infos"].size = 1
layout["Weather_Forcast_Days_Infos"].size = 1

layout["Weather_Info_Name"].update(
    Text(pyfiglet.figlet_format(city), style="title")
)
layout["Weather_Info_Location"].update(f"Lat| {location[0]} Lon| {location[1]} Country| {land}")

layout["Weather_Forcast_Hour_Infos"].update(Text("Hourly Forecast", style="label"))
layout["Weather_Forcast_Days_Infos"].update(Text("Weakly Forecast", style="label"))

layout["Weather_Forcast_Hour_Data"].update(output_day)
layout["Weather_Forcast_Days_Data"].update(output_weak)

# Banking
layout["Bank"].split_row(
    Layout(name="Bank_Info"),
    Layout(name="Bank_Data")
)

layout["Bank_Info"].split_column(
    Layout(name="Bank_Info_Name", size=6),
    Layout(name="Bank_Info_Account")
)

layout["Bank_Info_Name"].update(
    Text(pyfiglet.figlet_format("Banking"), style="title")
)

saldo_style = "money.good" if current_konto_summ > 0 else "money.bad" if current_konto_summ < 0 else "money.neutral"
layout["Bank_Info_Account"].update(
    Text.assemble(
        ("\nAusgegeben| ", "label"),
        (f"{cost:.2f}", "money.bad"),
        ("   Bekommen| ", "label"),
        (f"{received:.2f}", "money.good"),
        ("\nKontosumme| ", "label"),
        (f"{current_konto_summ:.2f}", saldo_style),
        ("\n", "")
    )
)

bank_table = Table(
    title="Alle Transaktionen",
    show_header=True,
    header_style="table.header",
    title_style="table.title"
)
bank_table.add_column("Buchung", no_wrap=True)
bank_table.add_column("Valuta", no_wrap=True)
bank_table.add_column("Buchungstext", overflow="ellipsis")
bank_table.add_column("Belastung", justify="right", no_wrap=True)
bank_table.add_column("Gutschrift", justify="right", no_wrap=True)
bank_table.add_column("Saldo", justify="right", no_wrap=True)

for t in banking_summary:
    row = (t + ["", "", "", "", "", ""])[:6]
    bank_table.add_row(row[0], row[1], row[2], row[3], row[4], row[5])

layout["Bank_Data"].update(bank_table)

console.print(layout)
