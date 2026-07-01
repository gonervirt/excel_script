from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from excel_lookup_merge import extend_excel_with_lookup


def _write_excel(df: pd.DataFrame, file_path: Path) -> None:
    df.to_excel(file_path, index=False)


def test_extend_excel_with_matches_and_unmatched(tmp_path: Path) -> None:
    source = pd.DataFrame(
        {
            "source_id": [10, 11, 12, 13],
            "name": ["Ana", "Bob", "Cyd", "Dan"],
        }
    )
    lookup = pd.DataFrame(
        {
            "lookup_id": [10, 11, 14],
            "country": ["FR", "ES", "DE"],
            "status": ["gold", "silver", "bronze"],
        }
    )

    source_file = tmp_path / "source.xlsx"
    lookup_file = tmp_path / "lookup.xlsx"
    output_file = tmp_path / "output.xlsx"
    unmatched_file = tmp_path / "unmatched.xlsx"

    _write_excel(source, source_file)
    _write_excel(lookup, lookup_file)

    source_rows, matched_rows, unmatched_rows = extend_excel_with_lookup(
        source_excel_file=source_file,
        lookup_excel_file=lookup_file,
        output_excel_file=output_file,
        source_key_column="source_id",
        lookup_key_column="lookup_id",
        lookup_columns_to_add=["country", "status"],
        unmatched_output_excel_file=unmatched_file,
    )

    assert (source_rows, matched_rows, unmatched_rows) == (4, 2, 2)

    out = pd.read_excel(output_file)
    unmatched = pd.read_excel(unmatched_file)

    assert list(out.columns) == ["source_id", "name", "country", "status"]
    assert out.loc[out["source_id"] == 10, "country"].iloc[0] == "FR"
    assert out.loc[out["source_id"] == 12, "country"].isna().iloc[0]

    assert set(unmatched["source_id"].tolist()) == {12, 13}


def test_duplicate_lookup_keys_keep_first_occurrence(tmp_path: Path) -> None:
    source = pd.DataFrame({"id": [1, 2], "value": ["x", "y"]})
    lookup = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "label": ["first", "second", "third"],
        }
    )

    source_file = tmp_path / "source.xlsx"
    lookup_file = tmp_path / "lookup.xlsx"
    output_file = tmp_path / "output.xlsx"
    unmatched_file = tmp_path / "unmatched.xlsx"

    _write_excel(source, source_file)
    _write_excel(lookup, lookup_file)

    extend_excel_with_lookup(
        source_excel_file=source_file,
        lookup_excel_file=lookup_file,
        output_excel_file=output_file,
        source_key_column="id",
        lookup_key_column="id",
        lookup_columns_to_add=["label"],
        unmatched_output_excel_file=unmatched_file,
    )

    out = pd.read_excel(output_file)
    assert out.loc[out["id"] == 1, "label"].iloc[0] == "first"


def test_missing_columns_raise_value_error(tmp_path: Path) -> None:
    source = pd.DataFrame({"id": [1]})
    lookup = pd.DataFrame({"other": [1], "label": ["x"]})

    source_file = tmp_path / "source.xlsx"
    lookup_file = tmp_path / "lookup.xlsx"
    output_file = tmp_path / "output.xlsx"
    unmatched_file = tmp_path / "unmatched.xlsx"

    _write_excel(source, source_file)
    _write_excel(lookup, lookup_file)

    with pytest.raises(ValueError, match="Missing columns"):
        extend_excel_with_lookup(
            source_excel_file=source_file,
            lookup_excel_file=lookup_file,
            output_excel_file=output_file,
            source_key_column="id",
            lookup_key_column="id",
            lookup_columns_to_add=["label"],
            unmatched_output_excel_file=unmatched_file,
        )


def test_no_lookup_columns_raises_value_error(tmp_path: Path) -> None:
    source = pd.DataFrame({"id": [1]})
    lookup = pd.DataFrame({"id": [1]})

    source_file = tmp_path / "source.xlsx"
    lookup_file = tmp_path / "lookup.xlsx"
    output_file = tmp_path / "output.xlsx"
    unmatched_file = tmp_path / "unmatched.xlsx"

    _write_excel(source, source_file)
    _write_excel(lookup, lookup_file)

    with pytest.raises(ValueError, match="must contain at least one"):
        extend_excel_with_lookup(
            source_excel_file=source_file,
            lookup_excel_file=lookup_file,
            output_excel_file=output_file,
            source_key_column="id",
            lookup_key_column="id",
            lookup_columns_to_add=[],
            unmatched_output_excel_file=unmatched_file,
        )
