import os
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

# 1. FETCH API REQUESTS
url = "https://coingecko.com"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": "false",
}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    print("✅ Data fetched successfully!")
else:
    print(f"❌ Failed to fetch data: {response.status_code}")


# 2. COMPLETE EDA CHECKLIST
print("\n--- 📊 DATA SHAPE ---")
print(df.shape)

print("\n--- 🔍 NULL VALUES ---")
print(df.isnull().sum())

print("\n--- 📈 SUMMARY STATISTICS ---")
print(df.describe())

# Create a custom category for group comparison requirement
df["price_tier"] = pd.qcut(
    df["current_price"], q=2, labels=["Low Price Coin", "High Price Coin"]
)

print("\n--- 🗂️ VALUE COUNTS (Price Tiers) ---")
print(df["price_tier"].value_counts())


# 3. VISUALIZATION & CHART GENERATION
os.makedirs("charts", exist_ok=True)
sns.set_theme(style="whitegrid")

# Chart 1: Bar Chart (Top 10 Coins by Market Cap)
plt.figure(figsize=(10, 5))
sns.barplot(data=df.head(10), x="market_cap", y="name", palette="viridis")
plt.title("Top 10 Cryptocurrencies by Market Cap")
plt.xlabel("Market Capitalization (USD)")
plt.ylabel("Coin Name")
plt.tight_layout()
plt.savefig("charts/1_bar_chart.png")
plt.close()

# Chart 2: Histogram (Distribution of 24h Price Changes)
plt.figure(figsize=(10, 5))
sns.histplot(
    df["price_change_percentage_24h"].dropna(), bins=20, kde=True, color="blue"
)
plt.title("Distribution of 24h Price Change Percentages")
plt.xlabel("Price Change (%)")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("charts/2_histogram.png")
plt.close()

# Chart 3: Scatter Plot (Market Cap vs Total Volume)
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="market_cap", y="total_volume", alpha=0.7, color="g")
plt.xscale("log")
plt.yscale("log")
plt.title("Market Cap vs Total Volume (Log Scale)")
plt.xlabel("Market Cap (USD)")
plt.ylabel("Total Volume (USD)")
plt.tight_layout()
plt.savefig("charts/3_scatter_plot.png")
plt.close()

# Chart 4: Correlation Heatmap
plt.figure(figsize=(8, 6))
numeric_cols = [
    "current_price",
    "market_cap",
    "total_volume",
    "price_change_percentage_24h",
]
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap of Crypto Metrics")
plt.tight_layout()
plt.savefig("charts/4_heatmap.png")
plt.close()

# Chart 5 (Should): Box Plot (Group Comparison of Volatility by Price Tier)
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=df,
    x="price_tier",
    y="price_change_percentage_24h",
    palette="Set2",
    showfliers=False,
)
plt.title("24h Price Volatility Comparison by Price Tier")
plt.xlabel("Price Tier Category")
plt.ylabel("24h Price Change (%)")
plt.tight_layout()
plt.savefig("charts/5_box_plot_comparison.png")
plt.close()

# BONUS: Pairplot
plt.figure(figsize=(12, 10))
pair_plot = sns.pairplot(df[numeric_cols])
pair_plot.fig.suptitle(
    "Bonus: Pairplot of Key Cryptocurrency Metrics", y=1.02
)
pair_plot.savefig("charts/6_bonus_pairplot.png")
plt.close()

print("\n🎉 All 6 charts saved successfully in the './charts' folder!")
