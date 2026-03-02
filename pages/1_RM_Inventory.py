import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory",
    layout="wide",
    page_icon="📦"
)

# ─────────────────────────────────────────────
# LOAD DATA FROM GITHUB-UPLOADED EXCEL
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_excel(
        "Sproutlife Inventory.xlsx",
        sheet_name="RM-Inventory"   # 🔥 Only RM-Inventory sheet
    )
    df.columns = df.columns.str.strip()
    return df


df = load_data()

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=False)

st.markdown("## 📦 RM Inventory")
st.markdown("Live raw material stock")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")
st.markdown("### 🔎 Search & Filter")

# Search
search = st.text_input("Search item, code, or location...")

filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────

# Adjust these column names if needed
qty_column = "Stock" if "Stock" in df.columns else df.columns[-1]

total_qty = filtered_df[qty_column].sum()
total_records = len(filtered_df)

st.markdown("### 📊 Summary")

c1, c2 = st.columns(2)

with c1:
    st.metric("Total Quantity", f"{total_qty:,.0f}")

with c2:
    st.metric("Total Records", total_records)

st.markdown("---")
st.markdown("### 📋 RM Inventory Records")

if filtered_df.empty:
    st.warning("No records found.")
else:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
