import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="Consumption vs Forecast", layout="wide")

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .metric-card .label {
        font-size: 13px;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .metric-card .sub {
        font-size: 12px;
        opacity: 0.65;
        margin-top: 4px;
    }
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Consumption vs Forecast")
st.caption("Material-wise comparison of actual consumption against forecast")

@st.cache_data
def load_data():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")

    # Consumption
    df_con = pd.read_excel(file_path, sheet_name="Consumption")
    df_con.columns = df_con.columns.str.strip()
    if "Material Code" in df_con.columns:
        df_con["Material Code"] = df_con["Material Code"].astype(str).str.strip().str.upper()
    if "Consumed (As per BOM)" in df_con.columns:
        df_con["Consumed (As per BOM)"] = pd.to_numeric(df_con["Consumed (As per BOM)"], errors="coerce").fillna(0)
    if "Batch Date" in df_con.columns:
        df_con["Batch Date"] = pd.to_datetime(df_con["Batch Date"], errors="coerce")

    # Forecast
    xl = pd.ExcelFile(file_path)
    sheet = next((s for s in xl.sheet_names if s.lower() == "forecast"), None)
    df_fc = pd.read_excel(file_path, sheet_name=sheet)
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"]
    df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]

    # Normalize item code
    ic_col = "Item code" if "Item code" in df_fc.columns else "Item Code"
    df_fc[ic_col] = df_fc[ic_col].astype(str).str.strip().str.upper()
    df_fc = df_fc.rename(columns={ic_col: "Item Code"})

    # Get product name from forecast if available
    fc_cols = ["Item Code", "Forecast"]
    if "Product Name" in df_fc.columns:
        fc_cols.append("Product Name")
    df_fc = df_fc[fc_cols].drop_duplicates(subset="Item Code")

    return df_con, df_fc

df_con, df_fc = load_data()

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------
f1, f2, f3 = st.columns([3, 2, 2])

with f1:
    search = st.text_input("Search (Material Code / Name)", placeholder="Type to search...")

with f2:
    if "Batch Date" in df_con.columns:
        months = ["All Months"] + sorted(
            df_con["Batch Date"].dropna().dt.strftime("%b-%Y").unique().tolist()
        )
        selected_month = st.selectbox("Month", months)
    else:
        selected_month = "All Months"

with f3:
    variance_filter = st.selectbox("Variance", [
        "All",
        "Over Consumed (Actual > Forecast)",
        "Under Consumed (Actual < Forecast)"
    ])

# ---------------------------------------------------
# APPLY FILTERS TO CONSUMPTION
# ---------------------------------------------------
df_filtered = df_con.copy()

if search:
    df_filtered = df_filtered[df_filtered.astype(str).apply(
        lambda x: x.str.contains(search, case=False).any(), axis=1
    )]

if selected_month != "All Months" and "Batch Date" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Batch Date"].dt.strftime("%b-%Y") == selected_month]

# ---------------------------------------------------
# AGGREGATE CONSUMPTION BY MATERIAL CODE
# ---------------------------------------------------
con_agg = df_filtered.groupby("Material Code").agg(
    Material_Name=("Material Name", "first"),
    Actual_Consumption=("Consumed (As per BOM)", "sum")
).reset_index()

# Merge with forecast
con_agg["_key"] = con_agg["Material Code"].astype(str).str.strip().str.upper()
df_fc["_key"] = df_fc["Item Code"].astype(str).str.strip().str.upper()
merged = con_agg.merge(df_fc[["_key", "Forecast"]], on="_key", how="left")
merged = merged.drop(columns=["_key"])
merged["Forecast"] = merged["Forecast"].fillna(0)

# Variance calculations
merged["Variance"] = merged["Actual_Consumption"] - merged["Forecast"]
merged["Variance (%)"] = merged.apply(
    lambda r: round((r["Variance"] / r["Forecast"]) * 100, 1) if r["Forecast"] > 0 else None,
    axis=1
)
merged["Status"] = merged.apply(
    lambda r: "🔴 Over" if r["Variance"] > 0 else ("🟢 Under" if r["Variance"] < 0 else "✅ On Track"),
    axis=1
)

# Apply variance filter
if variance_filter == "Over Consumed (Actual > Forecast)":
    merged = merged[merged["Variance"] > 0]
elif variance_filter == "Under Consumed (Actual < Forecast)":
    merged = merged[merged["Variance"] < 0]

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------
st.divider()

total_actual   = merged["Actual_Consumption"].sum()
total_forecast = merged["Forecast"].sum()
over_count     = (merged["Variance"] > 0).sum()
under_count    = (merged["Variance"] < 0).sum()
total_variance = merged["Variance"].sum()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Actual Consumption</div>
        <div class="value">{total_actual:,.0f}</div>
        <div class="sub">{len(merged):,} materials</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #1a5c38 0%, #27855a 100%);">
        <div class="label">Total Forecast</div>
        <div class="value">{total_forecast:,.0f}</div>
        <div class="sub">Expected consumption</div>
    </div>""", unsafe_allow_html=True)

with k3:
    color = "#7b2d2d" if total_variance > 0 else "#1a5c38"
    color2 = "#b94040" if total_variance > 0 else "#27855a"
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color2} 100%);">
        <div class="label">Total Variance</div>
        <div class="value">{total_variance:+,.0f}</div>
        <div class="sub">{"Over consumed" if total_variance > 0 else "Under consumed"}</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #7b5a1a 0%, #b88a30 100%);">
        <div class="label">Over / Under Items</div>
        <div class="value">{over_count} / {under_count}</div>
        <div class="sub">Over consumed / Under consumed</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------
# TABLE
# ---------------------------------------------------
r1, r2 = st.columns([6, 2])
with r1:
    st.markdown(f'<div class="section-title">📋 Showing {len(merged):,} materials</div>', unsafe_allow_html=True)
with r2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        merged.to_excel(writer, index=False, sheet_name="Consumption vs Forecast")
    st.download_button(
        label="⬇️ Download as Excel",
        data=buffer.getvalue(),
        file_name="Consumption_vs_Forecast.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

def highlight_rows(row):
    if "Variance" in row.index:
        if row["Variance"] > 0:
            return ["background-color: #ffd6d6"] * len(row)
        elif row["Variance"] < 0:
            return ["background-color: #d6f5e3"] * len(row)
    return [""] * len(row)

merged_display = merged.rename(columns={
    "Material Code": "Material Code",
    "Material_Name": "Material Name",
    "Actual_Consumption": "Actual Consumption",
})

st.dataframe(
    merged_display.style.apply(highlight_rows, axis=1),
    use_container_width=True,
    height=500,
    hide_index=True,
    column_config={
        "Actual Consumption": st.column_config.NumberColumn("Actual Consumption", format="%.2f"),
        "Forecast": st.column_config.NumberColumn("Forecast", format="%.0f"),
        "Variance": st.column_config.NumberColumn("Variance", format="%+.2f"),
        "Variance (%)": st.column_config.NumberColumn("Variance (%)", format="%+.1f%%"),
    }
)
st.caption("🔴 Red = Over consumed (Actual > Forecast)  |  🟢 Green = Under consumed (Actual < Forecast)")
