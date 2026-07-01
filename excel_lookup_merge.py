from __future__ import annotations

import argparse
import configparser
from pathlib import Path
from typing import Iterable

import pandas as pd


def extend_excel_with_lookup(
    source_excel_file: str | Path,
    lookup_excel_file: str | Path,
    output_excel_file: str | Path,
    source_key_column: str,
    lookup_key_column: str,
    lookup_columns_to_add: list[str] | tuple[str, ...],
    unmatched_output_excel_file: str | Path,
) -> tuple[int, int, int]:
    """Extend a source Excel file with columns from a lookup Excel file.

    Args:
        source_excel_file: Path to the source Excel file.
        lookup_excel_file: Path to the lookup Excel file.
        output_excel_file: Path where extended Excel output is written.
        source_key_column: Column in source used for lookup.
        lookup_key_column: Column in lookup used for lookup.
        lookup_columns_to_add: Columns from lookup to append in output.
        unmatched_output_excel_file: Path to unmatched rows report.

    Returns:
        A tuple of (source_rows, matched_rows, unmatched_rows).

    Raises:
        ValueError: If required columns are missing or lookup columns list is empty.
    """
    if not lookup_columns_to_add:
        raise ValueError("lookup_columns_to_add must contain at least one column name.")

    source_df = pd.read_excel(source_excel_file)
    lookup_df = pd.read_excel(lookup_excel_file)

    _validate_columns(source_df, [source_key_column], "source")
    _validate_columns(lookup_df, [lookup_key_column, *lookup_columns_to_add], "lookup")

    lookup_subset = lookup_df[[lookup_key_column, *lookup_columns_to_add]].copy()

    # Keep first occurrence for duplicate lookup keys to make the join deterministic.
    lookup_subset = lookup_subset.drop_duplicates(subset=[lookup_key_column], keep="first")

    merged_df = source_df.merge(
        lookup_subset,
        how="left",
        left_on=source_key_column,
        right_on=lookup_key_column,
        indicator=True,
    )

    if source_key_column != lookup_key_column:
        merged_df = merged_df.drop(columns=[lookup_key_column])

    unmatched_df = source_df.loc[merged_df["_merge"] == "left_only"].copy()
    output_df = merged_df.drop(columns=["_merge"])

    output_df.to_excel(output_excel_file, index=False)
    unmatched_df.to_excel(unmatched_output_excel_file, index=False)

    source_rows = len(source_df)
    unmatched_rows = len(unmatched_df)
    matched_rows = source_rows - unmatched_rows
    return source_rows, matched_rows, unmatched_rows


def _validate_columns(df: pd.DataFrame, required_columns: Iterable[str], df_name: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in {df_name} file: {missing}")


def _parse_columns(columns_text: str) -> list[str]:
    columns = [c.strip() for c in columns_text.split(",") if c.strip()]
    if not columns:
        raise argparse.ArgumentTypeError("At least one lookup column must be provided.")
    return columns


def _load_ini_config(config_path: str | Path) -> dict[str, str | list[str]]:
    parser = configparser.ConfigParser()
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}. Create it or pass --config with a valid file."
        )

    parser.read(config_path, encoding="utf-8")

    if "merge" not in parser:
        raise ValueError("Missing [merge] section in config file.")

    section = parser["merge"]
    required_keys = [
        "source_excel_file",
        "lookup_excel_file",
        "output_excel_file",
        "source_key_column",
        "lookup_key_column",
        "lookup_columns_to_add",
        "unmatched_output_excel_file",
    ]

    missing_keys = [k for k in required_keys if not section.get(k, "").strip()]
    if missing_keys:
        raise ValueError(f"Missing required keys in [merge] section: {missing_keys}")

    return {
        "source_excel_file": section["source_excel_file"],
        "lookup_excel_file": section["lookup_excel_file"],
        "output_excel_file": section["output_excel_file"],
        "source_key_column": section["source_key_column"],
        "lookup_key_column": section["lookup_key_column"],
        "lookup_columns_to_add": _parse_columns(section["lookup_columns_to_add"]),
        "unmatched_output_excel_file": section["unmatched_output_excel_file"],
    }


def main() -> None:
    default_config = Path(__file__).resolve().with_name("excel_lookup_merge.ini")
    parser = argparse.ArgumentParser(
        description="Extend a source Excel file with columns from a lookup Excel file using an INI config."
    )
    parser.add_argument(
        "--config",
        default=str(default_config),
        help=f"Path to INI config file (default: {default_config}).",
    )

    args = parser.parse_args()
    config = _load_ini_config(args.config)

    source_rows, matched_rows, unmatched_rows = extend_excel_with_lookup(**config)

    print(
        f"Done. source_rows={source_rows}, matched_rows={matched_rows}, unmatched_rows={unmatched_rows}"
    )


if __name__ == "__main__":
    main()
