import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="RM Inventory", layout="wide")

# Load Excel
df = pd.read_excel("Sproutlife Inventory.xlsx", sheet_name="RM-Inventory")

# Convert to JSON
data_json = df.to_json(orient="records")

# Read HTML
html_path = Path("rm_inventory.html")
html = html_path.read_text()

# Inject data into HTML
html = html.replace("DATA_PLACEHOLDER", data_json)

components.html(html, height=1200, scrolling=True)
