# CLAUDE.md - Python_Panel

## Project Overview

Terminal-based dashboard displaying real-time weather forecasts and bank transaction summaries. Built with Rich library for interactive CLI UI.

## Structure

```
├── main.py                     # Entry point wrapper
├── app/
│   ├── main.py                 # Core app logic
│   ├── config.py               # Config loader (config.json)
│   ├── banking.py              # CSV parser for bank statements
│   ├── weather.py              # WeatherService (OpenWeather integration)
│   ├── location.py             # LocationService (Geoapify + IPRegistry + WinRT GPS)
│   ├── paths.py                # Directory configuration
│   └── ui/
│       ├── layout.py           # Rich UI layout builder
│       ├── theme.py            # Terminal themes
│       └── utils.py            # UI utilities
├── requirements/
│   ├── apikey.py               # API credentials (gitignored)
│   ├── apikey_Def.py           # Template for API keys
│   └── config.json             # User settings (theme, refresh rate, units)
└── 02_Bankauszüge/             # Bank CSV statements (gitignored)
```

## APIs Used

| API | Used In | Purpose | Endpoint | Key Variable |
|-----|---------|---------|----------|--------------|
| **OpenWeather Hourly** | app/weather.py | Hourly forecast | `/data/2.5/forecast/hourly` | `api_key_weather` |
| **OpenWeather Daily** | app/weather.py | 7-day forecast | `/data/2.5/forecast/daily` | `api_key_weather` |
| **Geoapify** | app/location.py | Geocoding | `/v1/geocode/search` | `api_key_geo` |
| **IPRegistry** | app/location.py | IP geolocation | `https://api.ipregistry.co` | `api_key_getcity` |
| **Windows WinRT** | app/location.py | GPS coordinates | Native OS API | N/A |

## Current API Implementation

**WeatherService** (`app/weather.py:30-75`):
- `get_hourly_forecast()` → `https://pro.openweathermap.org/data/2.5/forecast/hourly`
- `get_weekly_forecast()` → `https://api.openweathermap.org/data/2.5/forecast/daily`
- Returns: temps, weather icons, wind speed, timestamps

**LocationService** (`app/location.py:25-95`):
- Fallback chain: WinRT GPS → IPRegistry → Geoapify
- `get_city_from_ip()` → IPRegistry API
- `get_coordinates(city)` → Geoapify geocoding API

## Configuration

**API Keys** (`requirements/apikey.py`):
```python
api_key_geo = "cada2c690e8b49beb6855eec51e50dad"         # Geoapify
api_key_weather = "58551f2566c10111a157c2223437a461"     # OpenWeather
api_key_getcity = "ira_6HVa1fY8zDOB0dVhKih0MZD3NZ0JTO1rzDKO"  # IPRegistry
```

**User Settings** (`requirements/config.json`):
```json
{
  "theme": "autumn",
  "refresh_minutes": 10,
  "units": "metric",
  "use_winrt_location": true,
  "live_screen": true,
  "bank_rows": 2,
  "max_hourly_forecast": 12,
  "max_weekly_forecast": 7
}
```

## Data Flow

```
main.py → app/main.py
    ├── LocationService → (WinRT GPS or IPRegistry) → Geoapify
    ├── WeatherService → OpenWeather API (hourly + daily)
    └── Banking → Local CSV parsing
    ↓
UI Rendering (Rich) → Terminal Dashboard
```

## Migration to API Gateway

**Target**: Use centralized API gateway at `https://api.novaroma-homelab.uk`

**Benefits**:
- No API keys in client code
- JWT-based authentication
- Centralized key management
- Better security

**Required Changes**:
1. Add authentication module (JWT tokens)
2. Replace WeatherService API calls with gateway endpoints
3. Replace LocationService API calls with gateway endpoints
4. Add hourly/daily forecast endpoints to gateway
5. Add IPRegistry proxy to gateway
