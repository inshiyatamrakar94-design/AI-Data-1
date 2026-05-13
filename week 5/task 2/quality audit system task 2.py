import json
import sqlite3
import pandas as pd
import requests

# 1. Fetch data from JSONPlaceholder API
url = "https://jsonplaceholder.typicode.com/posts"
response = requests.get(url)
data = response.json()

# Load into Pandas DataFrame
df_raw = pd.DataFrame(data)
initial_row_count = len(df_raw)

# 2. Programmatically detect issues before cleaning
# Convert columns to object type so they can accept mixed data types without crashing
df_raw["userId"] = df_raw["userId"].astype(object)
df_raw["title"] = df_raw["title"].astype(object)

# Introduce mock errors to test our audit layers
df_raw.loc[0, "title"] = None  # Introduce a null
df_raw.loc[1, "userId"] = "invalid_string_type"  # Introduce a type mismatch
df_raw.loc[2, "id"] = 9999  # Introduce an out-of-range value

# Introduce a duplicate row by duplicating the 10th row
duplicate_row = pd.DataFrame([df_raw.iloc[10]])
df_raw = pd.concat([df_raw, duplicate_row], ignore_index=True)

# Run the pre-cleaning audit metrics
null_counts = df_raw.isnull().sum().sum()
duplicate_counts = df_raw.duplicated().sum()

type_mismatches = 0
for val in df_raw["userId"]:
    if not isinstance(val, int):
        type_mismatches += 1

out_of_range = 0
for val in df_raw["id"]:
    if isinstance(val, (int, float)) and val > 200:
        out_of_range += 1

inconsistent_strings = 0
for val in df_raw["title"]:
    if isinstance(val, str) and not val.istitle():
        inconsistent_strings += 1

total_issues_before = (
    null_counts
    + duplicate_counts
    + type_mismatches
    + out_of_range
    + inconsistent_strings
)

# 3. Apply necessary transformations, cleaning, and enrichments
# Drop duplicates
df_clean = df_raw.drop_duplicates()

# Drop rows where title is null
df_clean = df_clean.dropna(subset=["title"])

# Fix type mismatches and out-of-range rows by filtering valid records
df_clean = df_clean[df_clean["userId"].apply(lambda x: isinstance(x, int))]
df_clean = df_clean[df_clean["id"] <= 200]

# Ensure correct data type conversions back to numeric elements
df_clean["userId"] = df_clean["userId"].astype(int)
df_clean["id"] = df_clean["id"].astype(int)

# Enrichments: Title casing
df_clean["title"] = df_clean["title"].astype(str).str.title()

# Enrichments: Word count
df_clean["word_count"] = df_clean["body"].astype(str).apply(lambda x: len(x.split()))

# Enrichments: Ranking (rank posts by word count descending)
df_clean["word_count_rank"] = (
    df_clean["word_count"].rank(ascending=False, method="dense").astype(int)
)

final_row_count = len(df_clean)

# Calculate fixed issues (Accounting for the artificially added duplicate row)
issues_fixed = (initial_row_count + 1) - final_row_count

# 4. Generate structured audit report
audit_data = {
    "Metric": [
        "Before Row Count",
        "After Row Count",
        "Null Values Detected",
        "Duplicate Rows Detected",
        "Type Mismatches Detected",
        "Out-of-Range Values Detected",
        "Inconsistent Strings Detected",
        "Total Issues Found",
        "Total Issues Fixed",
    ],
    "Value": [
        initial_row_count + 1,  # include the artificially added row
        final_row_count,
        null_counts,
        duplicate_counts,
        type_mismatches,
        out_of_range,
        inconsistent_strings,
        total_issues_before,
        issues_fixed,
    ],
}

audit_df = pd.DataFrame(audit_data)

# Save report to CSV
audit_df.to_csv("data_quality_audit_report.csv", index=False)

# Print as a formatted table
print("\n=== DATA QUALITY AUDIT REPORT ===")
print(audit_df.to_string(index=False))

# 5. Load the clean data into SQLite
conn = sqlite3.connect("clean_posts.db")
df_clean.to_sql("posts", conn, if_exists="replace", index=False)
conn.close()

print("\nETL Pipeline completed. Clean data saved to SQLite database successfully.")
