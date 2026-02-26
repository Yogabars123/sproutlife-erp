import streamlit as st
import pandas as pd
import os

st.title("📦 RM Inventory")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_rm():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="RM-Inventory")

    # Clean warehouse column
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()

    return df


df = load_rm()

# ---------------------------------------------------
# ALLOWED WAREHOUSES
# ---------------------------------------------------
allowed_warehouses = [
    "Central",
    "Central Production -Bar Line",
    "Central Production - Oats Line",
    "Central Production - Peanut Line",
    "Central Production - Muesli Line",
    "RM Warehouse Tumkur",
    "Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse",
    "Central Production -Packing",
    "Tumkur New Warehouse",
    "HF Factory FG Warehouse",
    "Sproutlife Foods Private Ltd (SNOWMAN)"
]

allowed_warehouses = [w.strip() for w in allowed_warehouses]

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------
df = df[df["Warehouse"].isin(allowed_warehouses)]

# ---------------------------------------------------
# SEARCH
# ---------------------------------------------------
search = st.text_input("Search RM")

if search:
    df = df[df.astype(str).apply(
        lambda x: x.str.contains(search, case=False, na=False).any(),
        axis=1
    )]

# ---------------------------------------------------
# DISPLAY
# ---------------------------------------------------
st.dataframe(df, use_container_width=True)