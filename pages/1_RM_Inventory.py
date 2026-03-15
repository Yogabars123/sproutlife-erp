# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM BUTTON PATCH for RM_Inventory.py
# ══════════════════════════════════════════════════════════════════════════════
#
# ADD THESE TWO SECTIONS to your RM_Inventory.py file:
#
# 1. Paste the HELPER FUNCTIONS near the top (after imports)
# 2. Paste the BUTTON BLOCK at the bottom of the page (after your main table)
#
# ══════════════════════════════════════════════════════════════════════════════

# ── SECTION 1: Paste near top of RM_Inventory.py (after imports) ──────────────

import requests as _requests
from datetime import datetime as _datetime
import pytz as _pytz

_TG_TOKEN   = "8368375473:AAERuMSZGrdrvYKiGGQl9HIrdNzh-6a8eZQ"
_TG_CHAT_ID = "5667118823"
_IST        = _pytz.timezone("Asia/Kolkata")

_RM_SOH_WH = [
    "Central",
    "RM Warehouse Tumkur",
    "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse",
    "Tumkur New Warehouse",
    "HF Factory FG Warehouse",
    "Sproutlife Foods Private Ltd (SNOWMAN)",
]

def _tg_send(text: str) -> tuple[bool, str]:
    """Send HTML message to Telegram. Returns (success, error_msg)."""
    url    = f"https://api.telegram.org/bot{_TG_TOKEN}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            r = _requests.post(url, json={
                "chat_id":    _TG_CHAT_ID,
                "text":       chunk,
                "parse_mode": "HTML",
            }, timeout=15)
            if r.status_code != 200:
                return False, f"Telegram error {r.status_code}: {r.text}"
        except Exception as e:
            return False, str(e)
    return True, ""


def _build_rm_tg_message(df_rm, df_fc) -> str:
    """Build RM critical Telegram message from live DataFrames."""
    import pandas as pd

    NL  = chr(10)
    now = _datetime.now(_IST).strftime("%d %b %Y %I:%M %p IST")

    # ── SOH per SKU ──────────────────────────────────────────────────────────
    if "Warehouse" in df_rm.columns:
        df_rm = df_rm[df_rm["Warehouse"].astype(str).str.strip().isin(_RM_SOH_WH)].copy()
    if "Qty Available" in df_rm.columns:
        df_rm["Qty Available"] = pd.to_numeric(df_rm["Qty Available"], errors="coerce").fillna(0)

    soh = df_rm.groupby("Item SKU")["Qty Available"].sum().reset_index()
    soh.columns = ["Item SKU", "SOH"]

    name_map = {}
    if "Item Name" in df_rm.columns:
        name_map = df_rm.drop_duplicates("Item SKU").set_index("Item SKU")["Item Name"].to_dict()

    # ── Per-day from Forecast ─────────────────────────────────────────────────
    per_day = {}
    if not df_fc.empty:
        df_fc = df_fc.copy()
        df_fc.columns = df_fc.columns.str.strip()
        if "Location" in df_fc.columns:
            df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
        ic = next((c for c in df_fc.columns if "item code" in c.lower()), None)
        if ic and "Forecast" in df_fc.columns:
            df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
            fc_agg = df_fc[df_fc["Forecast"] > 0].groupby(ic)["Forecast"].sum()
            per_day = {str(k).strip().upper(): float(v) / 24 for k, v in fc_agg.items()}

    soh["_k"]          = soh["Item SKU"].astype(str).str.upper()
    soh["Per Day Req"] = soh["_k"].map(per_day).fillna(0)
    soh["Days of Stock"] = soh.apply(
        lambda r: round(r["SOH"] / r["Per Day Req"], 1) if r["Per Day Req"] > 0 else None,
        axis=1
    )
    soh["Item Name"] = soh["Item SKU"].map(name_map).fillna("")

    has_fc = soh[soh["Per Day Req"] > 0].copy()

    stockout = has_fc[has_fc["Days of Stock"].fillna(999) <= 1].sort_values("Days of Stock")
    critical = has_fc[(has_fc["Days of Stock"].fillna(999) > 1) &
                      (has_fc["Days of Stock"].fillna(999) < 7)].sort_values("Days of Stock")
    low      = has_fc[(has_fc["Days of Stock"].fillna(999) >= 7) &
                      (has_fc["Days of Stock"].fillna(999) <= 14)].sort_values("Days of Stock")

    lines = [
        "🌾 <b>YogaBar · RM Critical Stock</b>",
        "🕐 " + now,
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if stockout.empty and critical.empty and low.empty:
        lines.append("✅ All RM SKUs have healthy stock levels!")
    else:
        if not stockout.empty:
            lines.append("")
            lines.append("⛔ <b>STOCKOUT (" + str(len(stockout)) + " SKUs — ≤ 1 day left):</b>")
            for _, r in stockout.iterrows():
                lines.append(
                    "  • <code>" + str(r["Item SKU"]) + "</code>  " + str(r["Item Name"])[:35] + NL +
                    "    SOH: <b>" + f"{r['SOH']:,.0f}" + "</b>" +
                    "  Per Day: " + f"{r['Per Day Req']:,.1f}" +
                    "  <b>⛔ " + (f"{r['Days of Stock']:.1f}" if pd.notna(r["Days of Stock"]) else "0.0") + "d</b>"
                )

        if not critical.empty:
            lines.append("")
            lines.append("🔴 <b>Critical (" + str(len(critical)) + " SKUs — < 7 days):</b>")
            for _, r in critical.iterrows():
                lines.append(
                    "  • <code>" + str(r["Item SKU"]) + "</code>  " + str(r["Item Name"])[:35] + NL +
                    "    SOH: <b>" + f"{r['SOH']:,.0f}" + "</b>" +
                    "  Per Day: " + f"{r['Per Day Req']:,.1f}" +
                    "  DoS: <b>" + f"{r['Days of Stock']:.1f}" + "d</b>"
                )

        if not low.empty:
            lines.append("")
            lines.append("🟡 <b>Low (" + str(len(low)) + " SKUs — 7–14 days):</b>")
            for _, r in low.head(10).iterrows():
                lines.append(
                    "  • <code>" + str(r["Item SKU"]) + "</code>  " + str(r["Item Name"])[:35] +
                    "  <i>" + f"{r['Days of Stock']:.1f}" + "d</i>"
                )
            if len(low) > 10:
                lines.append("  <i>...and " + str(len(low) - 10) + " more</i>")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 <i>Live from Dashboard · YogaBar ERP</i>")
    return NL.join(lines)


# ── SECTION 2: Paste at the bottom of your RM tab in RM_Inventory.py ─────────
#
# USAGE: Wherever your RM table/display ends, add this code block.
# It uses the DataFrames already loaded by your page (df_rm and df_fc).
# Make sure df_rm and df_fc are in scope at the point you paste this.
#
# ─────────────────────────────────────────────────────────────────────────────

def render_rm_telegram_button(df_rm, df_fc):
    """
    Call this function at the bottom of your RM Inventory display.
    Pass the same df_rm (RM-Inventory sheet) and df_fc (Forecast sheet)
    that your page already has loaded.
    """
    import streamlit as st

    st.markdown("---")
    st.markdown("### 📬 Send RM Alert to Telegram")
    st.caption("Sends live RM critical/stockout data directly from this dashboard.")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📬 Send RM Critical Alert to Telegram", use_container_width=True,
                     key="tg_rm_btn"):
            with st.spinner("Building and sending RM report..."):
                try:
                    msg = _build_rm_tg_message(df_rm, df_fc)
                    ok, err = _tg_send(msg)
                    if ok:
                        st.success("✅ RM Critical report sent to Telegram!")
                    else:
                        st.error(f"❌ Send failed: {err}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    with col2:
        st.caption(f"→ Chat: {_TG_CHAT_ID}")
