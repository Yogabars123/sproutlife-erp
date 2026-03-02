import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory",
    layout="wide",
    page_icon="📦"
)

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
# MAIN UI
# ─────────────────────────────────────────────
st.markdown("## 📦 RM Inventory Dashboard")

search = st.text_input("🔎 Search items")

filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

qty_column = "Stock" if "Stock" in df.columns else df.columns[-1]

total_qty = filtered_df[qty_column].sum()
total_records = len(filtered_df)

c1, c2 = st.columns(2)
c1.metric("Total Quantity", f"{total_qty:,.0f}")
c2.metric("Total Records", total_records)

st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("## 🤖 RM Inventory Assistant")

# ─────────────────────────────────────────────
# CHATBOT LOGIC
# ─────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about RM inventory...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = ""

    query = prompt.lower()

    if "total" in query:
        response = f"Total quantity available is {df[qty_column].sum():,.0f}"

    elif "low stock" in query:
        low_df = df[df[qty_column] < 100]
        response = f"There are {len(low_df)} low stock items."
        st.dataframe(low_df, use_container_width=True)

    elif "zero" in query or "out of stock" in query:
        zero_df = df[df[qty_column] == 0]
        response = f"There are {len(zero_df)} out of stock items."
        st.dataframe(zero_df, use_container_width=True)

    elif "top" in query:
        top_df = df.sort_values(by=qty_column, ascending=False).head(5)
        response = "Top 5 highest stock items:"
        st.dataframe(top_df, use_container_width=True)

    else:
        response = "I can help with: total stock, low stock, zero stock, top items."

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)
