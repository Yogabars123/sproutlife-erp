import pandas as pd
import time
import traceback
import requests
import io
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

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


# ================= TELEGRAM MESSAGE HANDLER =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        user_input = update.message.text.strip().lower()

        df_rm, df_grn, df_forecast, df_cons, df_fg = load_data()

        # ================= FG =================
        if user_input.startswith("fg-"):

            code = user_input.replace("fg-", "")

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

        # ================= RM =================
        if user_input.startswith("rm-"):

            code = user_input.replace("rm-", "")

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

        await update.message.reply_text("❌ Command not recognized.")

    except Exception as e:

        print("ERROR:", e)
        traceback.print_exc()

        await update.message.reply_text("⚠️ Internal error.")


# ================= START BOT =================
def main():

    print("🚀 ENTERPRISE BOT RUNNING...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # drop_pending_updates prevents old messages from crashing deployment
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
