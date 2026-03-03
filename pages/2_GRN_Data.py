import streamlit as st
import pandas as pd

st.set_page_config(page_title="GRN Data", layout="wide", page_icon="📥")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Sproutlife Inventory.xlsx", sheet_name="GRN-Data")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Convert numeric columns
numeric_cols = ["QuantityOrdered", "QuantityReceived", "QuantityRejected"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ─────────────────────────────────────────────
# BASE FILTER (Central + Valid PO Only)
# ─────────────────────────────────────────────
base_df = df[
    (df["Warehouse"] == "Central") &
    (df["PO No"].notna()) &
    (df["PO No"].astype(str).str.strip() != "") &
    (df["PO No"].astype(str).str.strip() != "-")
]

# ─────────────────────────────────────────────
# SEARCH & FILTER
# ─────────────────────────────────────────────
st.markdown("### SEARCH & FILTER")

col1, col2 = st.columns([3,2])

with col1:
    search_text = st.text_input("Search (GRN / Item Code / Item Name / PO No)")

with col2:
    vendor_options = ["All Vendors"] + sorted(base_df["Vendor Name"].dropna().astype(str).unique().tolist())
    vendor = st.selectbox("Vendor", vendor_options)

# Apply filters
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

if vendor != "All Vendors":
    filtered_df = filtered_df[filtered_df["Vendor Name"].astype(str) == vendor]

# ─────────────────────────────────────────────
# KPI CALCULATION
# ─────────────────────────────────────────────
total_ordered = filtered_df["QuantityOrdered"].sum()
total_received = filtered_df["QuantityReceived"].sum()
total_rejected = filtered_df["QuantityRejected"].sum()
pending_qty = total_ordered - total_received

# ─────────────────────────────────────────────
# COLORED KPI CARDS
# ─────────────────────────────────────────────
def kpi_card(title, value, color):
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}, {color}cc);
        padding: 20px;
        border-radius: 14px;
        color: white;
        box-shadow: 0 6px 18px {color}40;
    ">
        <div style="font-size: 14px; font-weight: 600;">
            {title}
        </div>
        <div style="font-size: 28px; font-weight: 800; margin-top: 6px;">
            {value:,.0f}
        </div>
    </div>
    """

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(kpi_card("Ordered Quantity", total_ordered, "#1A56DB"), unsafe_allow_html=True)

with c2:
    st.markdown(kpi_card("Received Quantity", total_received, "#16A34A"), unsafe_allow_html=True)

with c3:
    st.markdown(kpi_card("Pending Quantity", pending_qty, "#F59E0B"), unsafe_allow_html=True)

with c4:
    st.markdown(kpi_card("Rejected Quantity", total_rejected, "#DC2626"), unsafe_allow_html=True)

st.markdown("---")
st.markdown("### GRN Records (Central + Valid PO Only)")

st.dataframe(filtered_df, use_container_width=True, hide_index=True)
