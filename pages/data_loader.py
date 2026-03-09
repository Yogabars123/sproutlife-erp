import pandas as pd
import streamlit as st
import requests
import io

# ── OneDrive direct download URL ─────────────────────────────────────────────
ONEDRIVE_URL = "https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly9zcHJvdXRsaWZlMDEtbXkuc2hhcmVwb2ludC5jb20vOng6L2cvcGVyc29uYWwvYWJpbmF5YV9tX3lvZ2FiYXJzX2luL0lRQkx0SW9Ec1d0d1FaaUltQ0hrVzZCZUFhLVNuTmo3VUpkQXFqU2hoV2pIUzdVP2U9UUlibkZp/root/content"

@st.cache_data(ttl=300)  # Cache for 5 minutes — auto-refreshes live data
def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Fetch the latest Excel from OneDrive and return the requested sheet."""
    try:
        response = requests.get(ONEDRIVE_URL, timeout=30)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content), sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load data from OneDrive: {e}")
        return pd.DataFrame()
