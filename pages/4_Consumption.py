import streamlit as st
import pandas as pd
import os

st.title("📊 Consumption")

@st.cache_data
def load_consumption():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="Consumption")
    return df

df = load_consumption()

search = st.text_input("Search Consumption")

if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

st.dataframe(df, use_container_width=True)