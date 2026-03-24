from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import DESCRIPTION_COLUMN, FUNCTIONAL_LOC_COLUMN, ROOT_KEY, ROOT_NAME
from src.logger import logger


class ExcelManager:
    def __init__(
        self,
        excel_path: Optional[Path] = None,
        functional_column: str = FUNCTIONAL_LOC_COLUMN,
        description_column: str = DESCRIPTION_COLUMN,
    ) -> None:
        self.excel_path = Path(excel_path) if excel_path else None
        self._dataframe: Optional[pd.DataFrame] = None
        self.functional_column = functional_column
        self.description_column = description_column
        self._required_columns = (self.functional_column, self.description_column)
        logger.debug(
            f"ExcelManager initialized for path '{self.excel_path}' "
            f"(functional column='{self.functional_column}', description column='{self.description_column}')."
        )

    def _read_excel_file(self, path, sheet_name=None):
        return pd.read_excel(path, sheet_name=sheet_name, dtype=str)

    def load_records(self) -> pd.DataFrame:
        """Read and validate the source Excel workbook, returning a clean DataFrame."""

        if self._dataframe is not None:
            logger.debug(
                f"Returning cached hierarchy DataFrame with {len(self._dataframe)} rows for '{self.excel_path}'."
            )
            return self._dataframe.copy()

        if not self.excel_path:
            raise ValueError("Excel path is not set.")

        logger.debug(f"Reading hierarchy workbook from '{self.excel_path}'.")
        workbook = self._read_excel_file(self.excel_path, sheet_name=None)
        if isinstance(workbook, pd.DataFrame):
            workbook = {"Sheet1": workbook}
        logger.debug(f"Workbook contains {len(workbook)} sheet(s).")

        frames = []
        for sheet_name, raw_df in workbook.items():
            logger.info(f"Processing sheet: {sheet_name}")

            missing = [col for col in self._required_columns if col not in raw_df.columns]
            if missing:
                raise ValueError(f"Missing required columns in sheet '{sheet_name}': {', '.join(missing)}.")

            df = raw_df.loc[:, self._required_columns].copy()
            df = df.dropna(subset=self._required_columns, how="any") # type: ignore

            for col in self._required_columns:
                df[col] = df[col].astype(str).str.strip()

            df[self.functional_column] = df[self.functional_column].str.replace(r"\.0+$", "", regex=True)
            df = df[(df[self.functional_column] != "") & (df[self.description_column] != "")]

            if df.empty:
                logger.warning(f"Sheet '{sheet_name}' has no valid hierarchy rows. Skipping.")
                continue

            logger.debug(f"Sheet '{sheet_name}': {len(raw_df)} raw rows -> {len(df)} cleaned rows.")
            frames.append(df)

        if not frames:
            raise ValueError("No valid hierarchy data found in the provided Excel workbook.")

        combined = pd.concat(frames, ignore_index=True)
        logger.debug(f"Combined cleaned DataFrame has {len(combined)} rows.")

        duplicated = combined.duplicated(subset=self.functional_column, keep=False)
        if duplicated.any():
            dup_values = sorted(combined.loc[duplicated, self.functional_column].unique())
            raise ValueError(
                f"Duplicate {self.functional_column} values detected. Each value must be unique. "
                f"Duplicates: {', '.join(dup_values)}"
            )

        logger.debug(f"No duplicate {self.functional_column} values detected.")
        self._dataframe = combined
        return combined.copy()

    def _ensure_parent_chain(self, keys: set) -> None:
        for key in keys:
            if key == ROOT_KEY:
                continue

            if "-" not in key:
                raise ValueError(
                    f"Functional Loc. '{key}' is missing '-' segments and cannot link to root '{ROOT_KEY}'."
                )

            parent_key = "-".join(key.split("-")[:-1])
            if parent_key not in keys:
                raise ValueError(
                    f"Missing parent '{parent_key}' required for Functional Loc. '{key}'. "
                    "Ensure every element has a complete chain back to the root."
                )

    def create_dict(self):
        df = self.load_records()
        excel_dict = dict(zip(df[self.functional_column], df[self.description_column]))
        logger.debug(
            f"Excel provided {len(excel_dict)} unique {self.functional_column} entries before injecting root."
        )

        # Enforce canonical root definition regardless of Excel contents
        excel_dict.pop(ROOT_KEY, None)
        hierarchy_dict = {ROOT_KEY: ROOT_NAME, **excel_dict}

        self._ensure_parent_chain(set(hierarchy_dict.keys()))
        logger.debug(f"Parent chain validated for {len(hierarchy_dict)} hierarchy nodes.")
        logger.info(f"Loaded {len(hierarchy_dict)} hierarchy records (including root).")
        return hierarchy_dict
