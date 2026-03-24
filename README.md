# <div align="center">Merian Hierarchy PI Builder Automator</div>

## Introduction
- **What it does:** Converts the Merian Gold Mines source hierarchy Excel into a PI Builder-ready workbook while tracking every element in a JSON source of truth.
- **How it works:** Each run reads the Excel file, injects the mandatory root (`3007 → Merian Gold Mines`), compares the result with the stored JSON, and writes a PI Builder sheet that marks only new or renamed elements with `x`.
- **How the application behaves:** Parents always come before children, only changed rows are selected, and re-running safely updates the JSON plus Excel output without duplicating existing data.
- **First-run behaviour:** If the JSON snapshot is missing, the script auto-creates it, treats every element as “new,” and marks the root row (`Selected(x) = x`) so PI Builder can build the entire hierarchy from scratch.
- **Default behaviour:** Uses the settings from `.env` when present (otherwise the built-in defaults under `data/`), writes logs to `./logs/app.log`, and stops immediately if it can’t read/write any required file.

## Setup and Usage
0. **Get the code:**
   ```powershell
   git clone https://github.com/viru185/auto_merian_hierarchy.git
   cd auto_merian_hierarchy
   ```
1. **Install uv** (Python package/dependency manager):
   ```powershell
   pip install uv
   ```
2. **Install project dependencies** (creates/updates the virtual environment):
   ```powershell
   uv sync
   ```
3. **(Optional) Configure the environment file:**
   - Copy `.env.example` to `.env` **only if you want to override the defaults**.
   - Update any paths or logging settings you care about (see table below). If you skip this step, the script uses its built-in defaults.
4. **Run the automation:**
   ```powershell
   uv run python main.py
   ```

### `.env` Variables (optional overrides)
| Variable | Purpose |
| --- | --- |
| `DATA_IN` | Source Excel file containing `Functional Loc.` and `Standardized Description`. |
| `DATA_OUT` | Target PI Builder workbook path (defaults beside the input file). |
| `JSON_FILE` | JSON file storing the last synced hierarchy for delta detection. |
| `FUNCTIONAL_LOC_COLUMN` / `DESCRIPTION_COLUMN` | Override the Excel headers for the hierarchy key/description columns if the source workbook changes (defaults to `Functional Loc.` / `Standardized Description`). |
| `LOGS_DIR` / `LOGS_FILE` | Where log files live (defaults to `logs/app.log`). |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, etc.). |
| `LOG_TO_FILE` / `LOG_TO_CONSOLE` | Enable/disable file or console logging (`true`/`false`). |

## Commands and Examples
| Command | Description | Example |
| --- | --- | --- |
| `uv run python main.py` | Run with default paths defined in `.env`. | `uv run python main.py` |
| `uv run python main.py --file <path>` | Use a different Excel source file. | `uv run python main.py --file data/new-hierarchy.xlsx` |
| `uv run python main.py --json <path>` | Point to a different JSON snapshot file. | `uv run python main.py --json backups/merian.json` |
| `uv run python main.py --output <path>` | Choose a custom PI Builder output (file or directory). | `uv run python main.py --output output/Merian_PI.xlsx` |
| `uv run python main.py --all` | Mark *every* element with `x` (full rebuild). | `uv run python main.py --all` |
| `uv run python main.py --debug` | Enable verbose debug logs on the console. | `uv run python main.py --debug` |

> **Tip:** The script checks that every file or folder you reference can be read or written before it starts. If something is missing or locked, it exits with a clear error so you can fix the path or permissions.
