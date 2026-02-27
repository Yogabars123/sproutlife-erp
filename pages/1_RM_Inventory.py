import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="RM Inventory", layout="centered")

# ---------------------------------------------------
# SIMPLE MOBILE TOGGLE (NO EXTRA LIBRARY)
# ---------------------------------------------------
mobile_mode = st.toggle("📱 Mobile View", value=True)

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

    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)",
                "Value (Inc Tax)", "Value (Ex Tax)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df_raw = load_rm()

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
search = st.text_input("🔍 Search item name, SKU or batch")

wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
selected_wh = st.selectbox("Warehouse", wh_opts)

stock_filter = st.selectbox("Stock Status",
                            ["All", "Available Only", "Zero / Negative Stock"])

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
df = df_raw.copy()

if search:
    df = df[df.astype(str).apply(
        lambda x: x.str.contains(search, case=False, na=False)
    ).any(axis=1)]

if selected_wh != "All Warehouses":
    df = df[df["Warehouse"] == selected_wh]

if stock_filter == "Available Only":
    df = df[df["Qty Available"] > 0]
elif stock_filter == "Zero / Negative Stock":
    df = df[df["Qty Available"] <= 0]

# ---------------------------------------------------
# KPI
# ---------------------------------------------------
total_qty = df["Qty Available"].sum()

st.markdown(f"""
<div class="kpi-box">
    <div class="kpi-label">Total Qty Available</div>
    <div class="kpi-value">{total_qty:,.0f}</div>
    <div class="kpi-sub">{len(df):,} records</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="RM")

st.download_button(
    "⬇️ Download Excel",
    buf.getvalue(),
    "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.divider()

# ---------------------------------------------------
# DISPLAY DATA
# ---------------------------------------------------
if df.empty:
    st.warning("No records found.")

else:

    if mobile_mode:
        # 📱 MOBILE CARD VIEW
        for _, row in df.iterrows():

            expiry = row.get("Expiry Date", "")
            if pd.notna(expiry):
                expiry = expiry.strftime("%d-%b-%Y")

            st.markdown(f"""
            <div style="
                background:#f8f9fa;
                padding:12px;
                border-radius:10px;
                margin-bottom:10px;
                border:1px solid #eee;">
                
                <b style="font-size:14px;">{row.get('Item Name','')}</b><br>
                SKU: {row.get('Item SKU','')}<br>
                Warehouse: {row.get('Warehouse','')}<br>
                Qty: <b>{row.get('Qty Available',0):,.0f}</b><br>
                Expiry: {expiry}
            </div>
            """, unsafe_allow_html=True)

    else:
        # 💻 DESKTOP TABLE
        df_show = df.copy()

        for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
            if col in df_show.columns:
                df_show[col] = df_show[col].dt.strftime("%d-%b-%Y").fillna("")

        st.dataframe(
            df_show,
            use_container_width=True,
            height=500,
            hide_index=True
        )
