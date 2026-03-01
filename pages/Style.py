import streamlit as st

st.set_page_config(page_title="Style", layout="wide", page_icon="🎨")

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
.main .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1280px !important; }
.stButton > button {
    background: #1A56DB !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover { background: #1140A8 !important; transform: translateY(-1px) !important; }
.stTextInput > div > div > input {
    background: #fff !important; border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.875rem !important;
}
.stSelectbox > div > div {
    background: #fff !important; border: 1.5px solid #E2E8F0 !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.875rem !important;
}
#MainMenu { visibility: hidden; } footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid #E2E8F0;">
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.3rem;">
        <span style="font-size:1.8rem;">🎨</span>
        <h1 style="margin:0;font-family:'DM Sans',sans-serif;font-size:1.75rem;
                   font-weight:700;color:#0F172A;letter-spacing:-0.02em;">Design System</h1>
    </div>
    <p style="margin:0;font-size:0.875rem;color:#94A3B8;padding-left:2.6rem;">
        Live preview of all UI components used across Sproutlife ERP
    </p>
</div>""", unsafe_allow_html=True)

# ─── COLOUR PALETTE ──────────────────────────────────────────────────────────
st.markdown("""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
            text-transform:uppercase;color:#94A3B8;margin-bottom:0.8rem;">Colour Palette</div>""",
            unsafe_allow_html=True)

colors = [
    ("#1A56DB", "Primary Blue",   "Buttons, active states, primary cards"),
    ("#16A34A", "Success Green",  "Received, in-stock, positive metrics"),
    ("#B45309", "Warning Amber",  "Pending, low stock, caution states"),
    ("#DC2626", "Danger Red",     "Rejected, out-of-stock, critical alerts"),
    ("#0F172A", "Text Primary",   "Headings and body text"),
    ("#94A3B8", "Text Muted",     "Labels, placeholders, subtitles"),
    ("#E2E8F0", "Border",         "Dividers, card borders, input borders"),
    ("#F8FAFC", "Background",     "App background"),
]

cols = st.columns(4)
for i, (hex_code, name, usage) in enumerate(colors):
    with cols[i % 4]:
        text_color = "#fff" if hex_code not in ("#E2E8F0", "#F8FAFC") else "#0F172A"
        border = "border:1px solid #E2E8F0;" if hex_code in ("#E2E8F0", "#F8FAFC") else ""
        st.markdown(f"""
        <div style="background:{hex_code};{border}border-radius:10px;padding:1rem;
                    margin-bottom:0.75rem;min-height:80px;">
            <div style="color:{text_color};font-weight:700;font-size:0.85rem;
                        font-family:'DM Mono',monospace;">{hex_code}</div>
            <div style="color:{text_color};font-weight:600;font-size:0.78rem;
                        margin-top:0.25rem;opacity:0.9;">{name}</div>
            <div style="color:{text_color};font-size:0.68rem;margin-top:0.2rem;
                        opacity:0.65;">{usage}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── KPI STAT CARDS ──────────────────────────────────────────────────────────
st.markdown("""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
            text-transform:uppercase;color:#94A3B8;margin-bottom:0.8rem;">KPI Stat Cards</div>""",
            unsafe_allow_html=True)

cards_data = [
    ("#1A56DB", "📋", "Total QTY Ordered", "304,726,587", "12,918 GRNs"),
    ("#16A34A", "✅", "Total QTY Received", "135,393,246", "Against ordered qty"),
    ("#B45309", "⏳", "Pending QTY", "169,333,341", "Yet to be received"),
    ("#DC2626", "❌", "Total QTY Rejected", "31,429", "Rejection across GRNs"),
]
c1, c2, c3, c4 = st.columns(4)
for col, (color, icon, label, value, sub) in zip([c1, c2, c3, c4], cards_data):
    with col:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{color} 0%,{color}cc 100%);
                    border-radius:14px;padding:1.4rem 1.6rem;color:#fff;
                    box-shadow:0 6px 20px {color}40;margin-bottom:1rem;">
            <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                        text-transform:uppercase;opacity:0.8;margin-bottom:0.4rem;">{icon} {label}</div>
            <div style="font-size:2rem;font-weight:800;letter-spacing:-0.03em;
                        line-height:1.1;margin-bottom:0.25rem;">{value}</div>
            <div style="font-size:0.78rem;opacity:0.7;">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── TYPOGRAPHY ──────────────────────────────────────────────────────────────
st.markdown("""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
            text-transform:uppercase;color:#94A3B8;margin-bottom:0.8rem;">Typography</div>""",
            unsafe_allow_html=True)

st.markdown("""
<div style="background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:1.5rem 2rem;">
    <div style="font-family:'DM Sans',sans-serif;font-size:1.75rem;font-weight:700;
                color:#0F172A;letter-spacing:-0.02em;margin-bottom:0.5rem;">
        Page Title — DM Sans 700, 1.75rem
    </div>
    <div style="font-family:'DM Sans',sans-serif;font-size:1.25rem;font-weight:600;
                color:#0F172A;margin-bottom:0.5rem;">
        Section Heading — DM Sans 600, 1.25rem
    </div>
    <div style="font-family:'DM Sans',sans-serif;font-size:0.875rem;font-weight:400;
                color:#475569;margin-bottom:0.5rem;">
        Body Text — DM Sans 400, 0.875rem, #475569
    </div>
    <div style="font-family:'DM Sans',sans-serif;font-size:0.875rem;color:#94A3B8;margin-bottom:0.5rem;">
        Subtitle / Muted — DM Sans 400, 0.875rem, #94A3B8
    </div>
    <div style="font-family:'DM Sans',sans-serif;font-size:0.68rem;font-weight:700;
                letter-spacing:0.08em;text-transform:uppercase;color:#94A3B8;margin-bottom:0.5rem;">
        Section Label — DM Sans 700, 0.68rem, uppercase, tracked
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:0.82rem;color:#0F172A;">
        Table Numbers — DM Mono 400, 0.82rem (used in dataframes)
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── FORM COMPONENTS ─────────────────────────────────────────────────────────
st.markdown("""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
            text-transform:uppercase;color:#94A3B8;margin-bottom:0.8rem;">Form Components</div>""",
            unsafe_allow_html=True)

f1, f2, f3 = st.columns([3, 2, 2])
with f1:
    st.text_input("Text Input", placeholder="🔍  Search item name, SKU or batch…")
with f2:
    st.selectbox("Select Box", ["All Warehouses", "Warehouse A", "Warehouse B"])
with f3:
    st.selectbox("Status Filter", ["All", "In Stock", "Low Stock", "Out of Stock"])

b1, b2, b3, _ = st.columns([1, 1, 1, 3])
with b1:
    st.button("Primary Button")
with b2:
    st.button("🔄  Refresh Data")
with b3:
    st.toggle("📱 Mobile View", value=True)
