"""
YogaBar · Inventory Digest
══════════════════════════
Sends CFA FG Shortfall + RM Critical Stock to Telegram at 10 AM and 3 PM IST.

HOW TO RUN:
    python cfa_telegram_digest.py          ← keeps running, sends at 10 AM + 3 PM
    python cfa_telegram_digest.py --once   ← sends once and exits (GitHub Actions)
"""

import io
import os
import sys
import time
import logging
import requests
import pandas as pd
import schedule
import pytz
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
#  TELEGRAM CONFIG — hardcoded, no environment variable lookup
#  Bot: Inventory Assistant (8368375473)  ← same bot as dashboard button
# ══════════════════════════════════════════════════════════════════

TG_TOKEN   = "8368375473:AAERuMSZGrdrvYKiGGQl9HIrdNzh-6a8eZQ"
TG_CHAT_ID = "5667118823"

# ══════════════════════════════════════════════════════════════════
#  DATA SOURCE — reads the live local OneDrive file
#  Same file the dashboard reads → same data as the button
# ══════════════════════════════════════════════════════════════════

LOCAL_FILE = r"C:\Users\YOGA BAR\OneDrive - SPROUTLIFE FOODS PRIVATE LIMITED\Sproutlife Inventory.xlsx"

# GitHub Actions only — set ONEDRIVE_URL secret in repo if using Actions
GITHUB_ACTIONS_URL = os.environ.get("ONEDRIVE_URL", "")

# ══════════════════════════════════════════════════════════════════
#  SCHEDULE
# ══════════════════════════════════════════════════════════════════

SEND_TIMES_IST = ["10:00", "15:00"]

# ══════════════════════════════════════════════════════════════════
#  CONSTANTS
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
IST             = pytz.timezone("Asia/Kolkata")

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

# ══════════════════════════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════════════════════════

def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Load a sheet from the Excel file — local path or OneDrive URL."""
    try:
        if GITHUB_ACTIONS_URL:
            log.info(f"GitHub Actions: downloading from OneDrive URL...")
            url = GITHUB_ACTIONS_URL
            if "sharepoint.com" in url or "1drv.ms" in url:
                url = url + ("&download=1" if "?" in url else "?download=1")
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            data = io.BytesIO(resp.content)
        else:
            log.info(f"Local: reading {LOCAL_FILE}")
            data = LOCAL_FILE

        df = pd.read_excel(data, sheet_name=sheet_name, engine="openpyxl")
        df.columns = df.columns.str.strip()
        log.info(f"  Loaded '{sheet_name}': {len(df)} rows")
        return df
    except Exception as e:
        log.warning(f"  Could not load '{sheet_name}': {e}")
        return pd.DataFrame()

# ══════════════════════════════════════════════════════════════════
#  CFA SHORTFALL
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

    if "Qty Available" in df_fg.columns:
        df_fg["Qty Available"] = pd.to_numeric(df_fg["Qty Available"], errors="coerce").fillna(0)

    df_cfa = df_fg[df_fg["Warehouse"].astype(str).str.strip().isin(CFA_WAREHOUSES)].copy()
    if df_cfa.empty:
        log.warning("No FG rows for CFA warehouses")
        return result

    name_col = "Item Name" if "Item Name" in df_cfa.columns else "Item SKU"
    fg_agg = df_cfa.groupby(["Item SKU", "Warehouse"]).agg(
        Item_Name=(name_col, "first"),
        FG_Stock=("Qty Available", "sum"),
    ).reset_index()
    fg_agg.columns = ["Item SKU", "CFA Warehouse", "Item Name", "FG Stock"]

    # STN in-transit
    stn_agg = pd.DataFrame(columns=["Item SKU", "CFA Warehouse", "STN In-Transit"])
    if not df_stn.empty:
        fc = next((c for c in df_stn.columns if "fg code" in c.lower() or "sku" in c.lower() or "code" in c.lower()), None)
        tw = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None)
        sc = next((c for c in df_stn.columns if c.lower() == "status"), None)
        qc = next((c for c in df_stn.columns if c.lower() == "qty"), None)
        if fc and tw and sc and qc:
            df_stn[qc] = pd.to_numeric(df_stn[qc], errors="coerce").fillna(0)
            stn_f = df_stn[
                df_stn[tw].astype(str).str.strip().isin(CFA_WAREHOUSES) &
                df_stn[sc].astype(str).str.strip().str.lower().isin(STN_OPEN)
            ].copy()
            if not stn_f.empty:
                stn_f["_sku"] = stn_f[fc].astype(str).str.strip()
                stn_f["_wh"]  = stn_f[tw].astype(str).str.strip()
                stn_agg = stn_f.groupby(["_sku", "_wh"])[qc].sum().reset_index()
                stn_agg.columns = ["Item SKU", "CFA Warehouse", "STN In-Transit"]

    # Open SOS
    sc_so = next((c for c in df_sos.columns if "product sku" in c.lower()), None)
    wc_so = next((c for c in df_sos.columns if c.lower() == "warehouse"), None)
    qc_so = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
    if not sc_so or not wc_so or not qc_so:
        log.error(f"SOS missing columns. Found: {list(df_sos.columns)}")
        return result

    df_sos[qc_so] = pd.to_numeric(df_sos[qc_so], errors="coerce").fillna(0)
    if "SO Status" in df_sos.columns:
        open_mask = ~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)
    else:
        open_mask = pd.Series(True, index=df_sos.index)

    sos_open = df_sos[open_mask & df_sos[wc_so].astype(str).str.strip().isin(CFA_WAREHOUSES)].copy()
    if sos_open.empty:
        log.warning("No open SOS rows for CFA warehouses")
        return result

    sos_open["_sku"] = sos_open[sc_so].astype(str).str.strip()
    sos_open["_wh"]  = sos_open[wc_so].astype(str).str.strip()
    so_agg = sos_open.groupby(["_sku", "_wh"])[qc_so].sum().reset_index()
    so_agg.columns = ["Item SKU", "CFA Warehouse", "Open PO Qty"]

    merged = fg_agg.merge(stn_agg, on=["Item SKU", "CFA Warehouse"], how="outer")
    merged = merged.merge(so_agg,  on=["Item SKU", "CFA Warehouse"], how="outer")
    for col in ["FG Stock", "STN In-Transit", "Open PO Qty"]:
        merged[col] = merged[col].fillna(0)
    merged["Total Available"] = merged["FG Stock"] + merged["STN In-Transit"]
    merged["Diff"]            = merged["Total Available"] - merged["Open PO Qty"]
    merged["CFA Warehouse"]   = merged["CFA Warehouse"].fillna("")
    merged = merged[merged["CFA Warehouse"].isin(CFA_WAREHOUSES)]

    if "Item Name" in df_fg.columns:
        nm = df_fg.drop_duplicates("Item SKU").set_index("Item SKU")["Item Name"].to_dict()
        merged["Item Name"] = merged.apply(
            lambda r: nm.get(str(r["Item SKU"]).strip(), r["Item SKU"])
            if pd.isna(r.get("Item Name")) or str(r.get("Item Name", "")) == ""
            else r.get("Item Name", r["Item SKU"]), axis=1)
    else:
        merged["Item Name"] = merged["Item SKU"]

    central_stock = {}
    c_rows = df_fg[df_fg["Warehouse"].astype(str).str.strip() == "Central"].copy()
    if not c_rows.empty:
        central_stock = c_rows.groupby("Item SKU")["Qty Available"].sum().to_dict()

    shortfall = merged[merged["Diff"] < 0].copy().sort_values("Diff")
    result["total_shortfall_skus"] = len(shortfall)

    for cfa in CFA_WAREHOUSES:
        rows = shortfall[shortfall["CFA Warehouse"] == cfa]
        if rows.empty:
            continue
        skus = []
        for _, r in rows.iterrows():
            sku     = str(r["Item SKU"]).strip()
            cen     = float(central_stock.get(sku, 0))
            diff_a  = abs(float(r["Diff"]))
            status  = "✅" if cen >= diff_a else "⚠️" if cen > 0 else "❌"
            skus.append({
                "sku": sku, "name": str(r.get("Item Name", sku))[:40],
                "fg_stock": float(r["FG Stock"]), "open_po": float(r["Open PO Qty"]),
                "diff": float(r["Diff"]), "stn_status": status,
            })
        result["cfas"].append({
            "name": cfa, "shortfall_skus": skus,
            "total_diff": float(rows["Diff"].sum()),
        })
    return result

# ══════════════════════════════════════════════════════════════════
#  RM CRITICAL
# ══════════════════════════════════════════════════════════════════

def get_rm_critical() -> dict:
    result = {"stockout": [], "critical": [], "low": []}

    df_rm = load_sheet("RM-Inventory")
    df_fc = load_sheet("Forecast")

    if df_rm.empty:
        return result

    if "Warehouse" in df_rm.columns:
        df_rm = df_rm[df_rm["Warehouse"].astype(str).str.strip().isin(RM_SOH_WH)].copy()
    if "Qty Available" in df_rm.columns:
        df_rm["Qty Available"] = pd.to_numeric(df_rm["Qty Available"], errors="coerce").fillna(0)

    soh = df_rm.groupby("Item SKU")["Qty Available"].sum().reset_index()
    soh.columns = ["Item SKU", "SOH"]
    name_map = df_rm.drop_duplicates("Item SKU").set_index("Item SKU")["Item Name"].to_dict() \
               if "Item Name" in df_rm.columns else {}

    per_day = {}
    if not df_fc.empty:
        df_fc.columns = df_fc.columns.str.strip()
        if "Location" in df_fc.columns:
            df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
        ic = next((c for c in df_fc.columns if "item code" in c.lower()), None)
        if ic and "Forecast" in df_fc.columns:
            df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
            fc_agg = df_fc[df_fc["Forecast"] > 0].groupby(ic)["Forecast"].sum()
            per_day = {str(k).strip().upper(): float(v) / 24 for k, v in fc_agg.items()}

    soh["_k"]           = soh["Item SKU"].astype(str).str.upper()
    soh["Per Day Req"]  = soh["_k"].map(per_day).fillna(0)
    soh["Days of Stock"] = soh.apply(
        lambda r: round(r["SOH"] / r["Per Day Req"], 1) if r["Per Day Req"] > 0 else None, axis=1)
    soh["Item Name"] = soh["Item SKU"].map(name_map).fillna("")
    has_fc = soh[soh["Per Day Req"] > 0].copy()

    for _, r in has_fc[has_fc["Days of Stock"].fillna(999) <= 1].sort_values("Days of Stock").iterrows():
        result["stockout"].append({"sku": str(r["Item SKU"]), "name": str(r["Item Name"])[:35],
            "soh": float(r["SOH"]), "per_day": float(r["Per Day Req"]),
            "dos": float(r["Days of Stock"]) if pd.notna(r["Days of Stock"]) else 0.0})
    for _, r in has_fc[(has_fc["Days of Stock"].fillna(999) > 1) & (has_fc["Days of Stock"].fillna(999) < 7)].sort_values("Days of Stock").iterrows():
        result["critical"].append({"sku": str(r["Item SKU"]), "name": str(r["Item Name"])[:35],
            "soh": float(r["SOH"]), "per_day": float(r["Per Day Req"]), "dos": float(r["Days of Stock"])})
    for _, r in has_fc[(has_fc["Days of Stock"].fillna(999) >= 7) & (has_fc["Days of Stock"].fillna(999) <= 14)].sort_values("Days of Stock").iterrows():
        result["low"].append({"sku": str(r["Item SKU"]), "name": str(r["Item Name"])[:35],
            "soh": float(r["SOH"]), "per_day": float(r["Per Day Req"]), "dos": float(r["Days of Stock"])})
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
        "📦 <b>FG · CFA Shortfall</b>",
    ]

    if total == 0:
        lines.append("✅ All CFAs fully stocked — no shortfall today!")
    else:
        lines.append("⚠️ <b>" + str(total) + " shortfall SKU(s) across " + str(len(cfas)) + " CFA(s)</b>")
        lines.append("")
        for cd in cfas:
            sku_list = cd["shortfall_skus"]
            n = len(sku_list)
            lines.append("🏭 <b>" + cd["name"] + "</b>  [" + str(n) + " SKU" + ("s" if n > 1 else "") +
                         "  |  Net: " + f"{cd['total_diff']:+,.0f}" + "]")
            for s in sku_list:
                lines.append("  • <code>" + s["sku"] + "</code>  " + s["name"] + NL +
                             "    Stock: <b>" + f"{s['fg_stock']:,.0f}" + "</b>" +
                             "  PO: " + f"{s['open_po']:,.0f}" +
                             "  Diff: <b>" + f"{s['diff']:+,.0f}" + "</b>  " + s["stn_status"] + " STN")
            ok  = sum(1 for s in sku_list if s["stn_status"] == "✅")
            pt  = sum(1 for s in sku_list if s["stn_status"] == "⚠️")
            no  = sum(1 for s in sku_list if s["stn_status"] == "❌")
            parts = []
            if ok: parts.append("✅ " + str(ok) + " possible")
            if pt: parts.append("⚠️ " + str(pt) + " partial")
            if no: parts.append("❌ " + str(no) + " no stock")
            if parts: lines.append("  └ " + " · ".join(parts))
            lines.append("")

    lines += ["━━━━━━━━━━━━━━━━━━━━━━━━", "🌾 <b>RM · Critical Stock Alert</b>"]

    stockout = rm_data.get("stockout", [])
    critical = rm_data.get("critical", [])
    low      = rm_data.get("low",      [])

    if not stockout and not critical and not low:
        lines.append("✅ All RM SKUs have healthy stock levels!")
    else:
        if stockout:
            lines += ["", "⛔ <b>STOCKOUT (" + str(len(stockout)) + " SKUs — ≤ 1 day left):</b>"]
            for r in stockout:
                lines.append("  • <code>" + r["sku"] + "</code>  " + r["name"] + NL +
                             "    SOH: <b>" + f"{r['soh']:,.0f}" + "</b>  Per Day: " + f"{r['per_day']:,.1f}" +
                             "  <b>⛔ " + f"{r['dos']:.1f}" + "d</b>")
        if critical:
            lines += ["", "🔴 <b>Critical (" + str(len(critical)) + " SKUs — < 7 days):</b>"]
            for r in critical:
                lines.append("  • <code>" + r["sku"] + "</code>  " + r["name"] + NL +
                             "    SOH: <b>" + f"{r['soh']:,.0f}" + "</b>  Per Day: " + f"{r['per_day']:,.1f}" +
                             "  DoS: <b>" + f"{r['dos']:.1f}" + "d</b>")
        if low:
            lines += ["", "🟡 <b>Low (" + str(len(low)) + " SKUs — 7–14 days):</b>"]
            for r in low[:10]:
                lines.append("  • <code>" + r["sku"] + "</code>  " + r["name"] + "  <i>" + f"{r['dos']:.1f}" + "d</i>")
            if len(low) > 10:
                lines.append("  <i>...and " + str(len(low) - 10) + " more</i>")

    lines += ["", "━━━━━━━━━━━━━━━━━━━━━━━━", "🤖 <i>Auto-digest · YogaBar ERP · Sproutlife Foods</i>"]
    return NL.join(lines)

# ══════════════════════════════════════════════════════════════════
#  TELEGRAM SENDER
# ══════════════════════════════════════════════════════════════════

def send_telegram(text: str) -> bool:
    url     = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    chunks  = [text[i:i+4000] for i in range(0, len(text), 4000)]
    success = True
    for i, chunk in enumerate(chunks, 1):
        try:
            resp = requests.post(url, json={"chat_id": TG_CHAT_ID, "text": chunk, "parse_mode": "HTML"}, timeout=15)
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
    log.info("⏰ Running inventory digest...")
    log.info(f"   Using bot token starting with: {TG_TOKEN[:20]}...")
    log.info(f"   Sending to chat ID: {TG_CHAT_ID}")
    log.info(f"   Data source: {LOCAL_FILE if not GITHUB_ACTIONS_URL else 'OneDrive URL'}")
    try:
        cfa_data = get_cfa_shortfall()
        rm_data  = get_rm_critical()
        message  = build_message(cfa_data, rm_data)
        ok       = send_telegram(message)
        if ok:
            log.info(f"✅ Sent — CFA: {cfa_data['total_shortfall_skus']} shortfall | "
                     f"RM: {len(rm_data.get('stockout',[]))} stockout, "
                     f"{len(rm_data.get('critical',[]))} critical")
        else:
            log.error("❌ Failed to send")
    except Exception as e:
        log.exception(f"Digest crashed: {e}")

# ══════════════════════════════════════════════════════════════════
#  SCHEDULER / ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def main():
    log.info("🚀 Inventory Digest Scheduler starting...")
    log.info(f"   Bot  : {TG_TOKEN[:20]}...")
    log.info(f"   Chat : {TG_CHAT_ID}")
    log.info(f"   File : {LOCAL_FILE}")
    log.info(f"   Times: {', '.join(SEND_TIMES_IST)} IST (system clock)")

    # schedule uses system clock — on IST machine, pass IST times directly
    for t in SEND_TIMES_IST:
        schedule.every().day.at(t).do(run_digest)
        log.info(f"   Scheduled: {t} IST")

    log.info("📤 Sending startup test message now...")
    run_digest()

    log.info("✅ Scheduler running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    if "--once" in sys.argv:
        log.info("🚀 One-shot mode (GitHub Actions)...")
        run_digest()
        log.info("✅ Done.")
    else:
        main()
