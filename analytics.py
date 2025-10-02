import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("consolidated_ms_admits.csv")

# Preview
print(df.shape)
print(df.columns)
print(df.head())

top_admits = df["AdmitUniversity"].value_counts().head(10)
print(top_admits)

top_majors = df["TargetMajor"].value_counts().head(10)
print(top_majors)

df["IsFunded"] = df["AdmitType"].notna()
funding_stats = df["IsFunded"].value_counts()
print(funding_stats)

workex_stats = df.groupby("HasWorkEx")["AdmitUniversity"].count()
print(workex_stats)

for col in ["GRE_Verbal", "GRE_Quant", "GRE_AWA", "TOEFL"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Force CGPA to numeric by coercing all bad values to NaN
df["CGPA"] = pd.to_numeric(df["CGPA"].astype(str).str.strip(), errors="coerce")


avg_cgpa_major = df.groupby("TargetMajor")["CGPA"].mean().sort_values(ascending=False)
print(avg_cgpa_major.head(10))

avg_gre = df.groupby("AdmitUniversity")[["GRE_Verbal", "GRE_Quant", "GRE_AWA"]].mean()
print(avg_gre.sort_values("GRE_Quant", ascending=False).head(10))

yearly_stats = df.groupby("Year")["Name"].count()
print(yearly_stats)



top_admits.plot(kind="barh", title="Top Admit Universities")
plt.xlabel("Number of Admits")
plt.tight_layout()
plt.show()


