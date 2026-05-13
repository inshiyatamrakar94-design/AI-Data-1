import os
import pandas as pd

# 1. Define the file path
file_name = 'clean_students.csv'
output_name = 'enriched_students.csv'

# 2. Check if the file exists before loading
if not os.path.exists(file_name):
    raise FileNotFoundError(
        f"Could not find '{file_name}' in your current folder. "
        f"Please move the CSV file to: {os.getcwd()}"
    )

print(f"Successfully located: {file_name}")

# 3. Source and load the CSV data
df = pd.read_csv(file_name)

# 4. Define helper functions for feature engineering
def calculate_letter_grade(score):
    if score >= 90: return 'A'
    elif score >= 75: return 'B'
    elif score >= 60: return 'C'
    elif score >= 50: return 'D'
    else: return 'F'

def categorize_score_level(score):
    if score >= 80: return 'High'
    elif score >= 50: return 'Medium'
    else: return 'Low'

# 5. Execute Data Transformations (Feature Engineering)
# Add letter grades using apply()
df['grade'] = df['score'].apply(calculate_letter_grade)

# Add a boolean pass/fail column (50 is the passing mark)
df['passed'] = df['score'] >= 50

# Add text performance categories using apply()
df['score_category'] = df['score'].apply(categorize_score_level)

# Rank students globally (highest score gets rank 1)
df['rank'] = df['score'].rank(ascending=False, method='min')

# 6. Generate Summaries and Aggregations
print("\n=== PERFORMANCE SUMMARY BY GRADE ===")
summary_stats = df.groupby('grade')['score'].agg(['count', 'mean', 'min', 'max'])
print(summary_stats)

# Generate an advanced Pivot Table summary if 'subject' exists in your CSV
if 'subject' in df.columns:
    print("\n=== PIVOT TABLE: AVERAGE SCORE BY GRADE & SUBJECT ===")
    pivot_summary = df.pivot_table(values='score', index='grade', columns='subject', aggfunc='mean')
    print(pivot_summary)

# 7. Sort the Final Dataset by Rank
df = df.sort_values(by='rank').reset_index(drop=True)

# 8. Export the Data to a New CSV File
df.to_csv(output_name, index=False)
print(f"\nProcessing complete! Enriched data saved as: '{output_name}'")

# 9. Preview the Top 5 Performing Students
print("\n=== TOP 5 HIGHEST RANKED STUDENTS ===")
print(df.head(5))
