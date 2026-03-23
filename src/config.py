import os
from pathlib import Path

from dotenv import load_dotenv


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Load environment variables from .env file
load_dotenv()

# Load env config
IN_FILE = Path(os.getenv("DATA_IN", r"data/Merian-Kept-Hierarchy-Combined.xlsx"))
_derived_out = Path(IN_FILE).with_name(f"{Path(IN_FILE).stem}_PI_Builder{Path(IN_FILE).suffix}")
OUT_FILE = Path(os.getenv("DATA_OUT", str(_derived_out)))
JSON_FILE = Path(os.getenv("JSON_FILE", r"data/merian_hierarchy.json"))

# Constants path used in the app
LOGS_DIR = Path(os.getenv("LOGS_DIR", "logs"))
LOGS_FILE = Path(os.getenv("LOGS_FILE", str(LOGS_DIR / "app.log")))

# Hierarchy root definition
ROOT_KEY = "3007"
ROOT_NAME = "Merian Gold Mines"

# config related to Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = _as_bool(os.getenv("LOG_TO_FILE", "true"))
LOG_TO_CONSOL = _as_bool(os.getenv("LOG_TO_CONSOLE", "true"))
