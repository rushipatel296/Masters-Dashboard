import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Load data
df = pd.read_csv("consolidated_ms_admits.csv")

# Convert numeric fields
for col in ["GRE_Verbal", "GRE_Quant", "GRE_AWA", "TOEFL", "CGPA"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Funded flag
df["IsFunded"] = df["AdmitType"].notna()

# Sidebar
st.sidebar.title("Filters")
selected_year = st.sidebar.multiselect("Select Year(s)", sorted(df["Year"].dropna().unique()), default=df["Year"].dropna().unique())
df = df[df["Year"].isin(selected_year)]

# Title
st.title("MS Admits Dashboard")
st.write(f"Total records: {len(df)}")

# Charts
st.subheader("Top Admit Universities")
st.bar_chart(df["AdmitUniversity"].value_counts().head(10))

st.subheader("Top Target Majors")
st.bar_chart(df["TargetMajor"].value_counts().head(10))

st.subheader("Funding Stats")
st.bar_chart(df["IsFunded"].value_counts().rename({True: "Funded", False: "Not Funded"}))

st.subheader("Work Experience Distribution")
st.bar_chart(df["HasWorkEx"].value_counts().rename({True: "With Work Ex", False: "Without Work Ex"}))

st.subheader("Average CGPA by Major")
avg_cgpa = df.groupby("TargetMajor")["CGPA"].mean().sort_values(ascending=False).head(10)
st.bar_chart(avg_cgpa)

st.subheader("Average GRE Quant by Admit University")
avg_gre = df.groupby("AdmitUniversity")[["GRE_Verbal", "GRE_Quant", "GRE_AWA"]].mean()
st.dataframe(avg_gre.sort_values("GRE_Quant", ascending=False).head(10))

st.subheader("Admits per Year")
st.line_chart(df.groupby("Year")["Name"].count())

# CS-focused section
st.title("MS Admits Data Explorer")
st.header("📊 Computer Science Analytics")

# Filter CS entries
df["TargetMajor"] = df["TargetMajor"].astype(str).str.strip().str.lower()
cs_df = df[df["TargetMajor"].str.contains("computer science", na=False)]

st.subheader("Top Universities for CS Admits")
top_cs_admits = cs_df["AdmitUniversity"].value_counts().head(10)
st.dataframe(top_cs_admits)

fig, ax = plt.subplots()
top_cs_admits.plot(kind="barh", ax=ax)
ax.set_xlabel("Number of CS Admits")
ax.set_ylabel("University")
st.pyplot(fig)

st.subheader("CGPA Distribution for CS Admits")
fig, ax = plt.subplots()
cs_df["CGPA"].dropna().hist(bins=20, ax=ax)
ax.set_title("CGPA Distribution for CS Admits")
st.pyplot(fig)

st.dataframe(cs_df[["CGPA", "GRE_Quant", "GRE_Verbal", "GRE_AWA", "TOEFL"]].mean())

st.subheader("Most Commonly Applied Universities for CS")
applied_univs_series = cs_df["AppliedUniversity"].dropna().astype(str).str.lower().str.split(",")
all_applied_univs = [univ.strip() for sublist in applied_univs_series for univ in sublist]
applied_counts = Counter(all_applied_univs)
most_common_applied = pd.Series(dict(applied_counts)).sort_values(ascending=False).head(10)
st.dataframe(most_common_applied)

# Average CGPA by top CS admit universities
st.subheader("Average CGPA for Top 20 CS Admit Universities")
top_20_cs_univs = cs_df["AdmitUniversity"].value_counts().head(20).index
avg_cgpa_by_univ = cs_df[cs_df["AdmitUniversity"].isin(top_20_cs_univs)].groupby("AdmitUniversity")["CGPA"].mean().sort_values(ascending=False)
st.dataframe(avg_cgpa_by_univ)

fig, ax = plt.subplots()
avg_cgpa_by_univ.plot(kind="barh", ax=ax)
ax.set_xlabel("Average CGPA")
ax.set_ylabel("University")
ax.set_title("Top 20 CS Admit Universities - Average CGPA")
st.pyplot(fig)
