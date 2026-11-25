from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).with_name("consolidated_ms_admits.csv")
SCORE_RANGES = {
    "CGPA": (0, 10),
    "GRE_Verbal": (130, 170),
    "GRE_Quant": (130, 170),
    "GRE_AWA": (0, 6),
    "TOEFL": (1, 120),
}


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    for column, (minimum, maximum) in SCORE_RANGES.items():
        values = pd.to_numeric(df[column], errors="coerce")
        df[column] = values.where(values.between(minimum, maximum))

    df["TargetMajor"] = df["TargetMajor"].astype("string").str.strip()
    df["AdmitUniversity"] = df["AdmitUniversity"].astype("string").str.strip()
    df["IsCS"] = df["TargetMajor"].str.contains("computer science", case=False, na=False)
    return df


def counts_table(series: pd.Series, label: str, limit: int = 10) -> pd.DataFrame:
    return (
        series.dropna()
        .value_counts()
        .head(limit)
        .rename_axis(label)
        .reset_index(name="Admits")
    )


st.set_page_config(
    page_title="BITS Pilani MS Admits Explorer",
    page_icon="🎓",
    layout="wide",
)

df = load_data()

st.title("BITS Pilani MS Admits Explorer")
st.caption(
    "Ten years of postgraduate admission outcomes, cleaned from yearly spreadsheets "
    "and explored through an interactive dashboard."
)

with st.sidebar:
    st.header("Filters")
    available_years = sorted(df["Year"].dropna().astype(int).unique())
    selected_years = st.multiselect(
        "Admission years",
        available_years,
        default=available_years,
    )
    st.caption("Scores outside their documented ranges are treated as missing.")

filtered = df[df["Year"].isin(selected_years)] if selected_years else df.iloc[0:0]
cs_df = filtered[filtered["IsCS"]]

metric_columns = st.columns(4)
metric_columns[0].metric("Admit records", f"{len(filtered):,}")
metric_columns[1].metric("Years covered", filtered["Year"].nunique())
metric_columns[2].metric("Universities", filtered["AdmitUniversity"].nunique())
metric_columns[3].metric("Computer Science", f"{len(cs_df):,}")

overview_tab, cs_tab, notes_tab = st.tabs(
    ["Overview", "Computer Science", "Data notes"]
)

with overview_tab:
    left, right = st.columns(2)

    with left:
        st.subheader("Top admit universities")
        top_universities = counts_table(filtered["AdmitUniversity"], "University")
        st.bar_chart(
            top_universities,
            x="University",
            y="Admits",
            horizontal=True,
            height=420,
        )

    with right:
        st.subheader("Most common target majors")
        top_majors = counts_table(filtered["TargetMajor"], "Major")
        st.bar_chart(
            top_majors,
            x="Major",
            y="Admits",
            horizontal=True,
            height=420,
        )

    left, right = st.columns(2)

    with left:
        st.subheader("Admits by year")
        yearly = (
            filtered.groupby("Year")
            .size()
            .rename("Admits")
            .reset_index()
            .sort_values("Year")
        )
        st.line_chart(yearly, x="Year", y="Admits")

    with right:
        st.subheader("Work-experience coverage")
        work_experience = (
            filtered["HasWorkEx"]
            .map({True: "With work experience", False: "Without work experience"})
            .fillna("Not reported")
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Records")
        )
        st.bar_chart(
            work_experience,
            x="Status",
            y="Records",
            horizontal=True,
        )

    st.subheader("Average reported scores by popular university")
    popular_universities = filtered["AdmitUniversity"].value_counts().head(15).index
    score_summary = (
        filtered[filtered["AdmitUniversity"].isin(popular_universities)]
        .groupby("AdmitUniversity")[["CGPA", "GRE_Quant", "GRE_Verbal", "GRE_AWA", "TOEFL"]]
        .mean()
        .round(2)
        .sort_values("GRE_Quant", ascending=False)
    )
    st.dataframe(score_summary, width="stretch")

with cs_tab:
    st.subheader("Computer Science outcomes")
    st.write(
        "This view includes records whose target major contains “Computer Science”. "
        f"The current filters contain **{len(cs_df):,}** such records."
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Top universities")
        top_cs_universities = counts_table(cs_df["AdmitUniversity"], "University", 12)
        st.bar_chart(
            top_cs_universities,
            x="University",
            y="Admits",
            horizontal=True,
            height=460,
        )

    with right:
        st.markdown("#### CGPA distribution")
        cgpa_bins = pd.cut(
            cs_df["CGPA"],
            bins=[0, 7, 7.5, 8, 8.5, 9, 9.5, 10],
            include_lowest=True,
        )
        cgpa_distribution = (
            cgpa_bins.value_counts(sort=False)
            .rename_axis("CGPA range")
            .reset_index(name="Records")
        )
        cgpa_distribution["CGPA range"] = cgpa_distribution["CGPA range"].astype(str)
        st.bar_chart(cgpa_distribution, x="CGPA range", y="Records")

    st.markdown("#### Average reported scores for popular CS destinations")
    popular_cs_universities = cs_df["AdmitUniversity"].value_counts().head(15).index
    cs_score_summary = (
        cs_df[cs_df["AdmitUniversity"].isin(popular_cs_universities)]
        .groupby("AdmitUniversity")[["CGPA", "GRE_Quant", "GRE_Verbal", "GRE_AWA", "TOEFL"]]
        .agg(["mean", "count"])
        .round(2)
    )
    st.dataframe(cs_score_summary, width="stretch")

with notes_tab:
    st.subheader("How to read this dashboard")
    st.markdown(
        """
        - The source combines yearly spreadsheets from 2015–2024, whose formats and field names varied.
        - Records are self-reported and may contain inconsistent university or major names.
        - Invalid numeric scores are excluded from averages: CGPA 0–10, GRE sections 130–170,
          GRE AWA 0–6, and TOEFL 1–120.
        - Missing values remain missing; they are not estimated.
        - Counts describe this dataset, not admissions odds or university rankings.
        """
    )

    st.markdown("#### Field coverage")
    coverage_columns = [
        "AdmitUniversity",
        "TargetMajor",
        "CGPA",
        "GRE_Quant",
        "GRE_Verbal",
        "GRE_AWA",
        "TOEFL",
        "HasWorkEx",
    ]
    coverage = pd.DataFrame(
        {
            "Available": filtered[coverage_columns].notna().sum(),
            "Missing": filtered[coverage_columns].isna().sum(),
        }
    )
    coverage["Coverage"] = (
        coverage["Available"].div(len(filtered)).mul(100).round(1).astype(str) + "%"
        if len(filtered)
        else "0.0%"
    )
    st.dataframe(coverage, width="stretch")
