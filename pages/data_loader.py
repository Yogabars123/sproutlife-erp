import pandas as pd
import streamlit as st
import os
import io

# ── Local Excel file path ─────────────────────────────────────────────────────
def _get_excel_path():
    # Try relative to pages folder first, then cwd
    p1 = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    p2 = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    return p1 if os.path.exists(p1) else p2

@st.cache_data(ttl=300)
def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Load sheet from local Excel file."""
    try:
        fp = _get_excel_path()
        df = pd.read_excel(fp, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load data: {e}")
        return pd.DataFrame()
