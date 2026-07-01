from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from excel_split_by_column import split_excel_by_column


def _write_excel(df: pd.DataFrame, file_path: Path) -> None:
    df.to_excel(file_path, index=False)


def test_split_creates_one_file_per_distinct_value_including_null(tmp_path: Path) -> None:
    input_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "country": ["FR", "ES", "FR", None, "DE"],
            "amount": [10, 20, 30, 40, 50],
        }
    )

    input_file = tmp_path / "input.xlsx"
    out_dir = tmp_path / "out"
    _write_excel(input_df, input_file)

    input_rows, files_created = split_excel_by_column(
        input_excel_file=input_file,
        output_directory=out_dir,
        split_column="country",
        output_file_prefix="by_country",
    )

    assert (input_rows, files_created) == (5, 4)

    created_files = sorted(p.name for p in out_dir.glob("*.xlsx"))
    assert created_files == [
        "by_country_DE.xlsx",
        "by_country_ES.xlsx",
        "by_country_FR.xlsx",
        "by_country_NULL.xlsx",
    ]

    fr_df = pd.read_excel(out_dir / "by_country_FR.xlsx")
    assert set(fr_df["id"].tolist()) == {1, 3}


def test_missing_split_column_raises_value_error(tmp_path: Path) -> None:
    input_df = pd.DataFrame({"id": [1, 2], "country": ["FR", "ES"]})
    input_file = tmp_path / "input.xlsx"
    out_dir = tmp_path / "out"
    _write_excel(input_df, input_file)

    with pytest.raises(ValueError, match="Missing column"):
        split_excel_by_column(
            input_excel_file=input_file,
            output_directory=out_dir,
            split_column="unknown",
            output_file_prefix="by_country",
        )


def test_values_with_special_characters_create_safe_filenames(tmp_path: Path) -> None:
    input_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "city": ["New York", "Sao/Paulo", "Paris"],
        }
    )
    input_file = tmp_path / "input.xlsx"
    out_dir = tmp_path / "out"
    _write_excel(input_df, input_file)

    _, files_created = split_excel_by_column(
        input_excel_file=input_file,
        output_directory=out_dir,
        split_column="city",
        output_file_prefix="by_city",
    )

    assert files_created == 3
    created_files = sorted(p.name for p in out_dir.glob("*.xlsx"))
    assert created_files == [
        "by_city_New_York.xlsx",
        "by_city_Paris.xlsx",
        "by_city_Sao_Paulo.xlsx",
    ]
