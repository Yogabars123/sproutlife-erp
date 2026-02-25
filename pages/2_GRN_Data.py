import streamlit as st
import pandas as pd
import os

st.title("📥 GRN Data")

@st.cache_data
def load_grn():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="GRN-Data")
    return df

df = load_grn()

search = st.text_input("Search GRN")

if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

st.dataframe(df, use_container_width=True)