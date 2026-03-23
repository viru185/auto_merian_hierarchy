import sys
from pathlib import Path
from typing import Optional

import typer

from src.config import IN_FILE, JSON_FILE
from src.excel_manager import ExcelManager
from src.json_manager import JsonManager
from src.logger import logger

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
        exists=True,
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
        logger.debug("Debug mode enabled from CLI.")


    run(json_file=json_file, in_file=input_file, out_file=output, all=all_output)


def run(json_file, in_file,out_file,all):
    excel_manager = ExcelManager(in_file)
    json_manager = JsonManager(json_file)

    hierarchy_dict = excel_manager.create_dict()
    json_manager.save_to_json(hierarchy_dict)


if __name__ == "__main__":
    app()
