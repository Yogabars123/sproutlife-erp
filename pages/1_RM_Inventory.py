import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------
st.title("📦 RM Inventory")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_rm():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="RM-Inventory")

    # Ensure column exists
    if "wh" not in df.columns:
        st.error("Column 'wh' not found in Excel file")
        st.stop()

    # Clean warehouse column
    df["wh"] = df["wh"].astype(str).str.strip().str.lower()

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

# Convert to lowercase
allowed_warehouses = [w.strip().lower() for w in allowed_warehouses]

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------
df = df[df["wh"].isin(allowed_warehouses)]

# ---------------------------------------------------
# SEARCH OPTION
# ---------------------------------------------------
search = st.text_input("Search RM")

if search:
    df = df[df.astype(str).apply(
        lambda x: x.str.contains(search, case=False, na=False).any(),
        axis=1
    )]

# ---------------------------------------------------
# DISPLAY DATA
# ---------------------------------------------------
st.dataframe(df, use_container_width=True)