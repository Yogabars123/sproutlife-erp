"""
YogaBar · Inventory Digest
══════════════════════════
Reads from the same GitHub-hosted Excel file as the dashboard.
Sends CFA shortfall + RM critical stock digest at 10 AM and 3 PM IST.

Run modes:
  python cfa_telegram_digest.py          # scheduler (local/server)
  python cfa_telegram_digest.py --once   # GitHub Actions (run once)
"""

import os
import io
import sys
import time
import logging
import requests
import pandas as pd
import schedule
import pytz
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID   = os.environ.get("TG_CHAT_ID",   "YOUR_CHAT_ID_HERE")

# Same Excel source as dashboard and bot.py
FILE_URL  = "https://raw.githubusercontent.com/Yogabars123/sproutlife-erp/main/Sproutlife%20Inventory.xlsx"

SEND_TIMES_IST = ["10:00", "15:00"]

# ══════════════════════════════════════════════════════════════════
#  CONSTANTS — must match dashboard exactly
# ══════════════════════════════════════════════════════════════════

CFA_WAREHOUSES = [
    "Mumbai CFA",
    "Chennai CFA",
    "Kerala CFA",
    "Delhi -CFA GHEVRA",
    "Ahmedabad CFA",
    "Kolkata CFA",
    "Pune CFA",
    "Mithra Associates",
    "BENGALURU CFA",
]

# Channel stock warehouses (same as dashboard CHANNEL_STOCK_WAREHOUSES)
CHANNEL_STOCK_WH = ["Tumkur New Warehouse", "YB FG Warehouse"]

# Central warehouse for STN feasibility check
CENTRAL_WH = "Central"

# RM SOH warehouses
RM_SOH_WH = [
    "Central",
    "RM Warehouse Tumkur",
    "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse",
    "Tumkur New Warehouse",
    "HF Factory FG Warehouse",
    "Sproutlife Foods Private Ltd (SNOWMAN)",
]

CLOSED_STATUSES = {"cancelled", "closed"}
STN_OPEN        = {"raised", "approved", "in transit", "intransit", "in-transit", "pending"}

# ══════════════════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("digest.log", encoding="utf-8"),
    ]
)
log = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")

# ══════════════════════════════════════════════════════════════════
#  DATA LOADING — same GitHub URL as bot.py and dashboard
# ══════════════════════════════════════════════════════════════════

_excel_cache = None

def _get_excel_bytes() -> bytes:
    global _excel_cache
    if _excel_cache is not None:
        return _excel_cache
    log.info(f"Downloading Excel from GitHub: {FILE_URL}")
    resp = requests.get(FILE_URL, timeout=60)
    resp.raise_for_status()
    _excel_cache = resp.content
    log.info(f"Downloaded {len(_excel_cache):,} bytes")
    return _excel_cache


def load_sheet(sheet_name: str) -> pd.DataFrame:
    try:
        data = _get_excel_bytes()
        df   = pd.read_excel(io.BytesIO(data), sheet_name=sheet_name, engine="openpyxl")
        df.columns = df.columns.str.strip()
        log.info(f"Loaded '{sheet_name}': {len(df)} rows")
        return df
    except Exception as e:
        log.warning(f"Could not load '{sheet_name}': {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════
#  SECTION 1 — CFA FG SHORTFALL
#  Same logic as Tab 2 (CFA Stock vs Open Orders) in fg_inventory.py
# ══════════════════════════════════════════════════════════════════

def get_cfa_shortfall() -> dict:
    result = {
        "as_of": datetime.now(IST).strftime("%d %b %Y %I:%M %p IST"),
        "total_shortfall_skus": 0,
        "cfas": []
    }

    df_fg  = load_sheet("FG-Inventory")
    df_sos = load_sheet("SOS")
    df_stn = load_sheet("STN")

    if df_fg.empty or df_sos.empty:
        log.error("FG-Inventory or SOS sheet empty/missing")
        return result

    if "Warehouse" not in df_fg.columns or "Item SKU" not in df_fg.columns:
        log.error("FG-Inventory missing required columns")
        return result

    if "Qty Available" in df_fg.columns:
        df_fg["Qty Available"] = pd.to_numeric(df_fg["Qty Available"], errors="coerce").fillna(0)

    # ── FG stock at CFA warehouses ────────────────────────────────
    df_cfa = df_fg[df_fg["Warehouse"].astype(str).str.strip().isin(CFA_WAREHOUSES)].copy()
    if df_cfa.empty:
        log.warning("No FG rows found for CFA warehouses")
        return result

    item_name_col = "Item Name" if "Item Name" in df_cfa.columns else "Item SKU"
    fg_agg = df_cfa.groupby(["Item SKU", "Warehouse"]).agg(
        Item_Name=(item_name_col, "first"),
        FG_Stock =("Qty Available", "sum"),
    ).reset_index()
    fg_agg.columns = ["Item SKU", "CFA Warehouse", "Item Name", "FG Stock"]

    # ── STN in-transit to CFA ─────────────────────────────────────
    stn_agg = pd.DataFrame(columns=["Item SKU", "CFA Warehouse", "STN In-Transit"])
    if not df_stn.empty:
        fg_code_col = next((c for c in df_stn.columns
                            if "fg code" in c.lower() or "sku" in c.lower() or "code" in c.lower()), None)
        to_wh_col   = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None)
        stat_col    = next((c for c in df_stn.columns if c.lower() == "status"), None)
        qty_col     = next((c for c in df_stn.columns if c.lower() == "qty"), None)
        if fg_code_col and to_wh_col and stat_col and qty_col:
            df_stn[qty_col] = pd.to_numeric(df_stn[qty_col], errors="coerce").fillna(0)
            stn_f = df_stn[
                df_stn[to_wh_col].astype(str).str.strip().isin(CFA_WAREHOUSES) &
                df_stn[stat_col].astype(str).str.strip().str.lower().isin(STN_OPEN)
            ].copy()
            if not stn_f.empty:
                stn_f["_sku"] = stn_f[fg_code_col].astype(str).str.strip()
                stn_f["_wh"]  = stn_f[to_wh_col].astype(str).str.strip()
                stn_agg = stn_f.groupby(["_sku", "_wh"])[qty_col].sum().reset_index()
                stn_agg.columns = ["Item SKU", "CFA Warehouse", "STN In-Transit"]

    # ── Open SOS at CFA warehouses ────────────────────────────────
    sku_col_so = next((c for c in df_sos.columns if "product sku" in c.lower()), None)
    wh_col_so  = next((c for c in df_sos.columns if c.lower() == "warehouse"), None)
    qty_col_so = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
    if not sku_col_so or not wh_col_so or not qty_col_so:
        log.error(f"SOS missing required columns. Found: {list(df_sos.columns)}")
        return result

    df_sos[qty_col_so] = pd.to_numeric(df_sos[qty_col_so], errors="coerce").fillna(0)
    open_mask = ~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES) \
                if "SO Status" in df_sos.columns else pd.Series(True, index=df_sos.index)

    sos_open = df_sos[open_mask & df_sos[wh_col_so].astype(str).str.strip().isin(CFA_WAREHOUSES)].copy()
    if sos_open.empty:
        log.warning("No open SOS rows for CFA warehouses")
        return result

    sos_open["_sku"] = sos_open[sku_col_so].astype(str).str.strip()
    sos_open["_wh"]  = sos_open[wh_col_so].astype(str).str.strip()
    so_agg = sos_open.groupby(["_sku", "_wh"])[qty_col_so].sum().reset_index()
    so_agg.columns = ["Item SKU", "CFA Warehouse", "Open PO Qty"]

    # ── Merge FG + STN + SOS ─────────────────────────────────────
    merged = fg_agg.merge(stn_agg, on=["Item SKU", "CFA Warehouse"], how="outer")
    merged = merged.merge(so_agg,  on=["Item SKU", "CFA Warehouse"], how="outer")
    merged["FG Stock"]        = merged["FG Stock"].fillna(0)
    merged["STN In-Transit"]  = merged["STN In-Transit"].fillna(0)
    merged["Open PO Qty"]     = merged["Open PO Qty"].fillna(0)
    merged["Total Available"] = merged["FG Stock"] + merged["STN In-Transit"]
    merged["Diff"]            = merged["Total Available"] - merged["Open PO Qty"]
    merged["CFA Warehouse"]   = merged["CFA Warehouse"].fillna("")
    merged = merged[merged["CFA Warehouse"].isin(CFA_WAREHOUSES)]

    # Fill Item Name
    if "Item Name" in df_fg.columns:
        name_map = df_fg.drop_duplicates("Item SKU").set_index("Item SKU")["Item Name"].to_dict()
        merged["Item Name"] = merged.apply(
            lambda r: name_map.get(str(r["Item SKU"]).strip(), r["Item SKU"])
            if pd.isna(r.get("Item Name")) or str(r.get("Item Name", "")) == ""
            else r.get("Item Name", r["Item SKU"]), axis=1)
    else:
        merged["Item Name"] = merged["Item SKU"]

    # Central stock for STN feasibility
    central_stock = {}
    central_rows = df_fg[df_fg["Warehouse"].astype(str).str.strip() == CENTRAL_WH].copy()
    if not central_rows.empty:
        central_stock = central_rows.groupby("Item SKU")["Qty Available"].sum().to_dict()

    # Build shortfall list
    shortfall = merged[merged["Diff"] < 0].copy().sort_values("Diff")
    result["total_shortfall_skus"] = len(shortfall)

    for cfa in CFA_WAREHOUSES:
        cfa_rows = shortfall[shortfall["CFA Warehouse"] == cfa]
        if cfa_rows.empty:
            continue
        skus = []
        for _, r in cfa_rows.iterrows():
            sku      = str(r["Item SKU"]).strip()
            cen_qty  = float(central_stock.get(sku, 0))
            diff_abs = abs(float(r["Diff"]))
            stn_status = "✅" if cen_qty >= diff_abs else "⚠️" if cen_qty > 0 else "❌"
            skus.append({
                "sku":          sku,
                "name":         str(r.get("Item Name", sku))[:40],
                "fg_stock":     float(r["FG Stock"]),
                "stn_transit":  float(r["STN In-Transit"]),
                "open_po":      float(r["Open PO Qty"]),
                "diff":         float(r["Diff"]),
                "central_stock": cen_qty,
                "stn_status":   stn_status,
            })
        result["cfas"].append({
            "name":           cfa,
            "shortfall_skus": skus,
            "total_diff":     float(cfa_rows["Diff"].sum()),
        })

    return result


# ══════════════════════════════════════════════════════════════════
#  SECTION 2 — RM CRITICAL STOCK
#  Same logic as RM Inventory dashboard (Days of Stock calculation)
#  Per Day Req = Monthly Forecast / 26 working days
# ══════════════════════════════════════════════════════════════════

def get_rm_critical() -> dict:
    result = {"stockout": [], "critical": [], "low": []}

    df_rm = load_sheet("RM-Inventory")
    df_fc = load_sheet("Forecast")

    if df_rm.empty:
        log.warning("RM-Inventory sheet empty/missing")
        return result

    # Filter to SOH warehouses (same as dashboard)
    if "Warehouse" in df_rm.columns:
        df_rm = df_rm[df_rm["Warehouse"].astype(str).str.strip().isin(RM_SOH_WH)].copy()
    if "Qty Available" in df_rm.columns:
        df_rm["Qty Available"] = pd.to_numeric(df_rm["Qty Available"], errors="coerce").fillna(0)

    # SOH per SKU
    soh = df_rm.groupby("Item SKU")["Qty Available"].sum().reset_index()
    soh.columns = ["Item SKU", "SOH"]

    name_map = {}
    if "Item Name" in df_rm.columns:
        name_map = df_rm.drop_duplicates("Item SKU").set_index("Item SKU")["Item Name"].to_dict()

    # Forecast → Per Day = Monthly Forecast / 26
    per_day = {}
    if not df_fc.empty:
        df_fc.columns = df_fc.columns.str.strip()
        # Filter to Plant location (same as dashboard)
        if "Location" in df_fc.columns:
            df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
        ic = next((c for c in df_fc.columns if "item code" in c.lower()), None)
        if ic and "Forecast" in df_fc.columns:
            df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
            fc_agg = df_fc[df_fc["Forecast"] > 0].groupby(ic)["Forecast"].sum()
            per_day = {str(k).strip().upper(): float(v) / 26 for k, v in fc_agg.items()}

    soh["_k"]          = soh["Item SKU"].astype(str).str.upper()
    soh["Per Day Req"] = soh["_k"].map(per_day).fillna(0)
    soh["Days of Stock"] = soh.apply(
        lambda r: round(r["SOH"] / r["Per Day Req"], 1) if r["Per Day Req"] > 0 else None, axis=1)
    soh["Item Name"] = soh["Item SKU"].map(name_map).fillna("")

    has_fc = soh[soh["Per Day Req"] > 0].copy()

    # Bucket same thresholds as RM dashboard
    for _, r in has_fc[has_fc["Days of Stock"].fillna(999) <= 1].sort_values("Days of Stock").iterrows():
        result["stockout"].append({
            "sku": str(r["Item SKU"]), "name": str(r["Item Name"])[:35],
            "soh": float(r["SOH"]), "per_day": float(r["Per Day Req"]),
            "dos": float(r["Days of Stock"]) if pd.notna(r["Days of Stock"]) else 0.0,
        })
    for _, r in has_fc[
        (has_fc["Days of Stock"].fillna(999) > 1) & (has_fc["Days of Stock"].fillna(999) < 7)
    ].sort_values("Days of Stock").iterrows():
        result["critical"].append({
            "sku": str(r["Item SKU"]), "name": str(r["Item Name"])[:35],
            "soh": float(r["SOH"]), "per_day": float(r["Per Day Req"]),
            "dos": float(r["Days of Stock"]),
        })
    for _, r in has_fc[
        (has_fc["Days of Stock"].fillna(999) >= 7) & (has_fc["Days of Stock"].fillna(999) <= 14)
    ].sort_values("Days of Stock").iterrows():
        result["low"].append({
            "sku": str(r["Item SKU"]), "name": str(r["Item Name"])[:35],
            "soh": float(r["SOH"]), "per_day": float(r["Per Day Req"]),
            "dos": float(r["Days of Stock"]),
        })

    return result


# ══════════════════════════════════════════════════════════════════
#  MESSAGE BUILDER
# ══════════════════════════════════════════════════════════════════

def build_message(cfa_data: dict, rm_data: dict) -> str:
    NL    = chr(10)
    total = cfa_data["total_shortfall_skus"]
    cfas  = cfa_data["cfas"]

    lines = [
        "📊 <b>YogaBar · Inventory Digest</b>",
        "🕐 " + cfa_data["as_of"],
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    # ── Section 1: CFA FG Shortfall ──────────────────────────────
    lines.append("📦 <b>FG · CFA Shortfall</b>")
    if total == 0:
        lines.append("✅ All CFAs fully stocked — no shortfall today!")
    else:
        lines.append("⚠️ <b>" + str(total) + " shortfall SKU(s) across " + str(len(cfas)) + " CFA(s)</b>")
        lines.append("")
        for cd in cfas:
            n_skus   = len(cd["shortfall_skus"])
            n_ok     = sum(1 for s in cd["shortfall_skus"] if s["stn_status"] == "✅")
            n_pt     = sum(1 for s in cd["shortfall_skus"] if s["stn_status"] == "⚠️")
            n_no     = sum(1 for s in cd["shortfall_skus"] if s["stn_status"] == "❌")
            lines.append(
                "🏭 <b>" + cd["name"] + "</b>  [" +
                str(n_skus) + " SKU" + ("s" if n_skus > 1 else "") +
                "  |  Net: " + f"{cd['total_diff']:+,.0f}" + "]"
            )
            for s in cd["shortfall_skus"]:
                lines.append(
                    "  • <code>" + s["sku"] + "</code>  " + s["name"] + NL +
                    "    Stock: <b>" + f"{s['fg_stock']:,.0f}" + "</b>" +
                    "  PO: " + f"{s['open_po']:,.0f}" +
                    "  Diff: <b>" + f"{s['diff']:+,.0f}" + "</b>" +
                    "  " + s["stn_status"] + " STN"
                )
            stn_parts = []
            if n_ok: stn_parts.append("✅ " + str(n_ok) + " possible")
            if n_pt: stn_parts.append("⚠️ " + str(n_pt) + " partial")
            if n_no: stn_parts.append("❌ " + str(n_no) + " no stock")
            if stn_parts:
                lines.append("  └ " + " · ".join(stn_parts))
            lines.append("")

    # ── Section 2: RM Critical Stock ─────────────────────────────
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🌾 <b>RM · Critical Stock Alert</b>")

    stockout = rm_data.get("stockout", [])
    critical = rm_data.get("critical", [])
    low      = rm_data.get("low",      [])

    if not stockout and not critical and not low:
        lines.append("✅ All RM SKUs have healthy stock levels!")
    else:
        if stockout:
            lines.append("")
            lines.append("⛔ <b>STOCKOUT (" + str(len(stockout)) + " SKUs — ≤ 1 day left):</b>")
            for r in stockout:
                lines.append(
                    "  • <code>" + r["sku"] + "</code>  " + r["name"] + NL +
                    "    SOH: <b>" + f"{r['soh']:,.0f}" + "</b>" +
                    "  Per Day: " + f"{r['per_day']:,.1f}" +
                    "  <b>⛔ " + f"{r['dos']:.1f}" + "d</b>"
                )
        if critical:
            lines.append("")
            lines.append("🔴 <b>Critical (" + str(len(critical)) + " SKUs — < 7 days):</b>")
            for r in critical:
                lines.append(
                    "  • <code>" + r["sku"] + "</code>  " + r["name"] + NL +
                    "    SOH: <b>" + f"{r['soh']:,.0f}" + "</b>" +
                    "  Per Day: " + f"{r['per_day']:,.1f}" +
                    "  DoS: <b>" + f"{r['dos']:.1f}" + "d</b>"
                )
        if low:
            lines.append("")
            lines.append("🟡 <b>Low (" + str(len(low)) + " SKUs — 7–14 days):</b>")
            for r in low[:10]:
                lines.append(
                    "  • <code>" + r["sku"] + "</code>  " + r["name"] +
                    "  <i>" + f"{r['dos']:.1f}" + "d</i>"
                )
            if len(low) > 10:
                lines.append("  <i>...and " + str(len(low) - 10) + " more</i>")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 <i>Auto-digest · YogaBar ERP · Sproutlife Foods</i>")
    return NL.join(lines)


# ══════════════════════════════════════════════════════════════════
#  TELEGRAM SENDER
# ══════════════════════════════════════════════════════════════════

def send_telegram(text: str) -> bool:
    url     = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    chunks  = [text[i:i+4000] for i in range(0, len(text), 4000)]
    success = True
    for i, chunk in enumerate(chunks, 1):
        try:
            resp = requests.post(url, json={
                "chat_id":    CHAT_ID,
                "text":       chunk,
                "parse_mode": "HTML",
            }, timeout=15)
            if resp.status_code == 200:
                log.info(f"Telegram chunk {i}/{len(chunks)} sent ({len(chunk)} chars)")
            else:
                log.error(f"Telegram error {resp.status_code}: {resp.text}")
                success = False
        except Exception as e:
            log.error(f"Telegram send failed: {e}")
            success = False
    return success


# ══════════════════════════════════════════════════════════════════
#  MAIN JOB
# ══════════════════════════════════════════════════════════════════

def run_digest():
    global _excel_cache
    _excel_cache = None  # clear cache so fresh data is fetched each run

    log.info("⏰ Running inventory digest...")
    try:
        cfa_data = get_cfa_shortfall()
        rm_data  = get_rm_critical()
        message  = build_message(cfa_data, rm_data)
        ok       = send_telegram(message)
        if ok:
            log.info(
                "✅ Digest sent — "
                f"CFA: {cfa_data['total_shortfall_skus']} shortfall | "
                f"RM: {len(rm_data.get('stockout',[]))} stockout, "
                f"{len(rm_data.get('critical',[]))} critical, "
                f"{len(rm_data.get('low',[]))} low"
            )
        else:
            log.error("❌ Digest failed to send")
    except Exception as e:
        log.exception(f"Digest job crashed: {e}")


# ══════════════════════════════════════════════════════════════════
#  SCHEDULER
# ══════════════════════════════════════════════════════════════════

def main():
    log.info("🚀 YogaBar Inventory Digest starting...")
    log.info(f"   Source : {FILE_URL}")
    log.info(f"   Times  : {', '.join(SEND_TIMES_IST)} IST")
    log.info(f"   Chat   : {CHAT_ID}")

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        log.error("❌ Fill in BOT_TOKEN and CHAT_ID in CONFIG section!")
        return

    for t in SEND_TIMES_IST:
        # IMPORTANT: The `schedule` library uses the SYSTEM CLOCK, not UTC.
        # On your IST machine, schedule.at("10:00") fires at 10:00 IST.
        # Do NOT convert to UTC — that was causing wrong send times (e.g. 1 PM instead of 10 AM).
        schedule.every().day.at(t).do(run_digest)
        log.info(f"   Scheduled: {t} IST (system clock)")

    log.info("📤 Sending startup test message...")
    run_digest()

    log.info("✅ Scheduler running. Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(30)


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if "--once" in sys.argv:
        log.info("🚀 GitHub Actions one-shot mode...")
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
            log.error("❌ Set TG_BOT_TOKEN and TG_CHAT_ID as environment variables!")
            sys.exit(1)
        run_digest()
        log.info("✅ Done.")
    else:
        main()
