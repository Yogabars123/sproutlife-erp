import streamlit as st
import pandas as pd
import os

st.title("🏭 FG Inventory")

@st.cache_data
def load_fg():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="FG-Inventory")
    return df

df = load_fg()

search = st.text_input("Search FG")

if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

st.dataframe(df, use_container_width=True)