import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="E-Commerce Analytics", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "ecommerce_sales.csv", parse_dates=["Order_Date"])
df = df.drop_duplicates(subset=["Order_ID"])
df["Discount"] = df["Discount"].fillna(0)
df["Revenue"] = df["Revenue"].fillna(df["Quantity"] * df["Price"] * (1 - df["Discount"]))
df["Cost"] = df["Cost"].fillna(df["Revenue"] * .70)
df["Profit"] = df["Revenue"] - df["Cost"]

st.title("📊 E-Commerce Sales & Customer Analytics")

st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))

filtered = df[df["Region"].isin(regions) & df["Category"].isin(categories)].copy()

revenue = filtered["Revenue"].sum()
profit = filtered["Profit"].sum()
orders = filtered["Order_ID"].nunique()
customers = filtered["Customer_ID"].nunique()
aov = revenue / orders if orders else 0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Revenue", f"₹{revenue:,.0f}")
c2.metric("Profit", f"₹{profit:,.0f}")
c3.metric("Orders", f"{orders:,}")
c4.metric("Customers", f"{customers:,}")
c5.metric("AOV", f"₹{aov:,.0f}")

filtered["Month"] = filtered["Order_Date"].dt.to_period("M").astype(str)
monthly = filtered.groupby("Month", as_index=False)["Revenue"].sum()
st.subheader("Revenue Trend")
st.plotly_chart(px.line(monthly, x="Month", y="Revenue", markers=True), use_container_width=True)

left, right = st.columns(2)
with left:
    cat = filtered.groupby("Category", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.subheader("Revenue by Category")
    st.plotly_chart(px.bar(cat, x="Category", y="Revenue"), use_container_width=True)

with right:
    prod = filtered.groupby("Product", as_index=False)["Revenue"].sum().nlargest(10, "Revenue")
    st.subheader("Top Products")
    st.plotly_chart(px.bar(prod, x="Revenue", y="Product", orientation="h"), use_container_width=True)

st.subheader("Regional Performance")
reg = filtered.groupby("Region", as_index=False).agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"))
st.dataframe(reg.sort_values("Revenue", ascending=False), use_container_width=True)

st.caption("Built with Python, Pandas and Streamlit.")
