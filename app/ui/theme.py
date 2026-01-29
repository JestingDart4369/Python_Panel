# =========================
# Imports
# =========================
from rich.theme import Theme
# =========================
# Styling / Themes
# =========================
STYLES = {
"forest_dark": Theme({
    # App
    "divider": "#5A6B4E",
    "app.title": "#7FA36B",
    "app.subtitle": "#E6EBD9",

    # Statusbar
    "statusbart.text": "#7FA36B",
    "statusbart.City": "#E6EBD9",
    "statusbart.Time": "#AFC8A0",

    # Parts
    "label": "#E6EBD9",

    # Tables
    "table.header": "#6FA3A6",
    "table.title": "#9EDFE3",
    "table.border": "#2E4A3B",

    "title": "#9EDFE3",

    # App.Weather
    "app.weather.data": "#E6EBD9",
    "app.weather.title": "#7FA36B",

    # App.Banking
    "app.money.good": "bold #7FD37F",
    "app.money.bad": "bold #D37F7F",
    "app.money.neutral": "bold #E6EBD9",
    "app.money.title": "#7FA36B",

    # App.Banking.Table
    "app.money.table.columHeader": "#9FB89A",
    "app.money.table.title": "#7FA36B",
    "app.money.table.border": "#AFC8A0",
    "app.money.table.row": "#E6EBD9",
}),
"forest": Theme({
        #App
        "divider": "#89986D",
        "app.title": "#89986D",
        "app.subtitle": "#F6F0D7",
        #statusbar
        "statusbart.text": "#89986D",
        "statusbart.City": "#F6F0D7",
        "statusbart.Time": "#C5D89D",
        #Parts
        "label": "#F6F0D7",
        #Tables
        "table.header": "#158EA6",
        "table.title": "#29DFFF",
        "table.border": "#003D4D",

        "title": "#29DFFF",
        #App.Weather
        "app.weather.data": "#F6F0D7",
        "app.weather.title": "#89986D",
        #App.Banking
        "app.money.good": "bold bright_green",
        "app.money.bad": "bold bright_red",
        "app.money.neutral": "bold bright_white",
        "app.money.title": "#89986D",
        #App.Banking.Table
        "app.money.table.columHeader": "#9CAB84",
        "app.money.table.title": "#89986D",
        "app.money.table.border": "#C5D89D",
        "app.money.table.row": "#F6F0D7",
    }),
"autumn": Theme({
    # App
    "divider": "#B36A2E",
    "app.title": "#D9822B",
    "app.subtitle": "#F5E6D3",

    # Statusbar
    "statusbart.text": "#D9822B",
    "statusbart.City": "#F5E6D3",
    "statusbart.Time": "#E8B97E",

    # Parts
    "label": "#F5E6D3",

    # Tables
    "table.header": "#C45B3C",
    "table.title": "#FFB86C",
    "table.border": "#5A2E1B",

    "title": "#FFB86C",

    # App.Weather
    "app.weather.data": "#F5E6D3",
    "app.weather.title": "#D9822B",

    # App.Banking
    "app.money.good": "bold #9BD18B",
    "app.money.bad": "bold #E06C75",
    "app.money.neutral": "bold #F5E6D3",
    "app.money.title": "#D9822B",

    # App.Banking.Table
    "app.money.table.columHeader": "#E0A96D",
    "app.money.table.title": "#D9822B",
    "app.money.table.border": "#E8B97E",
    "app.money.table.row": "#F5E6D3",
})
,
"glacier": Theme({
    # App
    "divider": "#7AA2C3",
    "app.title": "#9FD3FF",
    "app.subtitle": "#EAF4FF",

    # Statusbar
    "statusbart.text": "#9FD3FF",
    "statusbart.City": "#EAF4FF",
    "statusbart.Time": "#C5E4FF",

    # Parts
    "label": "#EAF4FF",

    # Tables
    "table.header": "#5DA9E9",
    "table.title": "#BEE9FF",
    "table.border": "#2F4A63",

    "title": "#BEE9FF",

    # App.Weather
    "app.weather.data": "#EAF4FF",
    "app.weather.title": "#9FD3FF",

    # App.Banking
    "app.money.good": "bold #6FCF97",
    "app.money.bad": "bold #EB5757",
    "app.money.neutral": "bold #EAF4FF",
    "app.money.title": "#9FD3FF",

    # App.Banking.Table
    "app.money.table.columHeader": "#9CCEF2",
    "app.money.table.title": "#9FD3FF",
    "app.money.table.border": "#C5E4FF",
    "app.money.table.row": "#EAF4FF",
})
,
"midnight_olive": Theme({
    # App
    "divider": "#6B7C5A",
    "app.title": "#A8C686",
    "app.subtitle": "#E2EBD7",

    # Statusbar
    "statusbart.text": "#A8C686",
    "statusbart.City": "#E2EBD7",
    "statusbart.Time": "#C6D9AF",

    # Parts
    "label": "#E2EBD7",

    # Tables
    "table.header": "#8FB996",
    "table.title": "#BEEAC4",
    "table.border": "#394A3D",

    "title": "#BEEAC4",

    # App.Weather
    "app.weather.data": "#E2EBD7",
    "app.weather.title": "#A8C686",

    # App.Banking
    "app.money.good": "bold #9FE0A1",
    "app.money.bad": "bold #E07A7A",
    "app.money.neutral": "bold #E2EBD7",
    "app.money.title": "#A8C686",

    # App.Banking.Table
    "app.money.table.columHeader": "#AFC8A0",
    "app.money.table.title": "#A8C686",
    "app.money.table.border": "#C6D9AF",
    "app.money.table.row": "#E2EBD7",
})
,
"ocean_depths": Theme({
    # App
    "divider": "#2E6B7A",
    "app.title": "#5FBCD3",
    "app.subtitle": "#E0F4F7",

    # Statusbar
    "statusbart.text": "#5FBCD3",
    "statusbart.City": "#E0F4F7",
    "statusbart.Time": "#8DD3E0",

    # Parts
    "label": "#E0F4F7",

    # Tables
    "table.header": "#3A9DBF",
    "table.title": "#7FE0F0",
    "table.border": "#1A4A5A",

    "title": "#7FE0F0",

    # App.Weather
    "app.weather.data": "#E0F4F7",
    "app.weather.title": "#5FBCD3",

    # App.Banking
    "app.money.good": "bold #6FDBA0",
    "app.money.bad": "bold #E8736F",
    "app.money.neutral": "bold #E0F4F7",
    "app.money.title": "#5FBCD3",

    # App.Banking.Table
    "app.money.table.columHeader": "#7AC4D4",
    "app.money.table.title": "#5FBCD3",
    "app.money.table.border": "#8DD3E0",
    "app.money.table.row": "#E0F4F7",
})
,
"lavender_dusk": Theme({
    # App
    "divider": "#7B6B8A",
    "app.title": "#B89FD4",
    "app.subtitle": "#F0E8F5",

    # Statusbar
    "statusbart.text": "#B89FD4",
    "statusbart.City": "#F0E8F5",
    "statusbart.Time": "#D4C4E8",

    # Parts
    "label": "#F0E8F5",

    # Tables
    "table.header": "#9A7FBF",
    "table.title": "#D9C4F0",
    "table.border": "#4A3D5A",

    "title": "#D9C4F0",

    # App.Weather
    "app.weather.data": "#F0E8F5",
    "app.weather.title": "#B89FD4",

    # App.Banking
    "app.money.good": "bold #8FD9A0",
    "app.money.bad": "bold #E08A8A",
    "app.money.neutral": "bold #F0E8F5",
    "app.money.title": "#B89FD4",

    # App.Banking.Table
    "app.money.table.columHeader": "#C4B0DC",
    "app.money.table.title": "#B89FD4",
    "app.money.table.border": "#D4C4E8",
    "app.money.table.row": "#F0E8F5",
})
,
"desert_sunset": Theme({
    # App
    "divider": "#B8865A",
    "app.title": "#E8A862",
    "app.subtitle": "#FDF4E8",

    # Statusbar
    "statusbart.text": "#E8A862",
    "statusbart.City": "#FDF4E8",
    "statusbart.Time": "#F0C89A",

    # Parts
    "label": "#FDF4E8",

    # Tables
    "table.header": "#D4724A",
    "table.title": "#FFD4A8",
    "table.border": "#6B4A32",

    "title": "#FFD4A8",

    # App.Weather
    "app.weather.data": "#FDF4E8",
    "app.weather.title": "#E8A862",

    # App.Banking
    "app.money.good": "bold #8FD9A0",
    "app.money.bad": "bold #E87070",
    "app.money.neutral": "bold #FDF4E8",
    "app.money.title": "#E8A862",

    # App.Banking.Table
    "app.money.table.columHeader": "#E8BC7A",
    "app.money.table.title": "#E8A862",
    "app.money.table.border": "#F0C89A",
    "app.money.table.row": "#FDF4E8",
})
,
}
