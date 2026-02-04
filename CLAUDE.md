# CLAUDE.md - Python_Panel

## Project Overview

Terminal-based dashboard displaying real-time weather forecasts and bank transaction summaries. Built with Rich library for interactive CLI UI.

**Architecture**: Client application that connects to centralized API Gateway for all weather and location data.

## Structure

```
├── main.py                     # Entry point wrapper
├── app/
│   ├── main.py                 # Core app logic
│   ├── config.py               # Config loader (config.json)
│   ├── banking.py              # CSV parser for bank statements
│   ├── weather.py              # WeatherService (gateway integration)
│   ├── location.py             # LocationService (gateway + WinRT GPS)
│   ├── paths.py                # Directory configuration
│   └── ui/
│       ├── layout.py           # Rich UI layout builder
│       ├── theme.py            # Terminal themes
│       └── utils.py            # UI utilities
├── requirements/
│   ├── apikey.py               # Gateway credentials (gitignored)
│   ├── apikey_Def.py           # Template for API keys
│   ├── gateway.py              # Gateway client (JWT auth + API methods)
│   └── config.json             # User settings (theme, refresh rate, units)
└── 02_Bankauszüge/             # Bank CSV statements (gitignored)
```

## API Gateway Integration

All external APIs (OpenWeather, Geoapify, IPRegistry) are accessed through the centralized API Gateway at `https://api.novaroma-homelab.uk`.

### Gateway Client (`requirements/gateway.py`)

**Authentication**:
- JWT Bearer token authentication
- Automatic token refresh (tokens expire after 1 hour, refresh at 55 minutes)
- Credentials stored in `requirements/apikey.py` (gitignored)

**Available Methods**:
- `get_hourly_forecast(lat, lon, units)` - 48-hour hourly forecast
- `get_daily_forecast(lat, lon, days, units)` - Multi-day forecast
- `geocode(city)` - Convert city name to coordinates
- `get_location_from_ip(ip)` - Get location from IP address
- `send_email(to, subject, html, from_email)` - Send emails via Resend
- `list_software()` - List all registered software with health
- `get_software(name)` - Health for one software (includes `stale` flag)
- `push_software_heartbeat(name, health, details)` - Push heartbeat (`health`: ok/warning/error)
- `list_hardware()` - List all registered hardware with health + config
- `get_hardware(name)` - Health + config for one device (includes `stale` flag)
- `push_hardware_heartbeat(name, health, config, details)` - Push heartbeat with optional config

### Services Using Gateway

**WeatherService** (`app/weather.py`):
- `fetch_hourly()` → `gateway.get_hourly_forecast()`
- `fetch_weekly()` → `gateway.get_daily_forecast()`
- Returns: temps, weather icons, wind speed, timestamps

**LocationService** (`app/location.py`):
- Location detection fallback chain: WinRT GPS → IPRegistry → Geoapify
- `_detect_city_from_ip()` → `gateway.get_location_from_ip()`
- `_geocode_city()` → `gateway.geocode()`

## Configuration & Security

### Credentials File (`requirements/apikey.py`)

**CRITICAL: This file is gitignored and contains sensitive data!**

```python
# API Gateway Configuration (centralized API access)
GATEWAY_URL = "https://api.novaroma-homelab.uk"
GATEWAY_USERNAME = "..."
GATEWAY_PASSWORD = "..."

# Email configuration (for gateway send_email calls)
email = "Cmd@api.novaroma-homelab.uk"
```

### User Settings (`requirements/config.json`)

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

### Protected Files (.gitignore)

**Never commit these files:**
- `/requirements/apikey.py` - Gateway credentials
- `/requirements/config.json` - May contain sensitive settings
- `/02_Bankauszüge/*` - Bank statements

## Data Flow

```
main.py → app/main.py
    ├── LocationService → (WinRT GPS or gateway.get_location_from_ip()) → gateway.geocode()
    ├── WeatherService → gateway.get_hourly_forecast() + gateway.get_daily_forecast()
    └── Banking → Local CSV parsing
    ↓
UI Rendering (Rich) → Terminal Dashboard
```

## Security Benefits of Gateway

1. **No API Keys in Client Code**: All external API keys stored server-side only
2. **Centralized Authentication**: Single username/password for all services
3. **Token-Based Security**: JWT tokens with automatic refresh and expiration
4. **Credential Isolation**: Only gateway credentials in client code, external API keys never exposed

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
python main.py
```

## Testing

Test gateway connectivity:
```bash
python -c "from requirements.gateway import GatewayClient; from requirements import apikey; g = GatewayClient(apikey.GATEWAY_URL, apikey.GATEWAY_USERNAME, apikey.GATEWAY_PASSWORD); print(g.get_hourly_forecast(51.5074, -0.1278))"
```

## Common Tasks

### Change Theme
Edit `requirements/config.json` → `"theme": "..."` (autumn, sunrise, midnight, ocean, desert)

### Adjust Refresh Rate
Edit `requirements/config.json` → `"refresh_minutes": 10`

### Update Gateway Credentials
1. Edit `requirements/apikey.py`
2. Update `GATEWAY_USERNAME` or `GATEWAY_PASSWORD`
3. Do NOT commit this file!
