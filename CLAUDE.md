# CLAUDE.md - AI Assistant Guide for Python_Panel

This document provides comprehensive guidance for AI assistants working with the Python_Panel codebase.

## Project Overview

**Python_Panel** is a terminal dashboard application that displays real-time weather forecasts and banking transaction summaries in a styled terminal interface. Built with Python and the Rich library, it demonstrates clean separation of concerns and modular architecture.

### Key Features
- Real-time hourly and weekly weather forecasts via OpenWeather API
- Automatic location detection (WinRT on Windows, IP-based fallback)
- Banking overview from local CSV files with balance calculations
- Multiple terminal themes (forest_dark, forest, autumn, glacier, midnight_olive)
- Live screen refresh with configurable intervals

## Project Structure

```
Python_Panel/
├── app/                          # Main application package
│   ├── main.py                   # Entry point - orchestrates services and main loop
│   ├── config.py                 # Configuration loader with defaults
│   ├── paths.py                  # Path constants (BANK_DIR, CONFIG_DIR, LOG_DIR)
│   ├── weather.py                # WeatherService - OpenWeather API integration
│   ├── banking.py                # Banking class - CSV parsing and calculations
│   ├── location.py               # LocationService - geolocation handling
│   └── ui/                       # UI module
│       ├── layout.py             # Rich layout builder
│       ├── theme.py              # Theme definitions (Rich Theme objects)
│       └── utils.py              # UI helpers (forecast limits, text clamping)
├── requirements/                 # Configuration directory
│   ├── apikey_Def.py             # API key template (copy to apikey.py)
│   └── config.json               # User configuration
├── example.csv                   # Sample bank data for testing
├── requirements.txt              # Python dependencies
└── .github/ISSUE_TEMPLATE/       # GitHub issue templates
```

## Architecture & Data Flow

### Application Flow
1. **Startup**: Load config → Initialize services (Banking, Weather, Location)
2. **Main Loop**: Runs continuously with configurable refresh interval
3. **Each Cycle**:
   - Location service updates coordinates (WinRT or IP-based)
   - Weather service fetches hourly/weekly forecasts
   - Banking service parses latest CSV file
   - UI layout is built and rendered via Rich Live

### Core Services

| Service | File | Responsibility |
|---------|------|----------------|
| `Config` | `app/config.py` | Loads JSON config, provides defaults |
| `WeatherService` | `app/weather.py` | Fetches and formats weather data |
| `Banking` | `app/banking.py` | Parses CSV, calculates balance/spent/received |
| `LocationService` | `app/location.py` | Determines user location via multiple methods |

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys (copy template and fill in your keys)
cp requirements/apikey_Def.py requirements/apikey.py
# Edit requirements/apikey.py with your actual API keys

# Run the dashboard
python app/main.py
```

### Required API Keys
Configure in `requirements/apikey.py`:
- `api_key_weather`: OpenWeather API key (for hourly and daily forecasts)
- `api_key_getcity`: IPRegistry API key (for IP-based city detection)
- `api_key_geo`: Geoapify API key (for geocoding city names)

## Configuration

Configuration file: `requirements/config.json`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `theme` | string | `"autumn"` | UI theme (forest_dark, forest, autumn, glacier, midnight_olive) |
| `refresh_minutes` | int | `10` | Data refresh interval (min 10 seconds enforced) |
| `units` | string | `"metric"` | Temperature/wind units (metric or imperial) |
| `use_winrt_location` | bool | `true` | Enable Windows native geolocation |
| `live_screen` | bool | `true` | Enable Rich Live screen mode |
| `bank_rows` | int | `2` | Number of recent transactions to display (1-50) |
| `max_hourly_forecast` | int | `12` | Maximum hourly forecast rows |
| `max_weekly_forecast` | int | `7` | Maximum weekly forecast rows |

## Coding Conventions

### Python Style
- Use `from __future__ import annotations` for forward references
- Type hints are used throughout (e.g., `Path | None`, `tuple[float, float]`)
- Dataclasses for simple data containers (`@dataclass`)
- Custom exceptions inherit from `RuntimeError` (e.g., `WeatherError`, `LocationError`)

### Service Pattern
Services follow a consistent pattern:
```python
class ServiceName:
    def __init__(self, ...):
        # Initialize state attributes
        self.attribute = default_value

    def update(self, ...) -> None:
        # Refresh internal state from external source
        # Called from main loop
```

### UI/Rich Conventions
- Tables use `show_header=False, box=None` for minimal styling
- Styles reference theme keys like `"app.weather.data"`, `"app.money.good"`
- Layout uses Rich's `Layout.split_column()` and `Layout.split_row()`
- Text assembly uses `Text.assemble()` with style tuples

### Theme Style Keys
```
app.title, app.subtitle          # Main app styling
app.weather.title, app.weather.data
app.money.good, app.money.bad, app.money.neutral
app.money.table.*                # Banking table styles
statusbart.text, statusbart.City, statusbart.Time
table.header, table.title, table.border
divider, label, title
```

## Key Implementation Details

### Weather Service (`app/weather.py`)
- Uses OpenWeather Pro API for hourly forecasts
- Uses standard OpenWeather API for daily forecasts
- Weather icons mapped via `WEATHER_ICONS` dict (icon code -> emoji)
- Handles timezone conversion for local time display

### Banking Service (`app/banking.py`)
- Reads CSV files with `;` delimiter
- Supports multiple date formats: `DD.MM.YYYY`, `DD/MM/YYYY`, `YYYY-MM-DD`
- Automatically picks the most recent CSV file from the bank directory
- Calculates: total_spent, total_received, balance

### Location Service (`app/location.py`)
- Primary: WinRT geolocation (Windows only)
- Fallback: IPRegistry API -> Geoapify geocoding
- Handles async WinRT calls safely with event loop detection

## Testing

There is no formal test suite. For manual testing:
- Use `example.csv` for banking functionality testing
- The application handles missing directories by creating them on startup

## Security Considerations

### Protected Files (via .gitignore)
- `/requirements/apikey.py` - Real API keys (never commit)
- `/02_Bankauszüge/*` - Real bank data (never commit)
- `/Archive/` - Archived files

### Best Practices
- Use `requirements/apikey_Def.py` as a template only
- Test with `example.csv` containing fake data
- Never commit real financial data or API credentials

## Common Tasks

### Adding a New Theme
1. Edit `app/ui/theme.py`
2. Add a new entry to the `STYLES` dict
3. Define all required style keys (see existing themes for reference)

### Adding a New Configuration Option
1. Add default value to `DEFAULT_CONFIG` in `app/config.py`
2. Access via `config.data["option_name"]` in `app/main.py`
3. Update `requirements/config.json` with the new option

### Modifying the UI Layout
1. Edit `app/ui/layout.py`
2. The `build_layout()` function constructs the entire UI
3. Use Rich's Layout API for structural changes
4. Reference styles from themes via style key strings

### Adding a New API Integration
1. Create a new service class in `app/` directory
2. Follow the service pattern (init with config, update method)
3. Add API key placeholder to `requirements/apikey_Def.py`
4. Initialize and call from `app/main.py`

## Dependencies

Key libraries:
- **Rich** (14.2.0): Terminal UI, tables, layouts, themes, Live display
- **Requests** (2.32.5): HTTP requests for APIs
- **PyFiglet** (1.0.4): ASCII art text rendering for city names
- **winrt**: Windows Runtime for native geolocation (Windows only)

## Language Note

Some UI text and documentation is in German:
- Banking table headers (Buchung, Valuta, Belastung, Gutschrift, Saldo)
- CONTRIBUTING.md is written in German
- Error messages may be in German (e.g., "Keine CSV-Dateien gefunden!")

## File Naming

- Service classes: lowercase with underscores (`weather.py`, `location.py`)
- UI components: in `app/ui/` subdirectory
- Configuration: in `requirements/` directory
- Main entry point: `app/main.py`
