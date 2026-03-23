import sys
from pathlib import Path
from typing import Optional

import typer

from src.config import IN_FILE, JSON_FILE, OUT_FILE
from src.excel_manager import ExcelManager
from src.json_manager import JsonManager
from src.logger import logger
from src.pibuilder import build_pibuilder_dataframe, export_to_excel

app = typer.Typer(
    add_completion=False, no_args_is_help=False, help="Automate the Pi Builder Excel file of Merian Gold Mine excel file."
)


@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Option(
        IN_FILE, "--file", exists=True, file_okay=True, dir_okay=False, readable=True, help="Load input excel file."
    ),
    json_file: Optional[Path] = typer.Option(
        JSON_FILE,
        "--json",
        exists=False,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="will load the json file for the comparison or will choose defalut.",
    ),
    all_output: bool = typer.Option(False, "--all", help="give the whole pi builder excel file with all marked as X."),
    output: Optional[Path] = typer.Option(None, "--output", help="output location. file name is optional."),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug logging to stderr."),
):
    if debug:
        logger.add(sys.stderr, level="DEBUG", colorize=True)
        logger.debug(f"Debug mode enabled from CLI.")

    run(json_file=json_file, in_file=input_file, out_file=output, all_output=all_output)


def _resolve_output_path(custom_path: Optional[Path], input_path: Path) -> Path:
    config_path = Path(OUT_FILE)
    derived_suffix = config_path.suffix or input_path.suffix or ".xlsx"
    derived_name = config_path.name or f"{input_path.stem}_PI_Builder{derived_suffix}"

    if config_path.name:
        default_path = config_path if config_path.suffix else config_path.with_suffix(derived_suffix)
    else:
        default_path = input_path.with_name(derived_name)

    if custom_path is None:
        return default_path

    target = Path(custom_path)
    if target.exists() and target.is_dir():
        return target / derived_name

    if target.suffix == "":
        return target.with_suffix(derived_suffix)

    return target


def run(json_file: Optional[Path], in_file: Path, out_file: Optional[Path], all_output: bool):
    logger.debug(f"Starting run with input='{in_file}', json='{json_file}', output='{out_file}', mark_all={all_output}.")
    excel_manager = ExcelManager(in_file)
    hierarchy_dict = excel_manager.create_dict()

    json_manager = JsonManager(json_file)
    diff = json_manager.compare_and_update(hierarchy_dict)
    logger.debug(
        f"Diff stats | new={len(diff.new_elements)} | renamed={len(diff.renamed_elements)} | "
        f"removed={len(diff.removed_elements)}."
    )

    if diff.removed_elements:
        removed_keys = list(diff.removed_elements.keys())
        preview = ", ".join(removed_keys[:5])
        if len(removed_keys) > 5:
            preview += ", ..."
        logger.warning(
            f"Detected {len(diff.removed_elements)} removed elements in Excel input (examples: {preview}). "
            f"These entries will be dropped from the PI Builder export."
        )

    if not diff.has_changes and not all_output:
        message = "No changes detected"
        logger.info(f"{message}")
        typer.echo(message)
        return

    output_path = _resolve_output_path(out_file, in_file)
    logger.debug(f"Resolved PI Builder output path: '{output_path}'.")
    df = build_pibuilder_dataframe(hierarchy_dict, diff, mark_all=all_output)
    export_to_excel(df, output_path)

    logger.success(
        f"PI Builder Excel generated at {output_path} | Total rows: {len(df)} | "
        f"New: {len(diff.new_elements)} | Renamed: {len(diff.renamed_elements)}"
    )


if __name__ == "__main__":
    app()
