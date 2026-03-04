import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Forecast", layout="wide", page_icon="📊")

from pages.Sidebar_style import inject_sidebar
inject_sidebar("Forecast")

st.markdown("""
<style>
.block-container { padding-top: 0.8rem !important; padding-bottom: 1rem !important; }
.metric-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
    border-radius: 12px; padding: 20px 24px; color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15); margin-bottom: 10px;
}
.metric-card .label { font-size: 13px; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.metric-card .value { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }
.metric-card .sub   { font-size: 12px; opacity: 0.65; margin-top: 4px; }
.section-title { font-size: 14px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 1px; margin: 18px 0 8px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📊 Forecast")
st.caption("Stock forecast and days of supply analysis")
st.divider()

@st.cache_data
def load_data():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    xl = pd.ExcelFile(file_path)
    sheet = next((s for s in xl.sheet_names if s.lower() == "forecast"), None)
    if not sheet:
        st.error("Forecast sheet not found in Excel file.")
        return pd.DataFrame()
    df_fc = pd.read_excel(file_path, sheet_name=sheet)
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"]
    for col in ["Forecast", "Norm", "Per day Req"]:
        if col in df_fc.columns:
            df_fc[col] = pd.to_numeric(df_fc[col], errors="coerce").fillna(0)
    if "Forecast" in df_fc.columns:
        df_fc = df_fc[df_fc["Forecast"] > 0]
    df_rm = pd.read_excel(file_path, sheet_name="RM-Inventory")
    df_rm.columns = df_rm.columns.str.strip()
    df_rm["Warehouse"] = df_rm["Warehouse"].astype(str).str.strip()
    df_rm["Qty Available"] = pd.to_numeric(df_rm["Qty Available"], errors="coerce").fillna(0)
    soh_warehouses = [
        "Central", "RM Warehouse Tumkur", "Central Warehouse - Cold Storage RM",
        "Tumkur Warehouse", "Tumkur New Warehouse",
        "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
    ]
    df_soh = df_rm[df_rm["Warehouse"].isin(soh_warehouses)]
    soh_by_sku = df_soh.groupby("Item SKU")["Qty Available"].sum().reset_index()
    soh_by_sku.columns = ["Item SKU", "SOH"]
    if "Item code" in df_fc.columns:
        df_fc["Item code"] = df_fc["Item code"].astype(str).str.strip()
        df_fc = df_fc.merge(soh_by_sku, left_on="Item code", right_on="Item SKU", how="left")
        df_fc["SOH"] = df_fc["SOH"].fillna(0)
        df_fc["Days of Stock"] = df_fc.apply(
            lambda r: round(r["SOH"] / (r["Forecast"] / 26), 1) if r["Forecast"] > 0 else None, axis=1)
    return df_fc

df = load_data()

f1, f2 = st.columns([3, 2])
with f1:
    search = st.text_input("Search", label_visibility="collapsed",
                           placeholder="Search item code / product name...")
with f2:
    dos_filter = st.selectbox("Days of Stock",
                              ["All", "Critical (< 7 days)", "Low (7-14 days)", "Healthy (> 14 days)"])

if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]
if dos_filter == "Critical (< 7 days)" and "Days of Stock" in df.columns:
    df = df[df["Days of Stock"] < 7]
elif dos_filter == "Low (7-14 days)" and "Days of Stock" in df.columns:
    df = df[(df["Days of Stock"] >= 7) & (df["Days of Stock"] <= 14)]
elif dos_filter == "Healthy (> 14 days)" and "Days of Stock" in df.columns:
    df = df[df["Days of Stock"] > 14]

total_forecast = df["Forecast"].sum()             if "Forecast" in df.columns else 0
total_soh      = df["SOH"].sum()                  if "SOH" in df.columns else 0
total_per_day  = df["Per day Req"].sum()          if "Per day Req" in df.columns else 0
critical_count = (df["Days of Stock"] < 7).sum()  if "Days of Stock" in df.columns else 0
total_items    = df["Item code"].nunique()         if "Item code" in df.columns else len(df)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Total Forecast</div>
        <div class="value">{total_forecast:,.0f}</div>
        <div class="sub">{total_items:,} unique items</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card" style="background:linear-gradient(135deg,#1a5c38,#27855a);">
        <div class="label">Total SOH</div>
        <div class="value">{total_soh:,.0f}</div>
        <div class="sub">From SOH warehouses</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card" style="background:linear-gradient(135deg,#4a2070,#6d35a0);">
        <div class="label">Total Per Day Req</div>
        <div class="value">{total_per_day:,.0f}</div>
        <div class="sub">Daily requirement</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card" style="background:linear-gradient(135deg,#7b2d2d,#b94040);">
        <div class="label">Critical (&lt; 7 Days)</div>
        <div class="value">{critical_count:,}</div>
        <div class="sub">Urgent replenishment needed</div></div>""", unsafe_allow_html=True)

st.divider()
st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)

def highlight_rows(row):
    if "Days of Stock" in row.index:
        if pd.notna(row["Days of Stock"]) and row["Days of Stock"] < 7:
            return ["background-color: #ffd6d6"] * len(row)
        elif pd.notna(row["Days of Stock"]) and row["Days of Stock"] <= 14:
            return ["background-color: #fff3cd"] * len(row)
    return [""] * len(row)

if "Item SKU" in df.columns:
    df = df.drop(columns=["Item SKU"], errors="ignore")

st.dataframe(
    df.style.apply(highlight_rows, axis=1),
    use_container_width=True, hide_index=True, height=500,
    column_config={
        "Forecast":      st.column_config.NumberColumn("Forecast",      format="%.0f"),
        "SOH":           st.column_config.NumberColumn("SOH",           format="%.0f"),
        "Per day Req":   st.column_config.NumberColumn("Per Day Req",   format="%.1f"),
        "Days of Stock": st.column_config.NumberColumn("Days of Stock", format="%.1f"),
        "Norm":          st.column_config.NumberColumn("Norm",          format="%.0f"),
    }
)
st.caption("🔴 Red = Critical < 7 days  |  🟡 Yellow = Low 7–14 days  |  ✅ White = Healthy > 14 days")
