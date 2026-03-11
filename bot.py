import pandas as pd
import time
import traceback
import requests
import io
from difflib import get_close_matches
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ================= CONFIG =================
TOKEN = "8368375473:AAERuMSZGrdrvYKiGGQl9HIrdNzh-6a8eZQ"
FILE_PATH = "https://raw.githubusercontent.com/Yogabars123/sproutlife-erp/main/Sproutlife%20Inventory.xlsx"
CACHE_REFRESH_SECONDS = 300
MAX_MESSAGE_LENGTH = 4000

# ================= WAREHOUSES =================
RM_DISPLAY_WAREHOUSES = [
    "Central",
    "Central Production -Bar Line",
    "Central Production - Oats Line",
    "Central Production - Peanut Line",
    "Central Production - Muesli Line",
    "RM Warehouse Tumkur",
    "Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse",
    "Central Production -Packing",
    "Tumkur New Warehouse",
    "HF Factory FG Warehouse",
    "Sproutlife Foods Private Ltd (SNOWMAN)"
]

# ================= CACHE =================
df_rm_cache = None
df_grn_cache = None
df_forecast_cache = None
df_cons_cache = None
df_fg_cache = None
last_refresh_time = 0


async def send_long(update, text):
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        await update.message.reply_text(text[i:i + MAX_MESSAGE_LENGTH])


# ================= LOAD DATA =================
def load_data():
    global df_rm_cache, df_grn_cache, df_forecast_cache, df_cons_cache, df_fg_cache, last_refresh_time

    if time.time() - last_refresh_time > CACHE_REFRESH_SECONDS:

        print("Downloading Excel from GitHub...")
        response = requests.get(FILE_PATH, timeout=60)

        if response.status_code != 200:
            raise Exception("Failed to download Excel from GitHub")

        excel_file = io.BytesIO(response.content)

        # RM
        df_rm = pd.read_excel(excel_file, sheet_name="RM-Inventory")
        df_rm.columns = df_rm.columns.str.strip()
        df_rm["Item SKU"] = df_rm["Item SKU"].astype(str).str.strip()
        df_rm["Item Name"] = df_rm["Item Name"].astype(str).str.strip()
        df_rm["Warehouse"] = df_rm["Warehouse"].astype(str).str.strip()
        df_rm["Qty Available"] = pd.to_numeric(df_rm["Qty Available"], errors="coerce").fillna(0)
        df_rm["CleanSKU"] = df_rm["Item SKU"].str.lower()

        excel_file.seek(0)

        # GRN
        df_grn = pd.read_excel(excel_file, sheet_name="GRN-Data")
        df_grn.columns = df_grn.columns.str.strip()

        excel_file.seek(0)

        # Forecast
        df_forecast = pd.read_excel(excel_file, sheet_name="Forecast")
        df_forecast.columns = df_forecast.columns.str.strip()

        excel_file.seek(0)

        # Consumption
        df_cons = pd.read_excel(excel_file, sheet_name="Consumption")
        df_cons.columns = df_cons.columns.str.strip()

        excel_file.seek(0)

        # FG
        df_fg = pd.read_excel(excel_file, sheet_name="FG-Inventory")
        df_fg.columns = df_fg.columns.str.strip()
        df_fg["Item SKU"] = df_fg["Item SKU"].astype(str).str.strip()
        df_fg["Item Name"] = df_fg["Item Name"].astype(str).str.strip()
        df_fg["Warehouse"] = df_fg["Warehouse"].astype(str).str.strip()
        df_fg["Qty Available"] = pd.to_numeric(df_fg["Qty Available"], errors="coerce").fillna(0)
        df_fg["CleanSKU"] = df_fg["Item SKU"].str.lower()

        df_rm_cache = df_rm
        df_grn_cache = df_grn
        df_forecast_cache = df_forecast
        df_cons_cache = df_cons
        df_fg_cache = df_fg
        last_refresh_time = time.time()

        print("Excel loaded successfully")

    return df_rm_cache, df_grn_cache, df_forecast_cache, df_cons_cache, df_fg_cache


# ================= SEARCH ITEM =================
def find_item(query, df_rm, df_fg):
    """
    Search RM and FG by SKU (partial) or item name (keyword).
    Returns list of dicts: {sku, name, type} where type is 'rm' or 'fg'
    """
    q = query.lower().strip()
    results = []
    seen = set()

    # Search RM by SKU
    for _, row in df_rm[df_rm["CleanSKU"].str.contains(q, na=False)].iterrows():
        key = ("rm", row["Item SKU"])
        if key not in seen:
            results.append({"sku": row["Item SKU"], "name": row["Item Name"], "type": "rm"})
            seen.add(key)

    # Search FG by SKU
    for _, row in df_fg[df_fg["CleanSKU"].str.contains(q, na=False)].iterrows():
        key = ("fg", row["Item SKU"])
        if key not in seen:
            results.append({"sku": row["Item SKU"], "name": row["Item Name"], "type": "fg"})
            seen.add(key)

    # Search RM by name
    for _, row in df_rm[df_rm["Item Name"].str.lower().str.contains(q, na=False)].iterrows():
        key = ("rm", row["Item SKU"])
        if key not in seen:
            results.append({"sku": row["Item SKU"], "name": row["Item Name"], "type": "rm"})
            seen.add(key)

    # Search FG by name
    for _, row in df_fg[df_fg["Item Name"].str.lower().str.contains(q, na=False)].iterrows():
        key = ("fg", row["Item SKU"])
        if key not in seen:
            results.append({"sku": row["Item SKU"], "name": row["Item Name"], "type": "fg"})
            seen.add(key)

    return results


def build_menu(sku, item_type):
    """Build inline keyboard: Stock | GRN | Consumption | Forecast"""
    keyboard = [
        [
            InlineKeyboardButton("📦 Stock",       callback_data=f"stock|{item_type}|{sku}"),
            InlineKeyboardButton("🚚 GRN",          callback_data=f"grn|{item_type}|{sku}"),
        ],
        [
            InlineKeyboardButton("🔥 Consumption", callback_data=f"cons|{item_type}|{sku}"),
            InlineKeyboardButton("📈 Forecast",    callback_data=f"forecast|{item_type}|{sku}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ================= DATA FORMATTERS =================

def fmt_stock(sku, item_type, df_rm, df_fg):
    q = sku.lower()
    if item_type == "rm":
        matches = df_rm[
            (df_rm["CleanSKU"].str.contains(q))
            & (df_rm["Warehouse"].isin(RM_DISPLAY_WAREHOUSES))
        ]
        if matches.empty:
            return "❌ No RM stock found."
        item_name = matches.iloc[0]["Item Name"]
        summary = matches.groupby("Warehouse")["Qty Available"].sum().reset_index()
        reply = f"📦 RM STOCK\nItem: {item_name}\nSKU: {sku}\n\n"
        for _, row in summary.iterrows():
            reply += f"{row['Warehouse']} → {int(row['Qty Available'])}\n"
        reply += f"\nTotal: {int(summary['Qty Available'].sum())}"
        return reply
    else:
        matches = df_fg[df_fg["CleanSKU"].str.contains(q)]
        if matches.empty:
            return "❌ No FG stock found."
        item_name = matches.iloc[0]["Item Name"]
        summary = matches.groupby("Warehouse")["Qty Available"].sum().reset_index()
        reply = f"📦 FG STOCK\nItem: {item_name}\nSKU: {sku}\n\n"
        for _, row in summary.iterrows():
            reply += f"{row['Warehouse']} → {int(row['Qty Available'])}\n"
        reply += f"\nTotal: {int(summary['Qty Available'].sum())}"
        return reply


def _search_df(df, sku):
    """Find rows in any sheet matching the SKU across likely columns."""
    q = sku.lower()
    sku_col = next(
        (col for col in df.columns if "sku" in col.lower()
         or ("item" in col.lower() and "code" in col.lower())),
        None
    )
    if sku_col:
        return df[df[sku_col].astype(str).str.lower().str.contains(q, na=False)]
    # fallback: scan all columns
    return df[df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)]


def fmt_grn(sku, df_grn):
    matches = _search_df(df_grn, sku)
    if matches.empty:
        return f"❌ No GRN records found for {sku}."
    reply = f"🚚 GRN HISTORY\nSKU: {sku}\n\n"
    reply += matches.to_string(index=False)
    return reply


def fmt_consumption(sku, df_cons):
    matches = _search_df(df_cons, sku)
    if matches.empty:
        return f"❌ No consumption records found for {sku}."
    reply = f"🔥 CONSUMPTION\nSKU: {sku}\n\n"
    reply += matches.to_string(index=False)
    return reply


def fmt_forecast(sku, df_forecast):
    matches = _search_df(df_forecast, sku)
    if matches.empty:
        return f"❌ No forecast records found for {sku}."
    reply = f"📈 FORECAST\nSKU: {sku}\n\n"
    reply += matches.to_string(index=False)
    return reply


# ================= TELEGRAM MESSAGE HANDLER =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text.strip()
        lower = user_input.lower()

        df_rm, df_grn, df_forecast, df_cons, df_fg = load_data()

        # ── Help ────────────────────────────────────────────────
        if lower == "help":
            help_text = (
                "🤖 *Sproutlife ERP Bot*\n\n"
                "Type a *SKU* or *item name* — bot finds the item and shows buttons:\n"
                "📦 Stock  |  🚚 GRN  |  🔥 Consumption  |  📈 Forecast\n\n"
                "_Examples:_\n"
                "`10704`\n"
                "`rolled oats`\n"
                "`peanut butter`\n\n"
                "Legacy prefix commands still work:\n"
                "`rm-[sku]`  `fg-[sku]`"
            )
            await update.message.reply_text(help_text, parse_mode="Markdown")
            return

        # ── Legacy prefix commands (unchanged logic) ────────────
        if lower.startswith("fg-"):
            code = lower.replace("fg-", "")
            fg_matches = df_fg[df_fg["CleanSKU"].str.contains(code)]
            if fg_matches.empty:
                await update.message.reply_text("❌ No FG stock found.")
                return
            item_name = fg_matches.iloc[0]["Item Name"]
            reply = f"📦 FG STOCK\nItem: {item_name}\n\n"
            summary = fg_matches.groupby("Warehouse")["Qty Available"].sum().reset_index()
            for _, row in summary.iterrows():
                reply += f"{row['Warehouse']} → {int(row['Qty Available'])}\n"
            await send_long(update, reply)
            return

        if lower.startswith("rm-"):
            code = lower.replace("rm-", "")
            rm_display = df_rm[
                (df_rm["CleanSKU"].str.contains(code))
                & (df_rm["Warehouse"].isin(RM_DISPLAY_WAREHOUSES))
            ]
            if rm_display.empty:
                await update.message.reply_text("❌ No RM stock found.")
                return
            item_name = rm_display.iloc[0]["Item Name"]
            reply = f"📦 RM STOCK\nItem: {item_name}\n\n"
            summary = rm_display.groupby("Warehouse")["Qty Available"].sum().reset_index()
            for _, row in summary.iterrows():
                reply += f"{row['Warehouse']} → {int(row['Qty Available'])}\n"
            await send_long(update, reply)
            return

        # ── Smart search → inline keyboard ─────────────────────
        results = find_item(user_input, df_rm, df_fg)

        if not results:
            await update.message.reply_text(
                f"❌ No items found for *{user_input}*.\n\nTry a different SKU or keyword.\nType `help` for usage.",
                parse_mode="Markdown"
            )
            return

        if len(results) == 1:
            # Single match — show item card + 4 buttons
            item = results[0]
            text = (
                f"✅ *{item['name']}*\n"
                f"SKU: `{item['sku']}`  |  Type: {item['type'].upper()}\n\n"
                "What would you like to see?"
            )
            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=build_menu(item["sku"], item["type"])
            )
        else:
            # Multiple matches — one row of buttons per item
            await update.message.reply_text(
                f"🔍 Found *{len(results)}* item(s) for _{user_input}_. Select one:",
                parse_mode="Markdown"
            )
            for item in results[:10]:
                label = f"[{item['type'].upper()}] {item['sku']} — {item['name']}"
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("📦 Stock",      callback_data=f"stock|{item['type']}|{item['sku']}"),
                    InlineKeyboardButton("🚚 GRN",         callback_data=f"grn|{item['type']}|{item['sku']}"),
                    InlineKeyboardButton("🔥 Cons",        callback_data=f"cons|{item['type']}|{item['sku']}"),
                    InlineKeyboardButton("📈 Forecast",   callback_data=f"forecast|{item['type']}|{item['sku']}"),
                ]])
                await update.message.reply_text(label, reply_markup=keyboard)

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        await update.message.reply_text("⚠️ Internal error.")


# ================= CALLBACK HANDLER (button taps) =================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()  # dismiss spinner

        parts = query.data.split("|", 2)
        if len(parts) != 3:
            await query.message.reply_text("⚠️ Invalid callback.")
            return

        action, item_type, sku = parts

        df_rm, df_grn, df_forecast, df_cons, df_fg = load_data()

        if action == "stock":
            reply = fmt_stock(sku, item_type, df_rm, df_fg)
        elif action == "grn":
            reply = fmt_grn(sku, df_grn)
        elif action == "cons":
            reply = fmt_consumption(sku, df_cons)
        elif action == "forecast":
            reply = fmt_forecast(sku, df_forecast)
        else:
            reply = "⚠️ Unknown action."

        for i in range(0, len(reply), MAX_MESSAGE_LENGTH):
            await query.message.reply_text(reply[i:i + MAX_MESSAGE_LENGTH])

    except Exception as e:
        print("CALLBACK ERROR:", e)
        traceback.print_exc()
        await update.callback_query.message.reply_text("⚠️ Internal error.")


# ================= START BOT =================
def main():
    print("🚀 ENTERPRISE BOT RUNNING...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
