import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ecommerce_sales.csv"
REPORTS = ROOT / "reports"
CHARTS = REPORTS / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["Order_Date"])

# ---------------- Cleaning ----------------
df = df.drop_duplicates(subset=["Order_ID"])
df["Discount"] = df["Discount"].fillna(0)
df = df.dropna(subset=["Customer_ID", "Product", "Category"])
df["Revenue"] = df["Revenue"].fillna(df["Quantity"] * df["Price"] * (1 - df["Discount"]))
df["Cost"] = df["Cost"].fillna(df["Revenue"] * 0.70)
df["Profit"] = df["Revenue"] - df["Cost"]

# ---------------- KPIs ----------------
total_revenue = df["Revenue"].sum()
total_profit = df["Profit"].sum()
orders = df["Order_ID"].nunique()
customers = df["Customer_ID"].nunique()
units = df["Quantity"].sum()
aov = total_revenue / orders
profit_margin = total_profit / total_revenue

print("\nKEY PERFORMANCE INDICATORS")
print(f"Revenue: ₹{total_revenue:,.2f}")
print(f"Profit: ₹{total_profit:,.2f}")
print(f"Orders: {orders:,}")
print(f"Customers: {customers:,}")
print(f"Units: {units:,}")
print(f"Average Order Value: ₹{aov:,.2f}")
print(f"Profit Margin: {profit_margin:.2%}")

# ---------------- Time analysis ----------------
df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
monthly = df.groupby("Month", as_index=False).agg(
    Revenue=("Revenue","sum"),
    Profit=("Profit","sum"),
    Orders=("Order_ID","nunique")
)

plt.figure(figsize=(11,5))
plt.plot(monthly["Month"], monthly["Revenue"], marker="o")
plt.xticks(rotation=45)
plt.title("Monthly Revenue")
plt.tight_layout()
plt.savefig(CHARTS / "monthly_revenue.png", dpi=160)
plt.close()

# ---------------- Category / product / region ----------------
category = df.groupby("Category", as_index=False).agg(
    Revenue=("Revenue","sum"), Profit=("Profit","sum"), Units=("Quantity","sum")
).sort_values("Revenue", ascending=False)

plt.figure(figsize=(9,5))
plt.barh(category["Category"], category["Revenue"])
plt.title("Revenue by Category")
plt.tight_layout()
plt.savefig(CHARTS / "category_revenue.png", dpi=160)
plt.close()

product = df.groupby("Product", as_index=False).agg(
    Revenue=("Revenue","sum"), Units=("Quantity","sum")
).sort_values("Revenue", ascending=False).head(10)

plt.figure(figsize=(10,5))
plt.barh(product["Product"], product["Revenue"])
plt.title("Top 10 Products by Revenue")
plt.tight_layout()
plt.savefig(CHARTS / "top_products.png", dpi=160)
plt.close()

region = df.groupby("Region", as_index=False).agg(
    Revenue=("Revenue","sum"), Profit=("Profit","sum")
).sort_values("Revenue", ascending=False)

# ---------------- RFM ----------------
snapshot = df["Order_Date"].max() + pd.Timedelta(days=1)
rfm = df.groupby("Customer_ID").agg(
    Recency=("Order_Date", lambda x: (snapshot - x.max()).days),
    Frequency=("Order_ID", "nunique"),
    Monetary=("Revenue", "sum")
).reset_index()

rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

def segment(score):
    if score >= 13: return "VIP"
    if score >= 10: return "Loyal"
    if score >= 7: return "Potential"
    if score >= 5: return "At Risk"
    return "Inactive"

rfm["Segment"] = rfm["RFM_Score"].apply(segment)
rfm.to_csv(DATA.parent / "rfm_customers.csv", index=False)

# ---------------- Outlier detection ----------------
q1, q3 = df["Revenue"].quantile([.25,.75])
iqr = q3 - q1
lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
outliers = df[(df["Revenue"] < lower) | (df["Revenue"] > upper)]

# ---------------- Business insights ----------------
best_category = category.iloc[0]
best_product = product.iloc[0]
best_region = region.iloc[0]
best_month = monthly.loc[monthly["Revenue"].idxmax()]
best_segment = rfm["Segment"].value_counts().idxmax()

insights = pd.DataFrame({
    "Metric": [
        "Best Category", "Best Product (Top 10)", "Best Region",
        "Best Revenue Month", "Largest Customer Segment",
        "Revenue Outlier Transactions"
    ],
    "Value": [
        best_category["Category"],
        best_product["Product"],
        best_region["Region"],
        best_month["Month"],
        best_segment,
        len(outliers)
    ]
})
insights.to_csv(REPORTS / "business_insights.csv", index=False)

print("\nTOP BUSINESS INSIGHTS")
print(insights.to_string(index=False))
print("\nAnalysis complete. Reports saved in reports/.")
