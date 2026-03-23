import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.config import ROOT_KEY, ROOT_NAME
from src.logger import logger


@dataclass
class DiffResult:
    previous: Dict[str, str]
    latest: Dict[str, str]
    new_elements: Dict[str, str]
    renamed_elements: Dict[str, Tuple[str, str]]
    removed_elements: Dict[str, str]

    @property
    def has_changes(self) -> bool:
        return bool(self.new_elements or self.renamed_elements or self.removed_elements)


class JsonManager:
    def __init__(self, json_file) -> None:
        self.json_file = Path(json_file) if json_file else None
        self._root_missing_on_load = False
        self._root_name_mismatch: Optional[str] = None
        logger.debug(f"JsonManager initialized with path '{self.json_file}'.")

    def _reset_root_state(self) -> None:
        self._root_missing_on_load = False
        self._root_name_mismatch = None
        logger.debug("Reset root tracking state for JSON comparison.")

    def load_json(self) -> Dict[str, str]:
        self._reset_root_state()

        if not self.json_file or not self.json_file.exists():
            logger.info(f"No existing hierarchy JSON found. Treating all elements as new.")
            self._root_missing_on_load = True
            return {}

        logger.debug(f"Loading hierarchy JSON from '{self.json_file}'.")
        with open(self.json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Failed to parse JSON file '{self.json_file}': {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError("Hierarchy JSON must be an object mapping Functional Loc. to names.")

        data = {str(key): str(value) for key, value in data.items()}
        logger.debug(f"Loaded {len(data)} entries from hierarchy JSON.")

        if ROOT_KEY not in data:
            self._root_missing_on_load = True
            logger.warning(
                f"Root Functional Loc. '{ROOT_KEY}' missing from hierarchy JSON. It will be injected and marked as new."
            )
        elif data[ROOT_KEY] != ROOT_NAME:
            self._root_name_mismatch = data[ROOT_KEY]
            logger.warning(
                f"Root Functional Loc. '{ROOT_KEY}' has name '{data[ROOT_KEY]}'. Overriding with canonical '{ROOT_NAME}'."
            )

        return data

    def save_to_json(self, data):
        if not self.json_file:
            raise ValueError("JSON file path is not configured.")

        canonical = dict(data)
        canonical[ROOT_KEY] = ROOT_NAME
        logger.debug(f"Persisting hierarchy JSON with {len(canonical)} entries to '{self.json_file}'.")

        self.json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(canonical, f, indent=4, sort_keys=True)
        logger.info(f"Hierarchy JSON updated: {self.json_file}")

    def compare_and_update(self, latest_data: Dict[str, str]) -> DiffResult:
        logger.debug("Starting comparison between Excel hierarchy and stored JSON.")
        previous = self.load_json()

        latest_data = dict(latest_data)
        latest_data[ROOT_KEY] = ROOT_NAME
        logger.debug(f"Latest hierarchy contains {len(latest_data)} entries (root enforced).")

        new_elements = {key: latest_data[key] for key in latest_data.keys() - previous.keys()}
        removed_elements = {key: previous[key] for key in previous.keys() - latest_data.keys()}

        renamed_elements = {}
        for key in latest_data.keys() & previous.keys():
            old_name = previous[key]
            new_name = latest_data[key]
            if old_name != new_name:
                renamed_elements[key] = (old_name, new_name)

        if self._root_missing_on_load:
            new_elements = {ROOT_KEY: ROOT_NAME, **new_elements}
        if self._root_name_mismatch:
            renamed_elements = {ROOT_KEY: (self._root_name_mismatch, ROOT_NAME), **renamed_elements}
        if ROOT_KEY in removed_elements:
            logger.error(f"Root element should never be removed. Re-inserting into latest hierarchy.")
            removed_elements.pop(ROOT_KEY, None)

        logger.debug(
            f"Diff summary -> new: {len(new_elements)}, renamed: {len(renamed_elements)}, "
            f"removed: {len(removed_elements)}."
        )

        diff = DiffResult(
            previous=previous,
            latest=latest_data,
            new_elements=new_elements,
            renamed_elements=renamed_elements,
            removed_elements=removed_elements,
        )

        if diff.has_changes:
            logger.debug("Changes detected; persisting updated hierarchy JSON.")
            self.save_to_json(latest_data)
        else:
            logger.info(f"No changes detected. JSON file left untouched.")

        return diff
