from __future__ import annotations

from pathlib import Path

import pandas as pd


def generate_split_sample_data(output_dir: str | Path = "split_sample_data") -> Path:
    """Generate sample data for split-by-column behavior and edge cases."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7, 8],
            "country": ["FR", "ES", "FR", "DE", None, "US", "ES", "FR"],
            "segment": ["A", "B", "A", "A", "C", "C", "B", "A"],
            "amount": [100, 120, 80, 70, 50, 60, 110, 90],
        }
    )

    input_file = output_path / "input.xlsx"
    df.to_excel(input_file, index=False)
    return input_file


if __name__ == "__main__":
    generated_file = generate_split_sample_data()
    print(f"Generated input: {generated_file}")
