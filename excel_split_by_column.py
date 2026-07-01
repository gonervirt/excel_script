from __future__ import annotations

import argparse
import configparser
import re
from pathlib import Path
from typing import Any

import pandas as pd


def split_excel_by_column(
    input_excel_file: str | Path,
    output_directory: str | Path,
    split_column: str,
    output_file_prefix: str,
) -> tuple[int, int]:
    """Split an Excel file into several files based on distinct values of one column.

    Each distinct value in split_column creates one output file containing all rows
    matching that value. Null/NaN values are grouped into a file named 'NULL.xlsx'.

    Args:
        input_excel_file: Path to input Excel file.
        output_directory: Directory where split files are written.
        split_column: Column used to split rows.
        output_file_prefix: Common prefix used for all output file names.

    Returns:
        A tuple of (input_rows, files_created).

    Raises:
        ValueError: If split_column does not exist or output_file_prefix is invalid.
    """
    df = pd.read_excel(input_excel_file)
    if split_column not in df.columns:
        raise ValueError(f"Missing column in input file: {split_column}")
    if not output_file_prefix or not str(output_file_prefix).strip():
        raise ValueError("output_file_prefix must be a non-empty string.")

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    files_created = 0
    for raw_value, group_df in df.groupby(split_column, dropna=False):
        file_stem = _sanitize_filename_component(raw_value)
        output_file = output_dir / f"{output_file_prefix}_{file_stem}.xlsx"
        group_df.to_excel(output_file, index=False)
        files_created += 1

    return len(df), files_created


def _sanitize_filename_component(value: Any) -> str:
    if pd.isna(value):
        return "NULL"

    text = str(value).strip()
    if not text:
        return "EMPTY"

    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    sanitized = sanitized.strip("._-")
    return sanitized or "VALUE"


def _load_ini_config(config_path: str | Path) -> dict[str, Any]:
    parser = configparser.ConfigParser()
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}. Create it or pass --config with a valid file."
        )

    parser.read(config_path, encoding="utf-8")

    if "split" not in parser:
        raise ValueError("Missing [split] section in config file.")

    section = parser["split"]
    required_keys = [
        "input_excel_file",
        "output_directory",
        "split_column",
        "output_file_prefix",
    ]
    missing_keys = [k for k in required_keys if not section.get(k, "").strip()]
    if missing_keys:
        raise ValueError(f"Missing required keys in [split] section: {missing_keys}")

    return {
        "input_excel_file": section["input_excel_file"],
        "output_directory": section["output_directory"],
        "split_column": section["split_column"],
        "output_file_prefix": section["output_file_prefix"],
    }


def main() -> None:
    default_config = Path(__file__).resolve().with_name("excel_split_by_column.ini")
    parser = argparse.ArgumentParser(
        description="Split an Excel file into multiple files using one column and an INI config."
    )
    parser.add_argument(
        "--config",
        default=str(default_config),
        help=f"Path to INI config file (default: {default_config}).",
    )

    args = parser.parse_args()
    config = _load_ini_config(args.config)

    input_rows, files_created = split_excel_by_column(**config)
    print(f"Done. input_rows={input_rows}, files_created={files_created}")


if __name__ == "__main__":
    main()
