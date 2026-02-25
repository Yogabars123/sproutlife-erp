import streamlit as st

st.set_page_config(
    page_title="Sproutlife Inventory Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Sproutlife Inventory Management System")
st.markdown("---")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    (
        "RM Inventory",
        "GRN Data",
        "FG Inventory",
        "Consumption"
    )
)

if page == "RM Inventory":
    st.switch_page("pages/1_RM_Inventory.py")

elif page == "GRN Data":
    st.switch_page("pages/2_GRN_Data.py")

elif page == "FG Inventory":
    st.switch_page("pages/3_FG_Inventory.py")

elif page == "Consumption":
    st.switch_page("pages/4_Consumption.py")