import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="RM Inventory", layout="wide", page_icon="📦")

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDED STYLES — no external file needed, paste this block into every page
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
# HELPER FUNCTIONS — copy these into every page too
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

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONTENT
# ─────────────────────────────────────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=True)

page_header("📦", "RM Inventory", "Live raw material stock")

if st.button("🔄  Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

section_label("Search & Filter")
col_search, col_wh, col_status = st.columns([3, 2, 2])
with col_search:
    search = st.text_input("", placeholder="🔍  Search item name, SKU or batch…", label_visibility="collapsed")
with col_wh:
    warehouse = st.selectbox("Warehouse", ["All Warehouses"])
with col_status:
    stock_status = st.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock"])

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(stat_card("Total QTY Available", "16,300,788", "2,414 records", "#1A56DB", "📦"), unsafe_allow_html=True)
with c2:
    st.markdown(stat_card("Items In Stock", "1,892", "78.3% of catalogue", "#16A34A", "✅"), unsafe_allow_html=True)
with c3:
    st.markdown(stat_card("Low / Out of Stock", "522", "Need attention", "#DC2626", "⚠️"), unsafe_allow_html=True)

st.markdown("---")
section_label("Inventory Records")

# ── YOUR EXISTING DATA LOGIC GOES HERE ──────────────────────────────────────
# Paste your original data loading, filtering, and st.dataframe() code below:
#
# @st.cache_data
# def load_data():
#     ...
#     return df
#
# df = load_data()
# if search:
#     df = df[df['item_name'].str.contains(search, case=False, na=False)]
# if warehouse != "All Warehouses":
#     df = df[df['warehouse'] == warehouse]
# st.dataframe(df, use_container_width=True, hide_index=True)
