import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="FG Inventory", layout="wide", page_icon="📦")

# ─────────────────────────────────────────────
# PROFESSIONAL KPI + MOBILE CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>

/* Reduce extra padding */
.block-container {
    padding-top: 1rem !important;
}

/* KPI Card */
.kpi-card {
    border-radius: 14px;
    padding: 18px 20px;
    color: white;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

.kpi-title {
    font-size: 13px;
    font-weight: 600;
    opacity: 0.85;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 800;
    margin-top: 6px;
}

.kpi-sub {
    font-size: 12px;
    opacity: 0.75;
    margin-top: 4px;
}

/* Section title */
.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 18px 0 8px 0;
}

/* Mobile Optimization */
@media (max-width: 768px) {
    div[data-testid="column"] {
        width: 100% !important;
        flex: 100% !important;
    }
    .kpi-value {
        font-size: 20px;
    }
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
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

    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)",
                "Value (Inc Tax)", "Value (Ex Tax)", "Current Aging (Days)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df_raw = load_fg()

# ─────────────────────────────────────────────
# SHELF LIFE CALCULATION
# ─────────────────────────────────────────────
today = pd.Timestamp(datetime.today().date())

if "Expiry Date" in df_raw.columns and "MFG Date" in df_raw.columns:
    remaining_days = (df_raw["Expiry Date"] - today).dt.days
    total_days = (df_raw["Expiry Date"] - df_raw["MFG Date"]).dt.days

    df_raw["Remaining Shelf Life (%)"] = ((remaining_days / total_days) * 100).round(1).clip(0, 100)
    df_raw["Remaining Shelf Life (%)"] = df_raw["Remaining Shelf Life (%)"].fillna(0)
    df_raw["_remaining_days"] = remaining_days.fillna(0).astype(int)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📦 FG Inventory")
st.caption("Live view of finished goods stock across all warehouses")

st.divider()

# ─────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns([3, 2, 2])

with f1:
    search = st.text_input("Search (Item / SKU / Batch)")
with f2:
    warehouse_options = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    selected_warehouse = st.selectbox("Warehouse", warehouse_options)
with f3:
    shelf_filter = st.selectbox("Shelf Life", [
        "All",
        "Expiring in 30 days",
        "Expired"
    ])

df = df_raw.copy()

if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
    df = df[mask]

if selected_warehouse != "All Warehouses":
    df = df[df["Warehouse"] == selected_warehouse]

if "_remaining_days" in df.columns:
    if shelf_filter == "Expiring in 30 days":
        df = df[(df["_remaining_days"] >= 0) & (df["_remaining_days"] <= 30)]
    elif shelf_filter == "Expired":
        df = df[df["_remaining_days"] < 0]

# ─────────────────────────────────────────────
# KPI CALCULATION
# ─────────────────────────────────────────────
total_qty = df["Qty Available"].sum()
expiring_soon = (df["_remaining_days"] <= 30).sum() if "_remaining_days" in df.columns else 0
expired_count = (df["_remaining_days"] < 0).sum() if "_remaining_days" in df.columns else 0

# ─────────────────────────────────────────────
# KPI DISPLAY (GRN STYLE)
# ─────────────────────────────────────────────
k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="kpi-card" style="background:linear-gradient(135deg,#1A56DB,#2563EB);">
        <div class="kpi-title">Available Quantity</div>
        <div class="kpi-value">{total_qty:,.0f}</div>
        <div class="kpi-sub">{len(df):,} filtered records</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card" style="background:linear-gradient(135deg,#F59E0B,#FBBF24);">
        <div class="kpi-title">Expiring in 30 Days</div>
        <div class="kpi-value">{expiring_soon:,}</div>
        <div class="kpi-sub">Requires attention</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card" style="background:linear-gradient(135deg,#DC2626,#EF4444);">
        <div class="kpi-title">Expired Batches</div>
        <div class="kpi-value">{expired_count:,}</div>
        <div class="kpi-sub">Past expiry date</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
if df.empty:
    st.warning("No records match your filters.")
else:
    st.dataframe(df, use_container_width=True, height=500, hide_index=True)
