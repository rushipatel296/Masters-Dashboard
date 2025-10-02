import pandas as pd
import os
import glob
import re

# Directory where your Excel files are stored
data_dir = "/Users/rushipatel/Desktop/Masters/"

# Mapping raw column names to standardized names
COLUMN_MAPPING = {
    "Name": "Name",
    "Campus": "Campus",
    "CGPA": "CGPA",
    "Duration of work experience": "WorkExDuration",
    "Target Discipline": "TargetMajor",
    "In case you answered Other, please specify your target discipline in the text box below": "TargetMajor_Other",
    "University Selected": "AdmitUniversity",
    "Universities (Admits)": "AppliedUniversity",
    "Universities Applied To": "AppliedUniversity",
    "GRE Score : Verbal": "GRE_Verbal",
    "GRE Score : Quant": "GRE_Quant",
    "GRE Score : AWA": "GRE_AWA",
    "TOEFL Score": "TOEFL",
    "Universities (Funded admit)": "AdmitType"
}

# Alias normalization map for universities
univ_alias_map = {
    "cmu": "Carnegie Mellon University",
    "carnegie mellon": "Carnegie Mellon University",
    "carnegie mellon university": "Carnegie Mellon University",
    "uiuc": "University of Illinois Urbana-Champaign",
    "university of illinois - urbana-champaign": "University of Illinois Urbana-Champaign",
    "u illinois urbana champaign": "University of Illinois Urbana-Champaign",
    "ucsd": "University of California San Diego",
    "university of california san diego": "University of California San Diego",
    "uc san diego": "University of California San Diego",
    "tamu": "Texas A&M University",
    "texas a&m": "Texas A&M University",
    "texas a&m university": "Texas A&M University",
    "ut austin": "University of Texas at Austin",
    "university of texas at austin": "University of Texas at Austin",
    "uw madison": "University of Wisconsin-Madison",
    "university of wisconsin madison": "University of Wisconsin-Madison",
    "university of wisconsin - madison": "University of Wisconsin-Madison",
    "university of wisconsin-madison": "University of Wisconsin-Madison"
}

def parse_work_experience(text):
    if not isinstance(text, str):
        return 0
    text = text.lower().strip()
    years = 0
    months = 0
    decimal_years = re.findall(r'(\d+(?:\.\d+)?)\s*(?:yrs?|years?)', text)
    if decimal_years:
        years += float(decimal_years[0])
    month_matches = re.findall(r'(\d+)\s*(?:months?|mos?)', text)
    if month_matches:
        months += int(month_matches[0])
    return round(years * 12 + months)

def load_and_clean(file_path):
    try:
        year = int(os.path.basename(file_path).split("_")[0])
    except ValueError:
        print(f"Skipping file (invalid year): {file_path}")
        return pd.DataFrame()

    df = pd.read_excel(file_path, engine='openpyxl')
    kept_cols = {col: COLUMN_MAPPING[col] for col in df.columns if col in COLUMN_MAPPING}
    df = df[list(kept_cols.keys())].rename(columns=kept_cols)

    if "TargetMajor_Other" in df.columns:
        df["TargetMajor"] = df["TargetMajor"].fillna(df["TargetMajor_Other"])
        df.drop(columns=["TargetMajor_Other"], inplace=True)

    if "WorkExDuration" in df.columns:
        df["WorkExMonths"] = df["WorkExDuration"].apply(parse_work_experience)
        df["HasWorkEx"] = df["WorkExMonths"] > 0

    df["Year"] = year
    return df

file_paths = [
    f for f in glob.glob(os.path.join(data_dir, "*_Admits.xlsx"))
    if not os.path.basename(f).startswith("~$")
]

cleaned_dfs = [load_and_clean(fp) for fp in file_paths if not fp.startswith("~$")]
consolidated_df = pd.concat(cleaned_dfs, ignore_index=True)

# Strip all object columns
for col in consolidated_df.select_dtypes(include=["object"]):
    consolidated_df[col] = consolidated_df[col].astype(str).str.strip()

# Remove duplicates
consolidated_df = consolidated_df.drop_duplicates()

# Normalize AdmitUniversity
consolidated_df["AdmitUniversity_clean"] = consolidated_df["AdmitUniversity"].astype(str).str.strip().str.lower()
consolidated_df["AdmitUniversity_normalized"] = consolidated_df["AdmitUniversity_clean"].map(univ_alias_map)
consolidated_df["AdmitUniversity"] = consolidated_df["AdmitUniversity_normalized"].fillna(consolidated_df["AdmitUniversity"])
consolidated_df.drop(columns=["AdmitUniversity_clean", "AdmitUniversity_normalized"], inplace=True)

# Save cleaned data
consolidated_df.to_csv("consolidated_ms_admits.csv", index=False)
print(consolidated_df.head())
