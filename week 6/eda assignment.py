# Run this checklist on every dataset you ever work with — in this order.

# 1. Shape
# Code: df.shape
# Purpose: How many rows and columns?

# 2. Types
# Code: df.dtypes  /  df.info()
# Purpose: Are columns the right type? Any objects that should be numbers?

# 3. Nulls
# Code: df.isnull().sum()
# Purpose: Which columns have missing data? What % is missing?

# 4. Stats
# Code: df.describe()
# Purpose: Is mean ≈ median? Are min/max reasonable? Is std too high?

# 5. Uniques
# Code: df['col'].value_counts()
# Purpose: Categorical columns — how many unique values? Any unexpected ones?

# 6. Dist'n
# Code: df.hist()  /  sns.boxplot()
# Purpose: Are values normally distributed or skewed? Any outliers?

# 7. Correlation
# Code: df.corr()  /  sns.heatmap()
# Purpose: Which columns move together? Any surprisingly high correlations?

# 8. Pair plot
# Code: sns.pairplot(df[numeric_cols])
# Purpose: Visual scan of all relationships at once — spot anything unusual?


"""
FINAL EDA SUMMARY:
1. The dataset contains 20 unique customer records across 6 attributes, consisting mostly of numeric tracking metrics.
2. Missing data is present in 'Age' (15% nulls) and 'Review_Rating' (5% null), which require imputation before modeling.
3. Categorical distribution reveals 'Bronze' is the dominant tier (9 users), while premium 'Diamond' has only 1 user.
4. 'Total_Spend' shows a severe right skew; the median is $392.18, but the maximum reaches an extreme $5,200.50.
5. High standard deviations in spending and item counts point to distinct customer segments rather than uniform behavior.


"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# =====================================================================
# STEP 1: Load the Dataset
# =====================================================================
# FIXME: Update the file path to your actual dataset location
df = pd.read_csv("ecommerce data.csv")


# =====================================================================
# STEP 2: Print Basic Structure
# =====================================================================
print("--- STEP 2: DATASET STRUCTURE ---")
print("Dataset Shape:", df.shape)
print("\nDataset Info:")
df.info()
print("\nData Types:\n", df.dtypes)

# Comment observations:
# The dataset contains 20 rows and 6 columns.
# Column 'A' is an integer, while column 'B' is text (object).


# =====================================================================
# STEP 3: Check for Missing Values
# =====================================================================
print("\n--- STEP 3: MISSING VALUES ---")
missing_count = df.isnull().sum()
missing_percentage = (df.isnull().sum() / len(df)) * 100

print("Missing Count:\n", missing_count)
print("\nMissing Percentage:\n", missing_percentage)


# =====================================================================
# STEP 4: Run Summary Statistics
# =====================================================================
print("\n--- STEP 4: SUMMARY STATISTICS ---")
print(df.describe())

# Comment observations:
# 1. The mean of column X is much higher than the median, suggesting a right skew.
# 2. Column Y has a minimum value of 0, which seems suspicious for this metric.
# 3. Maximum value in column Z is an extreme outlier compared to the 75th percentile.


# =====================================================================
# STEP 5: Categorical Value Counts
# =====================================================================
print("\n--- STEP 5: CATEGORICAL VALUE COUNTS ---")
# FIXME: Replace 'categorical_column' with a real text column name from your data
cat_col = "Membership_Level"
if cat_col in df.columns:
    print(df[cat_col].value_counts())
else:
    print(f"Column '{cat_col}' not found. Please update the column name.")


# =====================================================================
# STEP 6: Plot Histograms
# =====================================================================
print("\n--- STEP 6: GENERATING HISTOGRAMS ---")
numeric_cols = df.select_dtypes(include=["number"]).columns

for col in numeric_cols:
    plt.figure()
    sns.histplot(df[col], kde=True)
    plt.title(f"Histogram of {col}")
    plt.tight_layout()
    plt.savefig(f"histogram_{col}.png")  # Saves file as a .png
    plt.close()
print("Histograms saved successfully.")


# =====================================================================
# STEP 7: Plot Box Plots
# =====================================================================
print("\n--- STEP 7: GENERATING BOX PLOTS ---")
# FIXME: Replace these two strings with actual numeric column names from your data
cols_to_plot = ["Total_Spend", "Items_Purchased"]

for col in cols_to_plot:
    if col in df.columns:
        plt.figure()
        sns.boxplot(y=df[col])
        plt.title(f"Box Plot of {col}")
        plt.tight_layout()
        plt.savefig(f"boxplot_{col}.png")  # Saves file as a .png
        plt.close()
    else:
        print(f"Column '{col}' not found for box plot.")
print("Box plots saved successfully.")


# =====================================================================
# BONUS STEP: Pairplot
# =====================================================================
print("\n--- BONUS STEP: GENERATING PAIRPLOT ---")
plt.figure()
sns.pairplot(df)
plt.tight_layout()
plt.savefig("bonus_pairplot.png")
plt.close()
print("Bonus pairplot saved successfully.")
# Observation comment: Highly correlated relationships appear linearly clustered.
