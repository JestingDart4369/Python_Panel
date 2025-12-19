# 📊 Terminal Dashboard – Weather & Banking Overview

A **Python-based terminal dashboard** built with **Rich**, combining real-time **weather forecasts** and **bank transaction summaries** in a single, stylish interface.

The application features a **theme system with live previews**, location-based weather data using external APIs, and automatic parsing of local bank CSV statements to calculate **expenses, income, and account balance** — all rendered in a structured and readable terminal layout.

---

## ✨ Features

### 🌦 Weather
- Hourly weather forecast by city name
- Weekly weather forecast
- Weather icons and descriptions
- Wind speed and temperature display

### 🗺 Location
- Automatic geolocation using **Geoapify**
- City-to-coordinate resolution

### 🎨 Themes
- Multiple terminal themes with live preview:
  - Classic
  - Midnight
  - Forest
  - Sunset
  - High Contrast

### 💰 Banking
- Banking overview from CSV files
- Automatic loading of the latest CSV file
- Calculates:
  - Total spent
  - Total received
  - Current account balance
- Transaction table rendered with **Rich**

---

## 🛠 Technologies Used

- **Python 3**
- **Rich** (layout, tables, themes)
- **OpenWeather API**
- **Geoapify API**
- **Requests**
- **PyFiglet**

---

## 📂 Folder Structure

02_Bankauszüge/ # Bank CSV statements (latest file auto-loaded)
requirements/ # API key management
dashboard.py # Main application logic

yaml
Code kopieren

---

## 🚀 Usage

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
Insert your API keys for:
Geoapify
OpenWeather

Place your bank CSV files into 02_Bankauszüge/

An example.csv with fake data is included for testing

Run the script:
bash
Code kopieren
python dashboard.py
Choose a theme and enter a city name
---
## 🔒 Security & Privacy Notice
example.csv contains fake demo data

Do not commit real bank statements or API keys

API keys should be stored locally and ignored via .gitignore
---
## ⚠️ Disclaimer
This project is intended for educational and local use only.
It is not suitable for production environments or handling sensitive financial data without additional security measures.
