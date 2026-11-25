"""Create the privacy-reduced dataset used by the public dashboard.

Run this script locally while ``consolidated_ms_admits.csv`` is present. The raw
survey export is intentionally not required by, or included with, the deployed
application.
"""

from pathlib import Path

import pandas as pd


SOURCE = Path(__file__).with_name("consolidated_ms_admits.csv")
DESTINATION = Path(__file__).with_name("admissions_public.csv")
PUBLIC_COLUMNS = [
    "TargetMajor",
    "CGPA",
    "AdmitUniversity",
    "GRE_Verbal",
    "GRE_Quant",
    "GRE_AWA",
    "TOEFL",
    "HasWorkEx",
    "Year",
]


def main() -> None:
    data = pd.read_csv(SOURCE, usecols=PUBLIC_COLUMNS)
    data.to_csv(DESTINATION, index=False)
    print(f"Wrote {len(data):,} privacy-reduced records to {DESTINATION.name}")


if __name__ == "__main__":
    main()
