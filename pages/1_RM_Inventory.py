import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="RM Inventory", layout="wide")

# Get project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# HTML file path
html_file = BASE_DIR / "rm_inventory.html"

# Read HTML
html = html_file.read_text(encoding="utf-8")

# Display HTML
components.html(html, height=1200, scrolling=True)
