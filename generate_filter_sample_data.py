from __future__ import annotations

from pathlib import Path

import pandas as pd


def generate_filter_sample_data(output_dir: str | Path = "filter_sample_data") -> Path:
    """Generate sample data that covers keep/remove and edge filtering cases."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7, 8],
            "country": ["FR", "FR", "ES", "DE", "US", "ES", None, "FR"],
            "status": [
                "active",
                "inactive",
                "active",
                "active",
                "inactive",
                "inactive",
                "active",
                "active",
            ],
            "segment": ["A", "A", "B", "A", "C", "B", "C", "A"],
            "amount": [100, 90, 120, 80, 70, 50, 40, 110],
        }
    )

    input_file = output_path / "input.xlsx"
    df.to_excel(input_file, index=False)
    return input_file


if __name__ == "__main__":
    generated_file = generate_filter_sample_data()
    print(f"Generated input: {generated_file}")
