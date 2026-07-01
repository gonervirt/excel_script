from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from excel_filter_rows import filter_excel_rows


def _write_excel(df: pd.DataFrame, file_path: Path) -> None:
    df.to_excel(file_path, index=False)


def _sample_input_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "country": ["FR", "FR", "ES", "DE", "ES", "US"],
            "status": ["active", "inactive", "active", "active", "inactive", "active"],
            "segment": ["A", "A", "B", "A", "B", "C"],
        }
    )


def test_keep_matching_values(tmp_path: Path) -> None:
    input_df = _sample_input_df()
    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "out_keep.xlsx"
    _write_excel(input_df, input_file)

    in_rows, out_rows = filter_excel_rows(
        input_excel_file=input_file,
        output_excel_file=output_file,
        column_filters={"country": ["FR", "ES"], "status": ["active"]},
        keep_matching_values=True,
    )

    out_df = pd.read_excel(output_file)

    assert (in_rows, out_rows) == (6, 2)
    assert set(out_df["id"].tolist()) == {1, 3}


def test_remove_matching_values(tmp_path: Path) -> None:
    input_df = _sample_input_df()
    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "out_remove.xlsx"
    _write_excel(input_df, input_file)

    in_rows, out_rows = filter_excel_rows(
        input_excel_file=input_file,
        output_excel_file=output_file,
        column_filters={"country": ["FR", "ES"], "status": ["active"]},
        keep_matching_values=False,
    )

    out_df = pd.read_excel(output_file)

    assert (in_rows, out_rows) == (6, 4)
    assert set(out_df["id"].tolist()) == {2, 4, 5, 6}


def test_missing_filter_column_raises_value_error(tmp_path: Path) -> None:
    input_df = _sample_input_df()
    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "out.xlsx"
    _write_excel(input_df, input_file)

    with pytest.raises(ValueError, match="Missing column"):
        filter_excel_rows(
            input_excel_file=input_file,
            output_excel_file=output_file,
            column_filters={"unknown_column": ["x"]},
            keep_matching_values=True,
        )


def test_empty_filters_raise_value_error(tmp_path: Path) -> None:
    input_df = _sample_input_df()
    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "out.xlsx"
    _write_excel(input_df, input_file)

    with pytest.raises(ValueError, match="must contain at least one"):
        filter_excel_rows(
            input_excel_file=input_file,
            output_excel_file=output_file,
            column_filters={},
            keep_matching_values=True,
        )


def test_empty_filter_value_list_raises_value_error(tmp_path: Path) -> None:
    input_df = _sample_input_df()
    input_file = tmp_path / "input.xlsx"
    output_file = tmp_path / "out.xlsx"
    _write_excel(input_df, input_file)

    with pytest.raises(ValueError, match="non-empty list"):
        filter_excel_rows(
            input_excel_file=input_file,
            output_excel_file=output_file,
            column_filters={"country": []},
            keep_matching_values=True,
        )
