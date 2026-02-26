import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

st.set_page_config(page_title="FG Inventory", layout="wide")

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a5c38 0%, #27855a 100%);
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
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_fg():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="FG-Inventory")
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)", "Value (Inc Tax)", "Value (Ex Tax)", "Current Aging (Days)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

df_raw = load_fg()

# CALCULATE SHELF LIFE
today = pd.Timestamp(datetime.today().date())

if "Expiry Date" in df_raw.columns and "MFG Date" in df_raw.columns:
    remaining_days = (df_raw["Expiry Date"] - today).dt.days
    total_days = (df_raw["Expiry Date"] - df_raw["MFG Date"]).dt.days

    # Remaining shelf life as percentage
    df_raw["Remaining Shelf Life (%)"] = ((remaining_days / total_days) * 100).round(1).clip(0, 100)
    df_raw["Remaining Shelf Life (%)"] = df_raw["Remaining Shelf Life (%)"].fillna(0)

    # Keep days for filtering logic internally
    df_raw["_remaining_days"] = remaining_days.fillna(0).astype(int)

# HEADER
st.title("📦 FG Inventory")
st.caption("Live view of finished goods stock across all warehouses")

col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# FILTERS
st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([3, 2, 2, 2])

with f1:
    search = st.text_input("Search (Item Name / SKU / Batch)", placeholder="Type to search...")
with f2:
    warehouse_options = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    selected_warehouse = st.selectbox("Warehouse", warehouse_options)
with f3:
    if "Category" in df_raw.columns:
        cat_options = ["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
        selected_category = st.selectbox("Category", cat_options)
    else:
        selected_category = "All Categories"
with f4:
    shelf_filter = st.selectbox("Shelf Life Status", [
        "All",
        "Expiring in 30 days",
        "Expiring in 60 days",
        "Expiring in 90 days",
        "Expired"
    ])

# APPLY FILTERS
df = df_raw.copy()

if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
    df = df[mask]

if selected_warehouse != "All Warehouses":
    df = df[df["Warehouse"] == selected_warehouse]

if selected_category != "All Categories" and "Category" in df.columns:
    df = df[df["Category"].astype(str) == selected_category]

if "_remaining_days" in df.columns:
    if shelf_filter == "Expiring in 30 days":
        df = df[(df["_remaining_days"] >= 0) & (df["_remaining_days"] <= 30)]
    elif shelf_filter == "Expiring in 60 days":
        df = df[(df["_remaining_days"] >= 0) & (df["_remaining_days"] <= 60)]
    elif shelf_filter == "Expiring in 90 days":
        df = df[(df["_remaining_days"] >= 0) & (df["_remaining_days"] <= 90)]
    elif shelf_filter == "Expired":
        df = df[df["_remaining_days"] < 0]

# KPI CARDS
st.divider()
total_qty = df["Qty Available"].sum() if "Qty Available" in df.columns else 0
expiring_soon = (df["_remaining_days"] <= 30).sum() if "_remaining_days" in df.columns else 0
expired_count = (df["_remaining_days"] < 0).sum() if "_remaining_days" in df.columns else 0

if selected_warehouse != "All Warehouses":
    card_label = f"Qty Available — {selected_warehouse}"
elif search:
    card_label = f"Qty Available — '{search}'"
elif selected_category != "All Categories":
    card_label = f"Qty Available — {selected_category}"
else:
    card_label = "Total Qty Available"

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">{card_label}</div>
        <div class="value">{total_qty:,.0f}</div>
        <div class="sub">{len(df):,} records matching filters</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #7b5a1a 0%, #b88a30 100%);">
        <div class="label">Expiring in 30 Days</div>
        <div class="value">{expiring_soon:,}</div>
        <div class="sub">Batches needing attention</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #7b2d2d 0%, #b94040 100%);">
        <div class="label">Expired Batches</div>
        <div class="value">{expired_count:,}</div>
        <div class="sub">Past expiry date</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# RESULTS COUNT + DOWNLOAD
r1, r2 = st.columns([6, 2])
with r1:
    st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)
with r2:
    buffer = io.BytesIO()
    # Remove internal column before export
    export_df = df.drop(columns=["_remaining_days"], errors="ignore")
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="FG Inventory")
    st.download_button(
        label="⬇️ Download as Excel",
        data=buffer.getvalue(),
        file_name="FG_Inventory_Filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# DISPLAY TABLE
if df.empty:
    st.warning("No records match your current filters.")
else:
    priority_cols = [
        "Item Name", "Item SKU", "Category", "Primary Category",
        "Warehouse", "Batch No", "UoM", "Qty Available", "Qty Inward",
        "Qty (Issue / Hold)", "MFG Date", "Expiry Date",
        "Remaining Shelf Life (%)",
        "Current Aging (Days)", "Value (Inc Tax)", "Value (Ex Tax)",
        "Inventory Date", "Item Type"
    ]
    display_cols = [c for c in priority_cols if c in df.columns]
    display_cols += [c for c in df.columns if c not in display_cols and c != "_remaining_days"]

    df_display = df[display_cols].copy()

    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].dt.strftime("%d-%b-%Y").fillna("")

    for col in ["Value (Inc Tax)", "Value (Ex Tax)"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"₹{x:,.2f}" if x else "")

    st.dataframe(
        df_display,
        use_container_width=True,
        height=500,
        hide_index=True,
        column_config={
            "Qty Available": st.column_config.NumberColumn("Qty Available", format="%.2f"),
            "Qty Inward": st.column_config.NumberColumn("Qty Inward", format="%.2f"),
            "Qty (Issue / Hold)": st.column_config.NumberColumn("Qty (Issue / Hold)", format="%.2f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging (Days)", format="%d"),
            "Remaining Shelf Life (%)": st.column_config.ProgressColumn(
                "Remaining Shelf Life (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
        }
    )
