import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Dataset Generation
np.random.seed(42)
n_students = 50

names = [f"Student_{i}" for i in range(1, n_students + 1)]
study_hours = np.random.uniform(2, 20, n_students)
sleep_hours = np.random.uniform(5, 9, n_students)
attendance_pct = np.random.uniform(60, 100, n_students)

noise = np.random.normal(0, 5, n_students)
score = (study_hours * 2.5) + (attendance_pct * 0.4) + noise
score = np.clip(score, 0, 100)
passed = score >= 50

df = pd.DataFrame({
    'name': names,
    'study_hours': study_hours,
    'sleep_hours': sleep_hours,
    'attendance_pct': attendance_pct,
    'score': score,
    'passed': passed
})

# Save CSV Deliverable
df.to_csv('students.csv', index=False)
print("✅ Saved 'students.csv'")

# ----------------------------------------------------
# 🖥️ SECTION 1: EDA CHECKLIST & DESCRIPTIVE STATISTICS
# ----------------------------------------------------
print("\n--- EDA CHECKLIST ---")
print(df.info())

print("\n--- DESCRIPTIVE STATISTICS ---")
print(df.describe())

# Calculate Correlation Matrix (excluding the 'name' column)
numeric_df = df.drop(columns=['name'])
corr_matrix = numeric_df.corr()

# ----------------------------------------------------
# 🖥️ SECTION 2: CORRELATION MATRICES
# ----------------------------------------------------
print("\n--- CORRELATION MATRIX FOR REPORT ---")
print(corr_matrix)

print("\n--- TOP CORRELATIONS (BY ABSOLUTE VALUE) ---")
corr_pairs = corr_matrix.unstack()
corr_pairs = corr_pairs[corr_pairs.index.get_level_values(0) != corr_pairs.index.get_level_values(1)]
print(corr_pairs.abs().sort_values(ascending=False).head(6))

# ----------------------------------------------------
# 🖼️ SECTION 3: GENERATING VISUALIZATION DELIVERABLES
# ----------------------------------------------------
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix Heatmap')
plt.tight_layout()
plt.savefig('heatmap.png', dpi=300)
plt.close()
print("\n✅ Saved 'heatmap.png'")

plt.figure(figsize=(7, 5))
sns.scatterplot(data=df, x='study_hours', y='score', hue='passed', palette='Set1')
plt.title('Study Hours vs Final Score')
plt.tight_layout()
plt.savefig('scatter_study_vs_score.png', dpi=300)
plt.close()
print("✅ Saved 'scatter_study_vs_score.png'")

plt.figure(figsize=(7, 5))
sns.scatterplot(data=df, x='attendance_pct', y='score', hue='passed', palette='Set1')
plt.title('Attendance Percentage vs Final Score')
plt.tight_layout()
plt.savefig('scatter_attendance_vs_score.png', dpi=300)
plt.close()
print("✅ Saved 'scatter_attendance_vs_score.png'")

pairplot_fig = sns.pairplot(df.drop(columns=['name']), hue='passed', palette='Set1')
pairplot_fig.savefig('bonus_pairplot.png', dpi=300)
plt.close()
print("✅ Saved 'bonus_pairplot.png'")

print("\n🎉 Perfect! Everything is printed to the screen and all files are saved successfully!")
