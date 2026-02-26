import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

st.set_page_config(page_title="GRN Data", layout="wide")

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
    .po-summary-card {
        background: #f8f9fa;
        border-left: 4px solid #2d5986;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 8px;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_grn():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="GRN-Data")
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    df["PO No"] = df["PO No"].astype(str).str.strip()

    for col in ["GRN Date", "Delivery Date", "PO Date", "Invoice Date", "Expiry Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["Quantity Ordered", "Quantity Received", "Quantity Rejected",
                "Percentage Rejection", "Rate of Goods Received(₹)",
                "Values of Goods Received without taxes(₹)",
                "Values of Goods Received with taxes(₹)",
                "Values of Goods Rejected without taxes(₹)",
                "Values of Goods Rejected with taxes(₹)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df_raw = load_grn()

# ---------------------------------------------------
# FILTER: Central WH + Has PO Number
# ---------------------------------------------------
df_raw = df_raw[df_raw["Warehouse"].str.lower() == "central"]
df_raw = df_raw[
    df_raw["PO No"].notna() &
    (df_raw["PO No"] != "") &
    (df_raw["PO No"].str.upper() != "NAN") &
    (df_raw["PO No"].str.upper() != "NONE")
]

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("📋 GRN Data")
st.caption("Central Warehouse — Purchase Order wise GRN tracking")

col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------
st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([3, 2, 2, 2])

with f1:
    search = st.text_input("Search (Item Name / GRN No / Vendor)", placeholder="Type to search...")

with f2:
    po_options = ["All POs"] + sorted(df_raw["PO No"].dropna().unique().tolist())
    selected_po = st.selectbox("PO Number", po_options)

with f3:
    if "GRN Month" in df_raw.columns:
        month_options = ["All Months"] + sorted(df_raw["GRN Month"].dropna().unique().tolist())
        selected_month = st.selectbox("Month", month_options)
    else:
        selected_month = "All Months"

with f4:
    if "Vendor Name" in df_raw.columns:
        vendor_options = ["All Vendors"] + sorted(df_raw["Vendor Name"].dropna().unique().tolist())
        selected_vendor = st.selectbox("Vendor", vendor_options)
    else:
        selected_vendor = "All Vendors"

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
df = df_raw.copy()

if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
    df = df[mask]

if selected_po != "All POs":
    df = df[df["PO No"] == selected_po]

if selected_month != "All Months" and "GRN Month" in df.columns:
    df = df[df["GRN Month"] == selected_month]

if selected_vendor != "All Vendors" and "Vendor Name" in df.columns:
    df = df[df["Vendor Name"] == selected_vendor]

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------
st.divider()

total_ordered = df["Quantity Ordered"].sum() if "Quantity Ordered" in df.columns else 0
total_received = df["Quantity Received"].sum() if "Quantity Received" in df.columns else 0
total_pending = total_ordered - total_received
total_rejected = df["Quantity Rejected"].sum() if "Quantity Rejected" in df.columns else 0
total_grns = df["GRN No"].nunique() if "GRN No" in df.columns else len(df)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Qty Ordered</div>
        <div class="value">{total_ordered:,.0f}</div>
        <div class="sub">{total_grns:,} GRNs</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #1a5c38 0%, #27855a 100%);">
        <div class="label">Total Qty Received</div>
        <div class="value">{total_received:,.0f}</div>
        <div class="sub">Against ordered qty</div>
    </div>""", unsafe_allow_html=True)

with k3:
    pending_color = "#7b5a1a" if total_pending > 0 else "#1a5c38"
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, {pending_color} 0%, #b88a30 100%);">
        <div class="label">Pending Qty</div>
        <div class="value">{max(total_pending, 0):,.0f}</div>
        <div class="sub">Yet to be received</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #7b2d2d 0%, #b94040 100%);">
        <div class="label">Total Qty Rejected</div>
        <div class="value">{total_rejected:,.0f}</div>
        <div class="sub">Rejection across GRNs</div>
    </div>""", unsafe_allow_html=True)

# ---------------------------------------------------
# PO SUMMARY (when a specific PO is selected)
# ---------------------------------------------------
if selected_po != "All POs":
    st.divider()
    st.markdown(f'<div class="section-title">📦 PO Summary — {selected_po}</div>', unsafe_allow_html=True)

    po_df = df[df["PO No"] == selected_po]
    po_ordered = po_df["Quantity Ordered"].sum()
    po_received = po_df["Quantity Received"].sum()
    po_pending = max(po_ordered - po_received, 0)
    po_rejected = po_df["Quantity Rejected"].sum()
    po_value = po_df["Values of Goods Received with taxes(₹)"].sum() if "Values of Goods Received with taxes(₹)" in po_df.columns else 0
    fulfillment_pct = (po_received / po_ordered * 100) if po_ordered > 0 else 0

    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.metric("Ordered Qty", f"{po_ordered:,.0f}")
    with p2:
        st.metric("Received Qty", f"{po_received:,.0f}")
    with p3:
        st.metric("Pending Qty", f"{po_pending:,.0f}")
    with p4:
        st.metric("Rejected Qty", f"{po_rejected:,.0f}")
    with p5:
        st.metric("Fulfilment", f"{fulfillment_pct:.1f}%")

    st.progress(min(fulfillment_pct / 100, 1.0), text=f"PO Fulfilment: {fulfillment_pct:.1f}%")

# ---------------------------------------------------
# RESULTS COUNT + DOWNLOAD
# ---------------------------------------------------
st.divider()
r1, r2 = st.columns([6, 2])
with r1:
    st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)
with r2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="GRN Data")
    st.download_button(
        label="⬇️ Download as Excel",
        data=buffer.getvalue(),
        file_name="GRN_Data_Filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ---------------------------------------------------
# DISPLAY TABLE
# ---------------------------------------------------
if df.empty:
    st.warning("No records match your current filters.")
else:
    priority_cols = [
        "GRN No", "GRN Date", "GRN Month", "Vendor Name", "PO No", "PO Date",
        "Item Name", "Item Code", "Warehouse",
        "Quantity Ordered", "Quantity Received", "Quantity Rejected",
        "Percentage Rejection",
        "Values of Goods Received with taxes(₹)",
        "Values of Goods Received without taxes(₹)",
        "Values of Goods Rejected with taxes(₹)",
        "Rate of Goods Received(₹)",
        "Invoice No", "Invoice Date", "Delivery Date",
        "Expiry Date", "Batch No", "GRN Notes", "Type", "GRN Created By"
    ]
    display_cols = [c for c in priority_cols if c in df.columns]
    display_cols += [c for c in df.columns if c not in display_cols]

    df_display = df[display_cols].copy()

    for col in ["GRN Date", "Delivery Date", "PO Date", "Invoice Date", "Expiry Date"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].dt.strftime("%d-%b-%Y").fillna("")

    for col in ["Values of Goods Received with taxes(₹)", "Values of Goods Received without taxes(₹)",
                "Values of Goods Rejected with taxes(₹)", "Rate of Goods Received(₹)"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"₹{x:,.2f}" if x else "")

    st.dataframe(
        df_display,
        use_container_width=True,
        height=500,
        hide_index=True,
        column_config={
            "Quantity Ordered": st.column_config.NumberColumn("Qty Ordered", format="%.2f"),
            "Quantity Received": st.column_config.NumberColumn("Qty Received", format="%.2f"),
            "Quantity Rejected": st.column_config.NumberColumn("Qty Rejected", format="%.2f"),
            "Percentage Rejection": st.column_config.NumberColumn("Rejection %", format="%.1f%%"),
        }
    )
