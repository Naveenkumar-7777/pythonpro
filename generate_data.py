import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)
N = 20000
out = Path(__file__).resolve().parents[1] / "data"
out.mkdir(exist_ok=True)

dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
customers = [f"C{n:05d}" for n in range(1, 4001)]

catalog = {
    "Electronics": [("Laptop", 60000), ("Smartphone", 30000), ("Headphones", 2500), ("Keyboard", 1800), ("Monitor", 12000)],
    "Fashion": [("Shoes", 2500), ("Jeans", 1800), ("T-Shirt", 900), ("Jacket", 3500), ("Backpack", 2200)],
    "Home": [("Chair", 4500), ("Table Lamp", 1600), ("Cookware", 3000), ("Bedsheet", 1800), ("Storage Box", 900)],
    "Books": [("Python Book", 900), ("Business Book", 700), ("Novel", 500), ("Data Science Book", 1200), ("Finance Book", 800)],
    "Sports": [("Running Shoes", 3200), ("Yoga Mat", 1200), ("Dumbbells", 2500), ("Football", 900), ("Cricket Bat", 2800)]
}
regions = ["North", "South", "East", "West"]
payments = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking"]

rows = []
for i in range(N):
    category = np.random.choice(list(catalog), p=[.32, .25, .18, .12, .13])
    product, base_price = catalog[category][np.random.randint(len(catalog[category]))]
    qty = np.random.choice([1,2,3,4,5], p=[.55,.25,.12,.06,.02])
    discount = np.random.choice([0,.05,.10,.15,.20], p=[.35,.25,.20,.15,.05])
    price = round(base_price * np.random.uniform(.92, 1.08), 2)
    rows.append([
        f"O{i+1:06d}",
        np.random.choice(dates),
        np.random.choice(customers),
        product,
        category,
        qty,
        price,
        discount,
        np.random.choice(regions),
        np.random.choice(payments)
    ])

df = pd.DataFrame(rows, columns=[
    "Order_ID","Order_Date","Customer_ID","Product","Category",
    "Quantity","Price","Discount","Region","Payment_Method"
])

df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Revenue"] = (df["Quantity"] * df["Price"] * (1 - df["Discount"])).round(2)
df["Cost"] = (df["Revenue"] * np.random.uniform(.55, .82, N)).round(2)
df["Profit"] = (df["Revenue"] - df["Cost"]).round(2)

# Add a few realistic data-quality issues for the cleaning phase.
df.loc[np.random.choice(df.index, 30, replace=False), "Discount"] = np.nan
df = pd.concat([df, df.iloc[:20]], ignore_index=True)

df.to_csv(out / "ecommerce_sales.csv", index=False)
print(f"Created {len(df):,} rows at {out/'ecommerce_sales.csv'}")
