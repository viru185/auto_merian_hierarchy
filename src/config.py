import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load env config
IN_FILE = Path(os.getenv("DATA_IN", r"data/Merian-Kept-Hierarchy-Combined.xlsx"))
_outfile_calc = IN_FILE.stem + "_PI_Builder" + IN_FILE.suffix
OUT_FILE = Path(os.getenv("DATA_OUT", _outfile_calc))
JSON_FILE = Path(os.getenv("JSON_FILE", r"data/merian_hierarchy.json"))

# Constants path used in the app
LOGS_FILE = Path("logs/app.log")
LOGS_DIR = Path("logs")

# Hierarchy root definition
ROOT_KEY = "3007"
ROOT_NAME = "Merian Gold Mines"

# config related to Logging
LOG_LEVEL = "DEBUG"
LOG_TO_FILE = True
LOG_TO_CONSOL = True
