import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

st.set_page_config(page_title="GRN Data", layout="wide", page_icon="📥")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #F8FAFC !important; }

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: 2px 0 12px rgba(15,23,42,0.05) !important;
}
[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important; margin: 2px 8px !important;
    padding: 8px 12px !important; font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebarNavLink"]:hover { background: #EBF2FF !important; color: #1A56DB !important; }
[data-testid="stSidebarNavLink"][aria-selected="true"] {
    background: #EBF2FF !important; color: #1A56DB !important;
    font-weight: 600 !important; border-left: 3px solid #1A56DB !important;
}
.main .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1280px !important; }
.stButton > button {
    background: #1A56DB !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.875rem !important;
    transition: all 0.15s ease !important; box-shadow: 0 1px 3px rgba(26,86,219,0.25) !important;
}
.stButton > button:hover {
    background: #1140A8 !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(26,86,219,0.30) !important;
}
.stTextInput > div > div > input {
    background: #fff !important; border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important; box-shadow: 0 1px 2px rgba(15,23,42,0.04) !important;
}
.stTextInput > div > div > input:focus {
    border-color: #93C5FD !important; box-shadow: 0 0 0 3px rgba(147,197,253,0.3) !important;
}
.stSelectbox > div > div {
    background: #fff !important; border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}
[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid #E2E8F0 !important; box-shadow: 0 1px 4px rgba(15,23,42,0.06) !important;
}
[data-testid="stDataFrame"] th {
    background: #F1F5F9 !important; font-weight: 600 !important; font-size: 0.75rem !important;
    text-transform: uppercase !important; letter-spacing: 0.05em !important; color: #475569 !important;
}
[data-testid="stDataFrame"] td { font-family: 'DM Mono', monospace !important; font-size: 0.82rem !important; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def stat_card(label, value, sub="", color="#1A56DB", icon=""):
    return f"""
    <div style="background:linear-gradient(135deg,{color} 0%,{color}cc 100%);
                border-radius:14px;padding:1.4rem 1.6rem;color:#fff;
                box-shadow:0 6px 20px {color}40;margin-bottom:1rem;">
        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                    text-transform:uppercase;opacity:0.8;margin-bottom:0.4rem;">{icon} {label}</div>
        <div style="font-size:2rem;font-weight:800;letter-spacing:-0.03em;
                    line-height:1.1;margin-bottom:0.25rem;">{value}</div>
        <div style="font-size:0.78rem;opacity:0.7;">{sub}</div>
    </div>"""

def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid #E2E8F0;">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.3rem;">
            <span style="font-size:1.8rem;line-height:1;">{icon}</span>
            <h1 style="margin:0;font-family:'DM Sans',sans-serif;font-size:1.75rem;
                       font-weight:700;color:#0F172A;letter-spacing:-0.02em;">{title}</h1>
        </div>
        <p style="margin:0;font-size:0.875rem;color:#94A3B8;padding-left:2.6rem;">{subtitle}</p>
    </div>""", unsafe_allow_html=True)

def section_label(text):
    st.markdown(f"""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                text-transform:uppercase;color:#94A3B8;margin-bottom:0.3rem;">{text}</div>""",
                unsafe_allow_html=True)

def fmt(n):
    return f"{int(n):,}"

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# Replace this section with your actual data source (DB, CSV, API, etc.)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_grn_data():
    np.random.seed(42)
    n = 200

    vendors   = ["Alpha Supplies", "Beta Traders", "Gamma Corp", "Delta Goods", "Epsilon Ltd"]
    warehouses= ["Mumbai WH", "Delhi WH", "Bangalore WH", "Chennai WH", "Hyderabad WH"]
    statuses  = ["Received", "Pending", "Partial", "Rejected"]

    grn_nos   = [f"GRN-{2024000 + i}" for i in range(n)]
    po_nos    = [f"PO-{10000 + np.random.randint(0, 50)}" for _ in range(n)]
    dates     = [date(2024, 1, 1) + timedelta(days=int(d)) for d in np.random.randint(0, 365, n)]
    qty_ord   = np.random.randint(500, 50000, n)
    qty_recv  = [int(q * np.random.uniform(0.4, 1.0)) for q in qty_ord]
    qty_rej   = [int(r * np.random.uniform(0, 0.05)) for r in qty_recv]
    qty_pend  = [o - r for o, r in zip(qty_ord, qty_recv)]

    df = pd.DataFrame({
        "GRN No"        : grn_nos,
        "PO Number"     : po_nos,
        "Vendor"        : np.random.choice(vendors, n),
        "Warehouse"     : np.random.choice(warehouses, n),
        "GRN Date"      : dates,
        "Qty Ordered"   : qty_ord,
        "Qty Received"  : qty_recv,
        "Qty Pending"   : qty_pend,
        "Qty Rejected"  : qty_rej,
        "Status"        : np.random.choice(statuses, n, p=[0.5, 0.25, 0.15, 0.1]),
    })
    return df

df_full = load_grn_data()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
page_header("📥", "GRN Data", "Goods Receipt Note tracking & analysis")

# ─────────────────────────────────────────────────────────────────────────────
# FILTERS — Row 1: search + dropdowns
# ─────────────────────────────────────────────────────────────────────────────
section_label("Search & Filter")

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    search_grn = st.text_input("", placeholder="🔍  Search GRN / PO…", label_visibility="collapsed")
with col2:
    po_options = ["All POs"] + sorted(df_full["PO Number"].unique().tolist())
    po_number  = st.selectbox("PO Number", po_options, label_visibility="visible")
with col3:
    vendor_options = ["All Vendors"] + sorted(df_full["Vendor"].unique().tolist())
    vendor         = st.selectbox("Vendor", vendor_options)
with col4:
    wh_options = ["All Warehouses"] + sorted(df_full["Warehouse"].unique().tolist())
    warehouse  = st.selectbox("Warehouse", wh_options)

# ── Row 2: Date range + Status ────────────────────────────────────────────────
col5, col6, col7 = st.columns([2, 2, 2])
with col5:
    min_date = df_full["GRN Date"].min()
    max_date = df_full["GRN Date"].max()
    date_from = st.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
with col6:
    date_to = st.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)
with col7:
    status_options = ["All Statuses"] + sorted(df_full["Status"].unique().tolist())
    status_filter  = st.selectbox("Status", status_options)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
df = df_full.copy()

if search_grn:
    mask = (
        df["GRN No"].str.contains(search_grn, case=False, na=False) |
        df["PO Number"].str.contains(search_grn, case=False, na=False)
    )
    df = df[mask]

if po_number != "All POs":
    df = df[df["PO Number"] == po_number]

if vendor != "All Vendors":
    df = df[df["Vendor"] == vendor]

if warehouse != "All Warehouses":
    df = df[df["Warehouse"] == warehouse]

if status_filter != "All Statuses":
    df = df[df["Status"] == status_filter]

# Date range filter
df = df[(df["GRN Date"] >= date_from) & (df["GRN Date"] <= date_to)]

# ─────────────────────────────────────────────────────────────────────────────
# STAT CARDS  (computed from filtered data)
# ─────────────────────────────────────────────────────────────────────────────
total_ordered  = df["Qty Ordered"].sum()
total_received = df["Qty Received"].sum()
total_pending  = df["Qty Pending"].sum()
total_rejected = df["Qty Rejected"].sum()
grn_count      = len(df)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(stat_card("Total QTY Ordered",  fmt(total_ordered),  f"{grn_count} GRNs",            "#1A56DB", "📋"), unsafe_allow_html=True)
with c2:
    st.markdown(stat_card("Total QTY Received", fmt(total_received), "Against ordered qty",           "#16A34A", "✅"), unsafe_allow_html=True)
with c3:
    st.markdown(stat_card("Pending QTY",        fmt(total_pending),  "Yet to be received",            "#B45309", "⏳"), unsafe_allow_html=True)
with c4:
    st.markdown(stat_card("Total QTY Rejected", fmt(total_rejected), "Rejection across GRNs",         "#DC2626", "❌"), unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# GRN TABLE
# ─────────────────────────────────────────────────────────────────────────────
section_label(f"GRN Records — {grn_count} rows")

# Colour-code status column
def style_status(val):
    colors = {
        "Received": "background-color:#DCFCE7;color:#166534;font-weight:600",
        "Pending":  "background-color:#FEF9C3;color:#713F12;font-weight:600",
        "Partial":  "background-color:#DBEAFE;color:#1E40AF;font-weight:600",
        "Rejected": "background-color:#FEE2E2;color:#991B1B;font-weight:600",
    }
    return colors.get(val, "")

display_df = df.copy()
display_df["GRN Date"] = display_df["GRN Date"].astype(str)

styled = (
    display_df.style
    .applymap(style_status, subset=["Status"])
    .format({
        "Qty Ordered"  : "{:,}",
        "Qty Received" : "{:,}",
        "Qty Pending"  : "{:,}",
        "Qty Rejected" : "{:,}",
    })
)

st.dataframe(styled, use_container_width=True, hide_index=True, height=480)
