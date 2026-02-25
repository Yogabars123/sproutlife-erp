import streamlit as st
import pandas as pd
import os

st.title("📦 RM Inventory")

@st.cache_data
def load_rm():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="RM-Inventory")
    return df

df = load_rm()

search = st.text_input("Search RM")

if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

st.dataframe(df, use_container_width=True)