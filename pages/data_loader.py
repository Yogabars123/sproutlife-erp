import pandas as pd
import streamlit as st
import requests
import io

# ── SharePoint direct download URL ───────────────────────────────────────────
# Adding download=1 forces SharePoint to return raw file bytes
ONEDRIVE_URL = "https://sproutlife01-my.sharepoint.com/:x:/g/personal/abinaya_m_yogabars_in/IQBLtIoDsWtwQZiImCHkW6BeAa-SnNj7UJdAqjShhWjHS7U?e=QIbnFi&download=1"

@st.cache_data(ttl=300)  # Cache for 5 minutes — auto-refreshes live data
def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Fetch the latest Excel from SharePoint/OneDrive and return the requested sheet."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(ONEDRIVE_URL, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content), sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load data from OneDrive: {e}")
        return pd.DataFrame()
