from pathlib import Path
from typing import Optional

import openpyxl
import pandas as pd

from src.logger import logger


class ExcelManager:
    def __init__(self, excel_path: Optional[Path] = None) -> None:
        self.excel_path = excel_path

    def _read_excel_file(self, path, sheet_name=None):
        # return openpyxl.load_workbook(path, read_only=True, data_only=True)
        return pd.read_excel(path, sheet_name=sheet_name)

    def create_dict(self):
        hierarchy_dict = {"3007": "Merian Gold Mines"}
        target_columns = ["Standardized Description", "Functional Loc."]

        df = self._read_excel_file(self.excel_path)
        for sheet_name, df in df.items():
            logger.info(f"Processing sheet: {sheet_name}")

            # Validate columns
            for col in target_columns:
                if col not in df.columns:
                    logger.error(f"Missing required columns in the Excel file. Required columns: {target_columns}")
                    raise ValueError(f"Missing column: {col}")

            for _, row in df.iterrows():
                standardized_desc = row["Standardized Description"].strip()
                functional_loc = row["Functional Loc."]

                if pd.isna(standardized_desc) or pd.isna(functional_loc):
                    logger.warning(f"Skipping row with missing data: {row}")
                    continue

                hierarchy_dict[functional_loc] = standardized_desc

        return hierarchy_dict

    def export_to_pibuilder_part(self):
        pass

    def export_to_pibuilder_all(self):
        pass
