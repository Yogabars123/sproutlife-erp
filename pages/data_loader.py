import pandas as pd
import streamlit as st
import requests
import os
import io

# SharePoint direct download URL
SHAREPOINT_URL = "https://sproutlife01-my.sharepoint.com/:x:/g/personal/abinaya_m_yogabars_in/IQBLtIoDsWtwQZiImCHkW6BeAa-SnNj7UJdAqjShhWjHS7U?e=MGwLOm&download=1"

def _get_local_path():
    p1 = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    p2 = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    return p1 if os.path.exists(p1) else p2

@st.cache_data(ttl=300)
def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Try SharePoint first, fall back to local Excel file."""

    # Try SharePoint
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/octet-stream,*/*"
        }
        response = requests.get(SHAREPOINT_URL, headers=headers, timeout=30, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "")
        if response.status_code == 200 and "html" not in content_type:
            df = pd.read_excel(io.BytesIO(response.content), sheet_name=sheet_name)
            df.columns = df.columns.str.strip()
            return df
    except Exception:
        pass

    # Fall back to local Excel on GitHub
    try:
        fp = _get_local_path()
        df = pd.read_excel(fp, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()
