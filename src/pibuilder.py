from pathlib import Path
from typing import Dict

import pandas as pd

from src.config import ROOT_KEY
from src.json_manager import DiffResult
from src.logger import logger

PI_BUILDER_COLUMNS = [
    "Selected(x)",
    "Parent",
    "Name",
    "ObjectType",
    "Error",
    "Description",
    "NewName",
]


def _key_depth(key: str) -> int:
    return key.count("-")


def _parent_path(key: str, hierarchy: Dict[str, str]) -> str:
    segments = key.split("-")
    if len(segments) == 1:
        return ""

    parent_keys = ["-".join(segments[:idx]) for idx in range(1, len(segments))]
    parent_names = []
    for parent_key in parent_keys:
        if parent_key not in hierarchy:
            raise ValueError(
                f"Parent key '{parent_key}' required to build the hierarchy path for '{key}' is missing."
            )
        parent_names.append(hierarchy[parent_key])

    return "\\".join(parent_names)


def _sort_keys_for_export(hierarchy: Dict[str, str]):
    def sort_key(key: str):
        if key == ROOT_KEY:
            return (-1, key)
        return (_key_depth(key), key)

    return sorted(hierarchy.keys(), key=sort_key)


def build_pibuilder_dataframe(hierarchy: Dict[str, str], diff: DiffResult, mark_all: bool = False) -> pd.DataFrame:
    rows = []
    sorted_keys = _sort_keys_for_export(hierarchy)
    logger.debug(
        f"Building PI Builder DataFrame for {len(sorted_keys)} elements | "
        f"mark_all={mark_all} | new={len(diff.new_elements)} | renamed={len(diff.renamed_elements)}."
    )

    for key in sorted_keys:
        name = hierarchy[key]
        new_name_value = ""

        if key in diff.renamed_elements:
            old_name, new_name = diff.renamed_elements[key]
            name = old_name
            new_name_value = new_name

        selected = "x" if mark_all or key in diff.new_elements or key in diff.renamed_elements else ""

        rows.append(
            {
                "Selected(x)": selected,
                "Parent": _parent_path(key, hierarchy),
                "Name": name,
                "ObjectType": "Element",
                "Error": "",
                "Description": key,
                "NewName": new_name_value,
            }
        )

    return pd.DataFrame(rows, columns=PI_BUILDER_COLUMNS)


def export_to_excel(df: pd.DataFrame, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Exporting PI Builder DataFrame with {len(df)} rows to '{output_path}'.")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="PI Builder", index=False)

        worksheet = writer.sheets["PI Builder"]
        for idx, column in enumerate(df.columns, start=1):
            max_length = max((len(str(value)) for value in df[column]), default=0)
            header_length = len(column)
            adjusted_width = min(max(max_length, header_length) + 2, 80)
            worksheet.column_dimensions[chr(64 + idx)].width = adjusted_width
        logger.debug("Auto-adjusted PI Builder column widths based on data.")

    return output_path
