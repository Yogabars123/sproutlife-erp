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
# MOBILE TOGGLE
# ─────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=False)

# ─────────────────────────────────────────────
# RESPONSIVE CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: #F8FAFC !important; }

@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem !important;
        max-width: 100% !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
}

.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1280px !important;
}

.stButton > button {
    background: #1A56DB !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

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

# Refresh
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# ─────────────────────────────────────────────
# LOAD DATA (REPLACE WITH YOUR REAL DATA)
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    # Replace this with your Excel file
    return pd.DataFrame({
        "Item": ["Sugar", "Oats", "Almond", "Milk Powder"],
        "Warehouse": ["WH1", "WH2", "WH1", "WH3"],
        "Stock": [12000, 0, 4500, 200]
    })

df = load_data()

# ─────────────────────────────────────────────
# SEARCH & FILTER
# ─────────────────────────────────────────────
st.markdown("### 🔎 Search & Filter")

if mobile_mode:
    search = st.text_input("", placeholder="Search item, SKU, batch...")
    warehouse = st.selectbox("Warehouse",
                             ["All Warehouses"] + sorted(df["Warehouse"].unique().tolist()))
    stock_status = st.selectbox("Stock Status",
                                ["All", "In Stock", "Low Stock", "Out of Stock"])
else:
    col1, col2, col3 = st.columns([3,2,2])
    with col1:
        search = st.text_input("", placeholder="Search item, SKU, batch...")
    with col2:
        warehouse = st.selectbox("Warehouse",
                                 ["All Warehouses"] + sorted(df["Warehouse"].unique().tolist()))
    with col3:
        stock_status = st.selectbox("Stock Status",
                                    ["All", "In Stock", "Low Stock", "Out of Stock"])

# ─────────────────────────────────────────────
# APPLY FILTERS SAFELY
# ─────────────────────────────────────────────
filtered_df = df.copy()

# Search across all columns safely
if search:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

# Warehouse filter
if warehouse != "All Warehouses":
    filtered_df = filtered_df[filtered_df["Warehouse"] == warehouse]

# Stock status filter
if stock_status == "In Stock":
    filtered_df = filtered_df[filtered_df["Stock"] > 0]
elif stock_status == "Out of Stock":
    filtered_df = filtered_df[filtered_df["Stock"] == 0]
elif stock_status == "Low Stock":
    filtered_df = filtered_df[(filtered_df["Stock"] > 0) & (filtered_df["Stock"] < 500)]

# ─────────────────────────────────────────────
# KPI CALCULATIONS (BASED ON FILTERED DATA)
# ─────────────────────────────────────────────
total_qty = filtered_df["Stock"].sum()
total_items = len(filtered_df)
in_stock = len(filtered_df[filtered_df["Stock"] > 0])
low_or_out = len(filtered_df[filtered_df["Stock"] <= 500])

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
if mobile_mode:
    st.markdown(stat_card("Total QTY Available", f"{total_qty:,}",
                          f"{total_items} records", "#1A56DB", "📦"),
                unsafe_allow_html=True)
    st.markdown(stat_card("Items In Stock", f"{in_stock:,}",
                          "Available items", "#16A34A", "✅"),
                unsafe_allow_html=True)
    st.markdown(stat_card("Low / Out of Stock", f"{low_or_out:,}",
                          "Need attention", "#DC2626", "⚠️"),
                unsafe_allow_html=True)
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(stat_card("Total QTY Available", f"{total_qty:,}",
                              f"{total_items} records", "#1A56DB", "📦"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Items In Stock", f"{in_stock:,}",
                              "Available items", "#16A34A", "✅"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("Low / Out of Stock", f"{low_or_out:,}",
                              "Need attention", "#DC2626", "⚠️"),
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INVENTORY TABLE
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Inventory Records")

if filtered_df.empty:
    st.warning("No records found for selected filters.")
else:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# ERP CHATBOT SECTION (READY FOR GPT)
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🤖 ERP Assistant")

user_input = st.text_input("Ask about stock, forecast, risk...")

if user_input:
    st.success(f"Bot response for: {user_input}")
