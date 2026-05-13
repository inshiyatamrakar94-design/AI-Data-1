import pandas as pd
import numpy as np

# --- TASK 2: Load and Inspect ---
df = pd.read_csv('messy_studentdata.csv')

print("--- Initial Info ---")
df.info()
print("\n--- Missing Values Count ---")
print(df.isnull().sum())

# --- TASK 3: Fix the 6 Problems ---

# 1. Whitespace: Remove extra spaces from names
df['name'] = df['name'].str.strip()

# 2. Casing: Make all names "Title Case" (e.g., alice -> Alice)
df['name'] = df['name'].str.title()

# 3. Type: Remove quotes and convert scores to numbers
# errors='coerce' turns things like empty strings into NaN (Null)
df['score'] = pd.to_numeric(df['score'].astype(str).str.replace('"', ''), errors='coerce')

# 4. Nulls: Fill missing names with 'Unknown' and missing scores with 0
df['name'] = df['name'].fillna('Unknown')
df['score'] = df['score'].fillna(0)

# 5. Invalid values: Replace scores below 0 with 0
df.loc[df['score'] < 0, 'score'] = 0

# 6. Duplicates: Remove identical rows
df = df.drop_duplicates()

# --- TASK 4: Add Grade Column ---
def assign_grade(score):
    if score >= 90: return 'A'
    if score >= 75: return 'B'
    if score >= 50: return 'C'
    return 'F'

df['grade'] = df['score'].apply(assign_grade)

# --- TASK 5: Save and Final Report ---
df.to_csv('clean_students.csv', index=False)

print("\n--- Cleaning Complete ---")
print(f"Original row count: 15")
print(f"Final row count: {len(df)}")
print("\nFinal Data Preview:")
print(df.head())
print("\n your new clean_students.csv file has been created with the cleaned data.")