from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BANK_DIR = PROJECT_ROOT / "02_Bankauszüge"
CONFIG_DIR = PROJECT_ROOT / "requirements"
LOG_DIR = PROJECT_ROOT / "logs"
CONFIG_PATH = CONFIG_DIR / "config.json"