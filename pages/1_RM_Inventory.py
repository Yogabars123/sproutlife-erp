import streamlit as st
import pandas as pd
import openai

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory | ERP",
    layout="wide",
    page_icon="📦"
)

openai.api_key = st.secrets["OPENAI_API_KEY"]

# ─────────────────────────────────────────────
# CUSTOM ENTERPRISE CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 10px;
}
.chat-container {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_excel(
        "Sproutlife Inventory.xlsx",
        sheet_name="RM-Inventory"
    )
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/warehouse.png", width=80)
st.sidebar.title("Sproutlife ERP")
st.sidebar.markdown("**Module:** RM Inventory")
st.sidebar.markdown("---")
search_sidebar = st.sidebar.text_input("🔎 Quick Search")

# Apply sidebar search
filtered_df = df.copy()
if search_sidebar:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search_sidebar, case=False).any(),
            axis=1
        )
    ]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>📦 Raw Material Inventory Overview</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI SECTION
# ─────────────────────────────────────────────
qty_column = df.columns[-1]

total_qty = filtered_df[qty_column].sum()
total_records = len(filtered_df)
zero_stock = len(filtered_df[filtered_df[qty_column] == 0])

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.metric("Total Quantity", f"{total_qty:,.0f}")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.metric("Total SKUs", total_records)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.metric("Out of Stock Items", zero_stock)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA TABLE
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>📋 Inventory Records</div>", unsafe_allow_html=True)
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AI ASSISTANT PANEL
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>🤖 AI Inventory Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about inventory risks, stock status, forecasts...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    data_preview = df.head(200).to_string()

    system_prompt = f"""
You are an enterprise ERP inventory assistant.
Use the RM Inventory data below to answer clearly and professionally.

{data_preview}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    answer = response["choices"][0]["message"]["content"]

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(answer)

st.markdown("</div>", unsafe_allow_html=True)
