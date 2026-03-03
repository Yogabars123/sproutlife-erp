import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GRN Data", layout="wide", page_icon="📥")

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #F8FAFC !important; }
[data-testid="stSidebar"] {
    background: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important;
    box-shadow: 2px 0 12px rgba(15,23,42,0.05) !important;
}
[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important; margin: 2px 8px !important;
    padding: 8px 12px !important; font-weight: 500 !important;
}
[data-testid="stSidebarNavLink"]:hover { background: #EBF2FF !important; color: #1A56DB !important; }
[data-testid="stSidebarNavLink"][aria-selected="true"] {
    background: #EBF2FF !important; color: #1A56DB !important;
    font-weight: 600 !important; border-left: 3px solid #1A56DB !important;
}
.main .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px !important; }
.stButton > button {
    background: #1A56DB !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.875rem !important;
    box-shadow: 0 1px 3px rgba(26,86,219,0.25) !important;
}
.stButton > button:hover {
    background: #1140A8 !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(26,86,219,0.30) !important;
}
.stTextInput > div > div > input, .stSelectbox > div > div {
    background: #fff !important; border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important; font-size: 0.875rem !important;
}
[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid #E2E8F0 !important; box-shadow: 0 1px 4px rgba(15,23,42,0.06) !important;
}
#MainMenu { visibility: hidden; } footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
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
            <h1 style="margin:0;font-size:1.75rem;font-weight:700;color:#0F172A;
                       letter-spacing:-0.02em;">{title}</h1>
        </div>
        <p style="margin:0;font-size:0.875rem;color:#94A3B8;padding-left:2.6rem;">{subtitle}</p>
    </div>""", unsafe_allow_html=True)

def section_label(text):
    st.markdown(f"""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                text-transform:uppercase;color:#94A3B8;margin-bottom:0.4rem;">{text}</div>""",
                unsafe_allow_html=True)

def fmt(n):
    return f"{n:,.0f}"

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING  — reads directly from SharePoint via Office365-REST-Python-Client
# pip install Office365-REST-Python-Client openpyxl
# ─────────────────────────────────────────────────────────────────────────────
import io, os

SHAREPOINT_SITE  = "https://sproutlife01-my.sharepoint.com/personal/abinaya_m_yogabars_in"
FILE_RELATIVE    = "/personal/abinaya_m_yogabars_in/Documents/Sproutlife Inventory.xlsx"
SHEET_NAME       = "GRN-Data"

# ── Credentials: set these as environment variables (never hard-code passwords)
#    In your terminal before running streamlit:
#      set SP_USER=abinaya_m@yogabars.in
#      set SP_PASS=your_password
SP_USER = os.environ.get("SP_USER", "")
SP_PASS = os.environ.get("SP_PASS", "")

@st.cache_data(ttl=300)
def load_grn_data():
    if not SP_USER or not SP_PASS:
        st.error("❌ Please set SP_USER and SP_PASS environment variables before running.")
        st.info("In your terminal run:\n`set SP_USER=your@email.com`\n`set SP_PASS=yourpassword`\nthen restart Streamlit.")
        st.stop()

    try:
        from office365.sharepoint.client_context import ClientContext
        from office365.runtime.auth.user_credential import UserCredential
    except ImportError:
        st.error("❌ Missing package. Run: `pip install Office365-REST-Python-Client`")
        st.stop()

    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(UserCredential(SP_USER, SP_PASS))
    file_obj = ctx.web.get_file_by_server_relative_url(FILE_RELATIVE)
    download = file_obj.download_session()
    ctx.execute_query()
    buf = io.BytesIO(download.read())

    df = pd.read_excel(buf, sheet_name=SHEET_NAME, engine="openpyxl")

    # ── Normalise column names (strip spaces) ────────────────────────────────
    df.columns = df.columns.str.strip()

    # ── Parse date ───────────────────────────────────────────────────────────
    df["GRN Date"] = pd.to_datetime(df["GRN Date"], errors="coerce").dt.date

    # ── Numeric cols ─────────────────────────────────────────────────────────
    for col in ["QuantityOrdered", "QuantityReceived", "QuantityRejected", "PercentageRejection"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── Derived columns ──────────────────────────────────────────────────────
    df["QuantityPending"] = (df["QuantityOrdered"] - df["QuantityReceived"]).clip(lower=0)

    # ── Status label ─────────────────────────────────────────────────────────
    def get_status(row):
        if row["QuantityRejected"] > 0:
            return "Rejected"
        elif row["QuantityPending"] == 0:
            return "Fully Received"
        elif row["QuantityReceived"] > 0:
            return "Partial"
        else:
            return "Pending"
    df["Status"] = df.apply(get_status, axis=1)

    return df

# ── Load with friendly error ─────────────────────────────────────────────────
try:
    df_full = load_grn_data()
except FileNotFoundError:
    st.error(f"❌ Excel file not found. Please update `EXCEL_PATH` in the script.\n\nCurrent path: `{EXCEL_PATH}`")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
page_header("📥", "GRN Data", "Goods Receipt Note tracking & analysis")

# ─────────────────────────────────────────────────────────────────────────────
# FILTERS — Row 1
# ─────────────────────────────────────────────────────────────────────────────
section_label("Search & Filter")
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    search_grn = st.text_input("", placeholder="🔍  Search GRN No / Item Name…", label_visibility="collapsed")
with col2:
    po_opts = ["All POs"] + sorted(df_full["PO No"].dropna().unique().tolist())
    po_sel  = st.selectbox("PO Number", po_opts)
with col3:
    vendor_opts = ["All Vendors"] + sorted(df_full["Vendor Name"].dropna().unique().tolist())
    vendor_sel  = st.selectbox("Vendor", vendor_opts)
with col4:
    wh_opts = ["All Warehouses"] + sorted(df_full["Warehouse"].dropna().unique().tolist())
    wh_sel  = st.selectbox("Warehouse", wh_opts)

# ── Row 2: Date range + Status ────────────────────────────────────────────────
valid_dates = df_full["GRN Date"].dropna()
min_d, max_d = valid_dates.min(), valid_dates.max()

col5, col6, col7, col8 = st.columns([2, 2, 2, 2])
with col5:
    date_from = st.date_input("From Date", value=min_d, min_value=min_d, max_value=max_d)
with col6:
    date_to   = st.date_input("To Date",   value=max_d, min_value=min_d, max_value=max_d)
with col7:
    status_opts = ["All Statuses"] + sorted(df_full["Status"].unique().tolist())
    status_sel  = st.selectbox("Status", status_opts)
with col8:
    item_opts = ["All Items"] + sorted(df_full["Item Name"].dropna().unique().tolist())
    item_sel  = st.selectbox("Item", item_opts)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
df = df_full.copy()

if search_grn:
    mask = (
        df["GRN No"].astype(str).str.contains(search_grn, case=False, na=False) |
        df["Item Name"].astype(str).str.contains(search_grn, case=False, na=False)
    )
    df = df[mask]

if po_sel      != "All POs":        df = df[df["PO No"]       == po_sel]
if vendor_sel  != "All Vendors":    df = df[df["Vendor Name"] == vendor_sel]
if wh_sel      != "All Warehouses": df = df[df["Warehouse"]   == wh_sel]
if status_sel  != "All Statuses":   df = df[df["Status"]      == status_sel]
if item_sel    != "All Items":       df = df[df["Item Name"]   == item_sel]

df = df[
    (df["GRN Date"].notna()) &
    (df["GRN Date"] >= date_from) &
    (df["GRN Date"] <= date_to)
]

# ─────────────────────────────────────────────────────────────────────────────
# STAT CARDS
# ─────────────────────────────────────────────────────────────────────────────
total_ordered  = df["QuantityOrdered"].sum()
total_received = df["QuantityReceived"].sum()
total_pending  = df["QuantityPending"].sum()
total_rejected = df["QuantityRejected"].sum()
grn_count      = df["GRN No"].nunique()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(stat_card("Total QTY Ordered",  fmt(total_ordered),  f"{grn_count} unique GRNs", "#1A56DB", "📋"), unsafe_allow_html=True)
with c2:
    st.markdown(stat_card("Total QTY Received", fmt(total_received), "Against ordered qty",       "#16A34A", "✅"), unsafe_allow_html=True)
with c3:
    st.markdown(stat_card("Pending QTY",        fmt(total_pending),  "Yet to be received",        "#B45309", "⏳"), unsafe_allow_html=True)
with c4:
    st.markdown(stat_card("Total QTY Rejected", fmt(total_rejected), "Rejection across GRNs",     "#DC2626", "❌"), unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────────────────────────────────────
section_label(f"GRN Records — {len(df):,} rows  |  {grn_count} GRNs")

display_cols = [
    "GRN No", "GRN Date", "Vendor Name", "PO No",
    "Item Code", "Item Name", "Warehouse",
    "QuantityOrdered", "QuantityReceived", "QuantityPending",
    "QuantityRejected", "PercentageRejection", "Status"
]
# Keep only columns that exist in the dataframe
display_cols = [c for c in display_cols if c in df.columns]

display_df = df[display_cols].copy()
display_df["GRN Date"] = display_df["GRN Date"].astype(str)

def style_status(val):
    colors = {
        "Fully Received": "background-color:#DCFCE7;color:#166534;font-weight:600",
        "Pending":        "background-color:#FEF9C3;color:#713F12;font-weight:600",
        "Partial":        "background-color:#DBEAFE;color:#1E40AF;font-weight:600",
        "Rejected":       "background-color:#FEE2E2;color:#991B1B;font-weight:600",
    }
    return colors.get(val, "")

fmt_cols = {c: "{:,.2f}" for c in ["QuantityOrdered", "QuantityReceived", "QuantityPending", "QuantityRejected"]}
fmt_cols["PercentageRejection"] = "{:.2f}%"
fmt_cols = {k: v for k, v in fmt_cols.items() if k in display_df.columns}

styled = (
    display_df.style
    .applymap(style_status, subset=["Status"] if "Status" in display_df.columns else [])
    .format(fmt_cols)
)

st.dataframe(styled, use_container_width=True, hide_index=True, height=520)

# ── Export button ─────────────────────────────────────────────────────────────
csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️  Export to CSV", csv, "grn_data_export.csv", "text/csv")
