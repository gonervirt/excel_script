from __future__ import annotations

from pathlib import Path

import pandas as pd


def generate_sample_data(output_dir: str | Path = "sample_data") -> dict[str, Path]:
    """Generate sample Excel files covering key merge scenarios.

    Scenarios covered:
    - matched rows
    - unmatched rows
    - duplicate keys in lookup (first occurrence kept)
    - null key in source
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    source_df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4, 5, 6],
            "customer_id": [100, 101, 102, 103, 104, None],
            "amount": [120.0, 250.0, 60.0, 99.0, 410.0, 75.5],
        }
    )

    lookup_df = pd.DataFrame(
        {
            "cust_id": [100, 101, 101, 104, 105],
            "segment": ["A", "B", "B_DUPLICATE", "A", "C"],
            "region": ["North", "South", "West", "North", "East"],
            "risk_score": [0.1, 0.5, 0.9, 0.2, 0.7],
        }
    )

    source_file = output_path / "source.xlsx"
    lookup_file = output_path / "lookup.xlsx"

    source_df.to_excel(source_file, index=False)
    lookup_df.to_excel(lookup_file, index=False)

    return {
        "source": source_file,
        "lookup": lookup_file,
    }


if __name__ == "__main__":
    files = generate_sample_data()
    print(f"Generated source: {files['source']}")
    print(f"Generated lookup: {files['lookup']}")
