import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="RM Inventory", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0.8rem 0.8rem 1rem 0.8rem !important;
        max-width: 100% !important;
    }
    .page-title {
        font-size: 18px;
        font-weight: 700;
        margin: 0 0 2px 0;
    }
    .page-sub {
        font-size: 11px;
        color: #888;
        margin: 0 0 10px 0;
    }
    .kpi-box {
        background: linear-gradient(135deg, #1e3a5f, #2d5986);
        border-radius: 10px;
        padding: 12px 16px;
        color: white;
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        opacity: 0.75;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 10px;
        opacity: 0.6;
        margin-top: 2px;
    }
    .sec-label {
        font-size: 11px;
        font-weight: 600;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 12px 0 6px 0;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        font-size: 12px !important;
    }
    .stTextInput input {
        font-size: 14px !important;
        padding: 8px 12px !important;
    }
    .stSelectbox > div > div {
        font-size: 13px !important;
        padding: 4px 8px !important;
    }
    .stButton button {
        font-size: 13px !important;
        padding: 4px 12px !important;
    }
    .stDownloadButton button {
        font-size: 12px !important;
        padding: 4px 10px !important;
    }
    hr {
        margin: 8px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_rm():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="RM-Inventory")
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)", "Value (Inc Tax)", "Value (Ex Tax)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_forecast():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    xl = pd.ExcelFile(file_path)
    sheet = next((s for s in xl.sheet_names if s.lower() == "forecast"), None)
    if not sheet:
        return pd.DataFrame(columns=["Item code", "Forecast"])
    df = pd.read_excel(file_path, sheet_name=sheet)
    df.columns = df.columns.str.strip()
    if "Location" in df.columns:
        df = df[df["Location"].astype(str).str.strip().str.lower() == "plant"]
    if "Forecast" in df.columns:
        df["Forecast"] = pd.to_numeric(df["Forecast"], errors="coerce").fillna(0)
        df = df[df["Forecast"] > 0]
    ic = "Item code" if "Item code" in df.columns else "Item Code"
    df[ic] = df[ic].astype(str).str.strip()
    return df[[ic, "Forecast"]].rename(columns={ic: "Item code"}).drop_duplicates(subset="Item code")

df_raw = load_rm()
df_forecast = load_forecast()

allowed_warehouses = [
    "Central", "Central Production -Bar Line", "Central Production - Oats Line",
    "Central Production - Peanut Line", "Central Production - Muesli Line",
    "RM Warehouse Tumkur", "Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM", "Tumkur Warehouse",
    "Central Production -Packing", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]
df_raw = df_raw[df_raw["Warehouse"].isin(allowed_warehouses)]

soh_warehouses = [
    "Central", "RM Warehouse Tumkur", "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]
df_soh = df_raw[df_raw["Warehouse"].isin(soh_warehouses)]
soh_by_sku = df_soh.groupby("Item SKU")["Qty Available"].sum().reset_index()
soh_by_sku.columns = ["Item SKU", "SOH"]
soh_by_sku["_key"] = soh_by_sku["Item SKU"].astype(str).str.upper()
df_forecast["_key"] = df_forecast["Item code"].astype(str).str.upper()
soh_by_sku = soh_by_sku.merge(df_forecast[["_key", "Forecast"]], on="_key", how="left")
soh_by_sku["Forecast"] = soh_by_sku["Forecast"].fillna(0)
soh_by_sku["Days of Stock"] = soh_by_sku.apply(
    lambda r: round(r["SOH"] / (r["Forecast"] / 26), 1) if r["Forecast"] > 0 else None, axis=1
)
soh_by_sku = soh_by_sku.drop(columns=["_key"])

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown('<p class="page-title">📦 RM Inventory</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Live raw material stock</p>', unsafe_allow_html=True)
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.divider()

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------
search = st.text_input("🔍 Search item name, SKU or batch", placeholder="e.g. 10704 or Flakes")
wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
selected_wh = st.selectbox("Warehouse", wh_opts)
cat_opts = ["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist()) if "Category" in df_raw.columns else ["All Categories"]
selected_cat = st.selectbox("Category", cat_opts)
stock_filter = st.selectbox("Stock Status", ["All", "Available Only", "Zero / Negative Stock"])

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if selected_wh != "All Warehouses":
    df = df[df["Warehouse"] == selected_wh]
if selected_cat != "All Categories" and "Category" in df.columns:
    df = df[df["Category"].astype(str) == selected_cat]
if stock_filter == "Available Only":
    df = df[df["Qty Available"] > 0]
elif stock_filter == "Zero / Negative Stock":
    df = df[df["Qty Available"] <= 0]

# ---------------------------------------------------
# KPI
# ---------------------------------------------------
st.divider()
soh_wh = ["Central","RM Warehouse Tumkur","Central Warehouse - Cold Storage RM",
          "Tumkur Warehouse","Tumkur New Warehouse","HF Factory FG Warehouse",
          "Sproutlife Foods Private Ltd (SNOWMAN)"]
total_qty = df[df["Warehouse"].isin(soh_wh)]["Qty Available"].sum()

if selected_wh != "All Warehouses":
    label = f"Qty — {selected_wh}"
elif search:
    label = f"Qty — '{search}'"
elif selected_cat != "All Categories":
    label = f"Qty — {selected_cat}"
else:
    label = "Total Qty Available"

st.markdown(f"""
<div class="kpi-box">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{total_qty:,.0f}</div>
    <div class="kpi-sub">{len(df):,} records</div>
</div>""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------
# TABLE
# ---------------------------------------------------
st.markdown(f'<div class="sec-label">📋 {len(df):,} records</div>', unsafe_allow_html=True)
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="RM")
st.download_button("⬇️ Download Excel", buf.getvalue(), "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)

if df.empty:
    st.warning("No records found.")
else:
    df_m = df.merge(soh_by_sku[["Item SKU","Forecast","Days of Stock"]], on="Item SKU", how="left")
    priority = ["Item Name","Item SKU","Category","Warehouse","UoM",
                "Qty Available","Forecast","Days of Stock",
                "Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)",
                "Batch No","MFG Date","Expiry Date","Current Aging (Days)"]
    cols = [c for c in priority if c in df_m.columns]
    cols += [c for c in df_m.columns if c not in cols]
    df_show = df_m[cols].copy()
    for col in ["Inventory Date","Expiry Date","MFG Date"]:
        if col in df_show.columns:
            df_show[col] = df_show[col].dt.strftime("%d-%b-%Y").fillna("")
    st.dataframe(df_show, use_container_width=True, height=400, hide_index=True,
        column_config={
            "Qty Available": st.column_config.NumberColumn("Qty Avail", format="%.0f"),
            "Forecast": st.column_config.NumberColumn("Forecast", format="%.0f"),
            "Days of Stock": st.column_config.NumberColumn("DoS", format="%.1f"),
            "Qty Inward": st.column_config.NumberColumn("Inward", format="%.0f"),
            "Qty (Issue / Hold)": st.column_config.NumberColumn("Issue/Hold", format="%.0f"),
            "Value (Inc Tax)": st.column_config.NumberColumn("Value", format="%.0f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging", format="%d"),
        })
