import streamlit as st
import pandas as pd

st.set_page_config(page_title="RM Inventory", layout="wide", page_icon="📦")

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
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
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def stat_card(label, value, color="#21bbb2", icon="📦"):
    return f"""
    <div style="background:linear-gradient(100deg,{color},{color}33);
                border-radius:12px;padding:1.2rem 1.6rem;color:#fff;
                box-shadow:0 4px 16px {color}40;margin-bottom:1rem;
                display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.06em;
                        text-transform:uppercase;opacity:0.85;margin-bottom:0.3rem;">{label}</div>
            <div style="font-size:1.9rem;font-weight:800;letter-spacing:-0.02em;">{value}</div>
        </div>
        <div style="font-size:2.2rem;opacity:0.8;">{icon}</div>
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
    return f"{n:,.2f}"

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING  ← same Excel file, different sheet
# ─────────────────────────────────────────────────────────────────────────────
EXCEL_PATH = r"C:\Users\YOGA BAR\OneDrive - SPROUTLIFE FOODS PRIVATE LIMITED\Sproutlife Inventory.xlsx"
SHEET_NAME = "RM-Inventory"   # ← update if your sheet name is different

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, engine="openpyxl")
    df.columns = df.columns.str.strip()

    # Normalise numeric qty column — adjust column name if needed
    qty_col = next((c for c in df.columns if "qty" in c.lower() or "quantity" in c.lower() or "available" in c.lower()), None)
    if qty_col:
        df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0)

    return df, qty_col

try:
    df_full, qty_col = load_data()
except FileNotFoundError:
    st.error(f"❌ File not found at: `{EXCEL_PATH}`")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
page_header("📦", "Raw Material Inventory", "Quick summary of products and their current status")

# ─────────────────────────────────────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────────────────────────────────────
section_label("Search & Filter")
col1, col2 = st.columns([3, 2])

# Detect item code / item name column
item_col = next((c for c in df_full.columns if "item" in c.lower() or "code" in c.lower()), df_full.columns[0])
wh_col   = next((c for c in df_full.columns if "warehouse" in c.lower()), None)

with col1:
    search = st.text_input("", placeholder=f"🔍  Search {item_col}…", label_visibility="collapsed")

with col2:
    if wh_col:
        wh_opts = ["All Warehouses"] + sorted(df_full[wh_col].dropna().unique().tolist())
        wh_sel  = st.selectbox("Warehouse", wh_opts)
    else:
        wh_sel = "All Warehouses"

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
df = df_full.copy()

if search:
    df = df[df[item_col].astype(str).str.contains(search, case=False, na=False)]

if wh_col and wh_sel != "All Warehouses":
    df = df[df[wh_col] == wh_sel]

# ─────────────────────────────────────────────────────────────────────────────
# STAT CARD
# ─────────────────────────────────────────────────────────────────────────────
total_stock = df[qty_col].sum() if qty_col else 0
st.markdown(stat_card("Total Stock", fmt(total_stock), "#21bbb2", "📦"), unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────────────────────────────────────
section_label(f"Inventory Records — {len(df):,} rows")

if len(df) == 0:
    st.info("No records match your filters.")
else:
    fmt_cols = {qty_col: "{:,.2f}"} if qty_col else {}
    styled = df.style.format(fmt_cols)
    st.dataframe(styled, use_container_width=True, hide_index=True, height=520)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️  Export to CSV", csv, "rm_inventory_export.csv", "text/csv")
