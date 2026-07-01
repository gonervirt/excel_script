from __future__ import annotations

import argparse
import configparser
import json
from pathlib import Path
from typing import Any

import pandas as pd


def filter_excel_rows(
    input_excel_file: str | Path,
    output_excel_file: str | Path,
    column_filters: dict[str, list[Any]],
    keep_matching_values: bool,
) -> tuple[int, int]:
    """Filter rows from an Excel file using per-column allowed values.

    A row is considered a match when, for every configured column, its value is in
    the configured allowed values list for that column.

    Args:
        input_excel_file: Path to input Excel file.
        output_excel_file: Path to filtered output Excel file.
        column_filters: Mapping of column name to list of values used for matching.
        keep_matching_values: If True, keep matching rows. If False, remove them.

    Returns:
        A tuple of (input_rows, output_rows).

    Raises:
        ValueError: If filters are empty, malformed, or reference missing columns.
    """
    if not column_filters:
        raise ValueError("column_filters must contain at least one column filter.")

    df = pd.read_excel(input_excel_file)

    for column_name, values in column_filters.items():
        if column_name not in df.columns:
            raise ValueError(f"Missing column in input file: {column_name}")
        if not isinstance(values, list) or not values:
            raise ValueError(
                f"Filter values for column '{column_name}' must be a non-empty list."
            )

    mask = pd.Series(True, index=df.index)
    for column_name, values in column_filters.items():
        mask = mask & df[column_name].isin(values)

    output_df = df.loc[mask].copy() if keep_matching_values else df.loc[~mask].copy()
    output_df.to_excel(output_excel_file, index=False)

    return len(df), len(output_df)


def _parse_column_filters_json(column_filters_json: str) -> dict[str, list[Any]]:
    try:
        parsed = json.loads(column_filters_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for column_filters_json: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("column_filters_json must decode to a dictionary.")

    normalized: dict[str, list[Any]] = {}
    for key, value in parsed.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("All filter keys must be non-empty column names.")
        if not isinstance(value, list):
            raise ValueError(f"Filter for column '{key}' must be a list.")
        normalized[key] = value

    return normalized


def _load_ini_config(config_path: str | Path) -> dict[str, Any]:
    parser = configparser.ConfigParser()
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}. Create it or pass --config with a valid file."
        )

    parser.read(config_path, encoding="utf-8")

    if "filter" not in parser:
        raise ValueError("Missing [filter] section in config file.")

    section = parser["filter"]
    required_keys = [
        "input_excel_file",
        "output_excel_file",
        "column_filters_json",
        "keep_matching_values",
    ]

    missing_keys = [k for k in required_keys if not section.get(k, "").strip()]
    if missing_keys:
        raise ValueError(f"Missing required keys in [filter] section: {missing_keys}")

    return {
        "input_excel_file": section["input_excel_file"],
        "output_excel_file": section["output_excel_file"],
        "column_filters": _parse_column_filters_json(section["column_filters_json"]),
        "keep_matching_values": section.getboolean("keep_matching_values"),
    }


def main() -> None:
    default_config = Path(__file__).resolve().with_name("excel_filter_rows.ini")
    parser = argparse.ArgumentParser(
        description="Filter rows from an Excel file using an INI config."
    )
    parser.add_argument(
        "--config",
        default=str(default_config),
        help=f"Path to INI config file (default: {default_config}).",
    )

    args = parser.parse_args()
    config = _load_ini_config(args.config)

    input_rows, output_rows = filter_excel_rows(**config)
    print(f"Done. input_rows={input_rows}, output_rows={output_rows}")


if __name__ == "__main__":
    main()
