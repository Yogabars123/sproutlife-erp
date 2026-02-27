import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="Replenishment Planner", layout="wide")

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .metric-card .label {
        font-size: 13px;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .metric-card .sub {
        font-size: 12px;
        opacity: 0.65;
        margin-top: 4px;
    }
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛒 Replenishment Planner")
st.caption("Items with less than 10 days of stock — auto-generated order suggestions")

@st.cache_data
def load_data():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")

    # RM Inventory
    df_rm = pd.read_excel(file_path, sheet_name="RM-Inventory")
    df_rm.columns = df_rm.columns.str.strip()
    df_rm["Warehouse"] = df_rm["Warehouse"].astype(str).str.strip()
    df_rm["Qty Available"] = pd.to_numeric(df_rm["Qty Available"], errors="coerce").fillna(0)

    # Forecast
    xl = pd.ExcelFile(file_path)
    sheet = next((s for s in xl.sheet_names if s.lower() == "forecast"), None)
    df_fc = pd.read_excel(file_path, sheet_name=sheet)
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"]
    df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]

    # Normalize item code column
    if "Item code" in df_fc.columns:
        df_fc = df_fc.rename(columns={"Item code": "Item Code"})
    df_fc["Item Code"] = df_fc["Item Code"].astype(str).str.strip().str.upper()

    return df_rm, df_fc[["Item Code", "Forecast"]].drop_duplicates(subset="Item Code")

df_rm, df_fc = load_data()

# SOH warehouses
soh_warehouses = [
    "Central", "RM Warehouse Tumkur", "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]

# Calculate SOH per SKU
df_soh = df_rm[df_rm["Warehouse"].isin(soh_warehouses)]
soh_by_sku = df_soh.groupby("Item SKU").agg(
    SOH=("Qty Available", "sum"),
    Item_Name=("Item Name", "first"),
    Category=("Category", "first"),
    UoM=("UoM", "first")
).reset_index()

# Merge forecast
soh_by_sku["_key"] = soh_by_sku["Item SKU"].astype(str).str.strip().str.upper()
df_fc["_key"] = df_fc["Item Code"].astype(str).str.strip().str.upper()
soh_by_sku = soh_by_sku.merge(df_fc[["_key", "Forecast"]], on="_key", how="inner")
soh_by_sku = soh_by_sku.drop(columns=["_key"])

# Calculate Days of Stock
soh_by_sku["Daily Req"] = soh_by_sku["Forecast"] / 26
soh_by_sku["Days of Stock"] = (soh_by_sku["SOH"] / soh_by_sku["Daily Req"]).round(1)

# Filter < 10 days
df_critical = soh_by_sku[soh_by_sku["Days of Stock"] < 10].copy()

# ---------------------------------------------------
# SLIDER — target days
# ---------------------------------------------------
st.divider()
target_days = st.slider(
    "🎯 Target Days of Stock (suggested order will bring stock up to this level)",
    min_value=10, max_value=90, value=30, step=5
)

# Suggested Order Qty = (Daily Req × target_days) - SOH
df_critical["Suggested Order Qty"] = (
    (df_critical["Daily Req"] * target_days) - df_critical["SOH"]
).clip(lower=0).round(0)

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------
st.divider()

total_critical    = len(df_critical)
total_order_qty   = df_critical["Suggested Order Qty"].sum()
most_urgent       = df_critical["Days of Stock"].min() if len(df_critical) > 0 else 0
zero_stock        = (df_critical["SOH"] <= 0).sum()

k1, _, _ = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #7b2d2d 0%, #b94040 100%);">
        <div class="label">Critical Items (< 10 Days)</div>
        <div class="value">{total_critical:,}</div>
        <div class="sub">Need immediate ordering</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------
# DISPLAY TABLE
# ---------------------------------------------------
r1, r2 = st.columns([6, 2])
with r1:
    st.markdown(f'<div class="section-title">📋 {len(df_critical):,} items need replenishment</div>', unsafe_allow_html=True)
with r2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_critical.to_excel(writer, index=False, sheet_name="Replenishment")
    st.download_button(
        label="⬇️ Download Order List",
        data=buffer.getvalue(),
        file_name="Replenishment_Plan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

display_cols = ["Item SKU", "Item_Name", "Category", "UoM", "SOH",
                "Forecast", "Daily Req", "Days of Stock", "Suggested Order Qty"]
display_cols = [c for c in display_cols if c in df_critical.columns]

def highlight_rows(row):
    if "Days of Stock" in row.index:
        if row["Days of Stock"] <= 0:
            return ["background-color: #ffd6d6"] * len(row)
        elif row["Days of Stock"] < 5:
            return ["background-color: #ffb3b3"] * len(row)
        elif row["Days of Stock"] < 10:
            return ["background-color: #fff3cd"] * len(row)
    return [""] * len(row)

df_show = df_critical[display_cols].sort_values("Days of Stock").rename(
    columns={"Item_Name": "Item Name"}
)

st.dataframe(
    df_show.style.apply(highlight_rows, axis=1),
    use_container_width=True,
    height=500,
    hide_index=True,
    column_config={
        "SOH": st.column_config.NumberColumn("SOH", format="%.2f"),
        "Forecast": st.column_config.NumberColumn("Forecast", format="%.0f"),
        "Daily Req": st.column_config.NumberColumn("Daily Req", format="%.2f"),
        "Days of Stock": st.column_config.NumberColumn("Days of Stock", format="%.1f"),
        "Suggested Order Qty": st.column_config.NumberColumn("Suggested Order Qty", format="%.0f"),
    }
)
st.caption("🔴 Dark Red = Zero stock  |  🟠 Red = < 5 days  |  🟡 Yellow = 5–10 days")
