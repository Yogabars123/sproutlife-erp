"""
YogaBar · Inventory Digest
══════════════════════════
Sends a combined daily digest of:
  1. CFA FG Shortfall SKUs (which SKU is short at which CFA)
  2. RM Critical SKUs (< 7 days of stock)
at 10:00 AM and 3:00 PM IST.

SETUP:
1. Install dependencies:
       pip install pandas openpyxl schedule pytz requests

2. Fill in CONFIG section below (8368375473:AAERuMSZGrdrvYKiGGQl9HIrdNzh-6a8eZQ, 5667118823, https://sproutlife01-my.sharepoint.com/:x:/g/personal/abinaya_m_yogabars_in/IQBLtIoDsWtwQZiImCHkW6BeARmYhaC5YPlnyqVbJa5gOF0?e=bBGW7q)

3. GitHub Actions mode (recommended):
   - Add secrets TG_BOT_TOKEN, TG_CHAT_ID, ONEDRIVE_URL to your repo
   - Upload telegram_digest.yml to .github/workflows/
   - Run workflow manually to test

4. Local / server mode:
       python cfa_telegram_digest.py
   Or background:
       nohup python cfa_telegram_digest.py > digest.log 2>&1 &
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
#  CONFIG  ← Fill these in OR set as GitHub / environment secrets
# ══════════════════════════════════════════════════════════════════

BOT_TOKEN    = os.environ.get("TG_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID      = os.environ.get("TG_CHAT_ID",   "YOUR_CHAT_ID_HERE")

# For GitHub Actions: set ONEDRIVE_URL secret as your OneDrive share link
# For local use: FILE_PATH is used automatically
ONEDRIVE_URL = os.environ.get("ONEDRIVE_URL", "")
FILE_PATH    = r"C:\Users\YOGA BAR\OneDrive - SPROUTLIFE FOODS PRIVATE LIMITED\Sproutlife Inventory.xlsx"

# Send times IST (24h) — used in scheduler / local mode
SEND_TIMES_IST = ["10:00", "15:00"]

# ══════════════════════════════════════════════════════════════════
#  CONSTANTS  (must match fg_inventory.py and rm_inventory.py)
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
#  DATA LOADING
# ══════════════════════════════════════════════════════════════════

_excel_bytes_cache = None

def _get_excel_bytes() -> bytes:
    global _excel_bytes_cache
    if _excel_bytes_cache is not None:
        return _excel_bytes_cache

    if ONEDRIVE_URL:
        log.info("Downloading Excel from OneDrive...")
        direct = ONEDRIVE_URL.rstrip("/")
        if "1drv.ms" in direct or "sharepoint.com" in direct:
            direct = direct + ("&download=1" if "?" in direct else "?download=1")
        resp = requests.get(direct, timeout=60)
        resp.raise_for_status()
        _excel_bytes_cache = resp.content
        log.info(f"Downloaded {len(_excel_bytes_cache):,} bytes from OneDrive")
    else:
        log.info(f"Reading Excel from: {FILE_PATH}")
        with open(FILE_PATH, "rb") as f:
            _excel_bytes_cache = f.read()

    return _excel_bytes_cache


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
#  SECTION 1: CFA FG SHORTFALL
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
        log.error("FG-Inventory missing Warehouse or Item SKU")
        return result

    if "Qty Available" in df_fg.columns:
        df_fg["Qty Available"] = pd.to_numeric(df_fg["Qty Available"], errors="coerce").fillna(0)

    # FG at CFA warehouses
    df_cfa = df_fg[df_fg["Warehouse"].astype(str).str.strip().isin(CFA_WAREHOUSES)].copy()
    if df_cfa.empty:
        log.warning("No FG rows for CFA warehouses")
        return result

    item_name_col = "Item Name" if "Item Name" in df_cfa.columns else "Item SKU"
    fg_agg = df_cfa.groupby(["Item SKU", "Warehouse"]).agg(
        Item_Name=(item_name_col, "first"),
        FG_Stock =("Qty Available", "sum"),
    ).reset_index()
    fg_agg.columns = ["Item SKU", "CFA Warehouse", "Item Name", "FG Stock"]

    # STN in-transit
    stn_agg = pd.DataFrame(columns=["Item SKU", "CFA Warehouse", "STN In-Transit"])
    if not df_stn.empty:
        fg_code_col = next((c for c in df_stn.columns if "fg code" in c.lower() or "sku" in c.lower() or "code" in c.lower()), None)
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

    # Open SOS
    sku_col_so = next((c for c in df_sos.columns if "product sku" in c.lower()), None)
    wh_col_so  = next((c for c in df_sos.columns if c.lower() == "warehouse"), None)
    qty_col_so = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
    if not sku_col_so or not wh_col_so or not qty_col_so:
        log.error(f"SOS missing columns. Found: {list(df_sos.columns)}")
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

    # Merge
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

    # Central stock for STN check
    central_stock = {}
    central_rows = df_fg[df_fg["Warehouse"].astype(str).str.strip() == "Central"].copy()
    if not central_rows.empty:
        central_stock = central_rows.groupby("Item SKU")["Qty Available"].sum().to_dict()

    # Build per-CFA output
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
#  SECTION 2: RM CRITICAL STOCK
# ══════════════════════════════════════════════════════════════════

def get_rm_critical() -> dict:
    result = {"stockout": [], "critical": [], "low": []}

    df_rm = load_sheet("RM-Inventory")
    df_fc = load_sheet("Forecast")

    if df_rm.empty:
        log.warning("RM-Inventory sheet empty/missing")
        return result

    if "Warehouse" in df_rm.columns:
        df_rm = df_rm[df_rm["Warehouse"].astype(str).str.strip().isin(RM_SOH_WH)].copy()
    if "Qty Available" in df_rm.columns:
        df_rm["Qty Available"] = pd.to_numeric(df_rm["Qty Available"], errors="coerce").fillna(0)

    soh = df_rm.groupby("Item SKU")["Qty Available"].sum().reset_index()
    soh.columns = ["Item SKU", "SOH"]

    name_map = {}
    if "Item Name" in df_rm.columns:
        name_map = df_rm.drop_duplicates("Item SKU").set_index("Item SKU")["Item Name"].to_dict()

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

    soh["_k"]          = soh["Item SKU"].astype(str).str.upper()
    soh["Per Day Req"] = soh["_k"].map(per_day).fillna(0)
    soh["Days of Stock"] = soh.apply(
        lambda r: round(r["SOH"] / r["Per Day Req"], 1) if r["Per Day Req"] > 0 else None, axis=1)
    soh["Item Name"] = soh["Item SKU"].map(name_map).fillna("")

    has_fc = soh[soh["Per Day Req"] > 0].copy()

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
    NL      = chr(10)
    now_str = cfa_data["as_of"]
    total   = cfa_data["total_shortfall_skus"]
    cfas    = cfa_data["cfas"]

    lines = [
        "📊 <b>YogaBar · Inventory Digest</b>",
        "🕐 " + now_str,
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    # Section 1: FG CFA Shortfall
    lines.append("📦 <b>FG · CFA Shortfall</b>")
    if total == 0:
        lines.append("✅ All CFAs fully stocked — no shortfall today!")
    else:
        lines.append("⚠️ <b>" + str(total) + " shortfall SKU(s) across " + str(len(cfas)) + " CFA(s)</b>")
        lines.append("")
        for cd in cfas:
            cfa_name = cd["name"]
            cfa_diff = cd["total_diff"]
            sku_list = cd["shortfall_skus"]
            n_skus   = len(sku_list)
            n_stn_ok = sum(1 for s in sku_list if s["stn_status"] == "✅")
            n_stn_pt = sum(1 for s in sku_list if s["stn_status"] == "⚠️")
            n_stn_no = sum(1 for s in sku_list if s["stn_status"] == "❌")
            lines.append(
                "🏭 <b>" + cfa_name + "</b>  [" + str(n_skus) +
                " SKU" + ("s" if n_skus > 1 else "") +
                "  |  Net: " + f"{cfa_diff:+,.0f}" + "]"
            )
            for s in sku_list:
                lines.append(
                    "  • <code>" + s["sku"] + "</code>  " + s["name"] + NL +
                    "    Stock: <b>" + f"{s['fg_stock']:,.0f}" + "</b>" +
                    "  PO: " + f"{s['open_po']:,.0f}" +
                    "  Diff: <b>" + f"{s['diff']:+,.0f}" + "</b>" +
                    "  " + s["stn_status"] + " STN"
                )
            stn_parts = []
            if n_stn_ok: stn_parts.append("✅ " + str(n_stn_ok) + " possible")
            if n_stn_pt: stn_parts.append("⚠️ " + str(n_stn_pt) + " partial")
            if n_stn_no: stn_parts.append("❌ " + str(n_stn_no) + " no stock")
            if stn_parts:
                lines.append("  └ " + " · ".join(stn_parts))
            lines.append("")

    # Section 2: RM Critical
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
    global _excel_bytes_cache
    _excel_bytes_cache = None  # Fresh data each run

    log.info("⏰ Running combined inventory digest...")
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
    log.info("🚀 YogaBar Inventory Digest Scheduler starting...")
    log.info(f"   File  : {FILE_PATH if not ONEDRIVE_URL else 'OneDrive URL'}")
    log.info(f"   Times : {', '.join(SEND_TIMES_IST)} IST")
    log.info(f"   Chat  : {CHAT_ID}")

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        log.error("❌ Fill in BOT_TOKEN and CHAT_ID in CONFIG section!")
        return

    for t in SEND_TIMES_IST:
        h, m   = int(t.split(":")[0]), int(t.split(":")[1])
        ist_dt = IST.localize(datetime.now().replace(hour=h, minute=m, second=0, microsecond=0))
        utc_t  = ist_dt.astimezone(pytz.utc).strftime("%H:%M")
        schedule.every().day.at(utc_t).do(run_digest)
        log.info(f"   Scheduled: {t} IST  →  {utc_t} UTC")

    log.info("📤 Sending startup verification message...")
    run_digest()

    log.info("✅ Scheduler running. Press Ctrl+C to stop.")
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
