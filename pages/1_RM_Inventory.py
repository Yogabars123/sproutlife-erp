import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# MOBILE DETECTION (Auto)
# ─────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=False)

# ─────────────────────────────────────────────
# RESPONSIVE CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #F8FAFC !important; }

/* Reduce container width on mobile */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem !important;
        max-width: 100% !important;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }
}

/* Desktop padding */
.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1280px !important;
}

/* Buttons */
.stButton > button {
    background: #1A56DB !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────
def stat_card(label, value, sub="", color="#1A56DB", icon=""):
    return f"""
    <div style="background:linear-gradient(135deg,{color} 0%,{color}cc 100%);
                border-radius:16px;
                padding:1.5rem;
                color:white;
                margin-bottom:1rem;
                box-shadow:0 10px 25px {color}40;">
        <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;opacity:0.85;">
            {icon} {label}
        </div>
        <div style="font-size:2rem;font-weight:800;margin:0.5rem 0;">
            {value}
        </div>
        <div style="font-size:0.8rem;opacity:0.75;">
            {sub}
        </div>
    </div>
    """

def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;">
            <span style="font-size:1.8rem;">{icon}</span>
            <h1 style="margin:0;font-size:1.8rem;font-weight:800;">{title}</h1>
        </div>
        <p style="margin:0;color:#64748B;font-size:0.9rem;padding-left:2.2rem;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────
page_header("📦", "RM Inventory", "Live raw material stock")

# Refresh Button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("### 🔎 Search & Filter")

# ─────────────────────────────────────────────
# RESPONSIVE FILTER SECTION
# ─────────────────────────────────────────────
if mobile_mode:
    search = st.text_input("", placeholder="Search item name, SKU or batch…")
    warehouse = st.selectbox("Warehouse", ["All Warehouses"])
    stock_status = st.selectbox("Stock Status",
                                ["All", "In Stock", "Low Stock", "Out of Stock"])
else:
    col_search, col_wh, col_status = st.columns([3,2,2])
    with col_search:
        search = st.text_input("", placeholder="Search item name, SKU or batch…")
    with col_wh:
        warehouse = st.selectbox("Warehouse", ["All Warehouses"])
    with col_status:
        stock_status = st.selectbox("Stock Status",
                                    ["All", "In Stock", "Low Stock", "Out of Stock"])

st.markdown("")

# ─────────────────────────────────────────────
# RESPONSIVE KPI CARDS
# ─────────────────────────────────────────────
if mobile_mode:
    st.markdown(stat_card("Total QTY Available", "16,300,788",
                          "2,414 records", "#1A56DB", "📦"),
                unsafe_allow_html=True)

    st.markdown(stat_card("Items In Stock", "1,892",
                          "78.3% of catalogue", "#16A34A", "✅"),
                unsafe_allow_html=True)

    st.markdown(stat_card("Low / Out of Stock", "522",
                          "Need attention", "#DC2626", "⚠️"),
                unsafe_allow_html=True)

else:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(stat_card("Total QTY Available", "16,300,788",
                              "2,414 records", "#1A56DB", "📦"),
                    unsafe_allow_html=True)

    with c2:
        st.markdown(stat_card("Items In Stock", "1,892",
                              "78.3% of catalogue", "#16A34A", "✅"),
                    unsafe_allow_html=True)

    with c3:
        st.markdown(stat_card("Low / Out of Stock", "522",
                              "Need attention", "#DC2626", "⚠️"),
                    unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📋 Inventory Records")

# ─────────────────────────────────────────────
# SAMPLE DATA (Replace With Your Logic)
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.DataFrame({
        "Item": ["Item A", "Item B", "Item C"],
        "Warehouse": ["WH1", "WH2", "WH1"],
        "Stock": [120, 45, 0]
    })

df = load_data()

if search:
    df = df[df["Item"].str.contains(search, case=False)]

st.dataframe(df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# FUTURE CHATBOT SECTION
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🤖 ERP Assistant")

user_input = st.text_input("Ask about stock, forecast, risk...")

if user_input:
    st.success(f"Bot response for: {user_input}")
