# BITS Pilani MS Admits Explorer

An interactive look at ten years of postgraduate admission outcomes from BITS Pilani. The project consolidates yearly spreadsheets with changing formats into one dataset, then surfaces trends across universities, majors, test scores, and work experience.

## What it includes

- Year-by-year admission trends from 2015–2024
- Popular universities and target majors
- A focused view of Computer Science outcomes
- Transparent score validation and field-coverage notes
- Interactive filters built with Streamlit

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

## Data note

The source records are self-reported and contain inconsistent naming and missing values. The dashboard excludes scores outside their documented ranges from averages and does not estimate missing data. Its aggregates describe this dataset—not admission probabilities or university rankings.

## Built with

Python, pandas, and Streamlit.
