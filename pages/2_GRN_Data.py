import streamlit as st
import pandas as pd

st.set_page_config(page_title="GRN Data", layout="wide", page_icon="📥")

# ─────────────────────────────────────────────
# MOBILE OPTIMIZED CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
.kpi-card {
    border-radius: 12px;
    padding: 16px;
    color: white;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.kpi-title {
    font-size: 13px;
    font-weight: 600;
    opacity: 0.9;
}

.kpi-value {
    font-size: 24px;
    font-weight: 800;
    margin-top: 4px;
}

/* Mobile Optimization */
@media (max-width: 768px) {
    .kpi-card {
        padding: 12px;
    }
    .kpi-title {
        font-size: 11px;
    }
    .kpi-value {
        font-size: 18px;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Sproutlife Inventory.xlsx", sheet_name="GRN-Data")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

numeric_cols = ["QuantityOrdered", "QuantityReceived", "QuantityRejected"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ─────────────────────────────────────────────
# CENTRAL + VALID PO FILTER
# ─────────────────────────────────────────────
base_df = df[
    (df["Warehouse"] == "Central") &
    (df["PO No"].notna()) &
    (df["PO No"].astype(str).str.strip() != "") &
    (df["PO No"].astype(str).str.strip() != "-")
]

# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────
search_text = st.text_input("Search (GRN / Item Code / Item Name / PO No)")

filtered_df = base_df.copy()

if search_text:
    search_text = search_text.lower()
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row:
                search_text in str(row["GRN No"]).lower()
                or search_text in str(row["Item Code"]).lower()
                or search_text in str(row["Item Name"]).lower()
                or search_text in str(row["PO No"]).lower(),
            axis=1
        )
    ]

# ─────────────────────────────────────────────
# KPI CALCULATION
# ─────────────────────────────────────────────
total_ordered = filtered_df["QuantityOrdered"].sum()
total_received = filtered_df["QuantityReceived"].sum()
total_rejected = filtered_df["QuantityRejected"].sum()
pending_qty = total_ordered - total_received

# ─────────────────────────────────────────────
# KPI DISPLAY (Responsive Grid)
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg,#1A56DB,#2563EB);">
        <div class="kpi-title">Ordered Quantity</div>
        <div class="kpi-value">{total_ordered:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg,#16A34A,#22C55E);">
        <div class="kpi-title">Received Quantity</div>
        <div class="kpi-value">{total_received:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg,#F59E0B,#FBBF24);">
        <div class="kpi-title">Pending Quantity</div>
        <div class="kpi-value">{pending_qty:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg,#DC2626,#EF4444);">
        <div class="kpi-title">Rejected Quantity</div>
        <div class="kpi-value">{total_rejected:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### GRN Records (Central + Valid PO Only)")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
