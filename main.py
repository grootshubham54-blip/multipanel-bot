import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

is_bot_active = True 

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    global is_bot_active
    status = "ON" if is_bot_active else "OFF"
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"], ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"], [f"Maintenance: {status}"], ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    # यूजर डेटाबेस में ऐड करें
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit(); conn.close()
    
    welcome_text = ("🎮 Welcome to IOS SHUBHAM License Store\n\n"
                    "🚀 Select an option from the menu below to get started.")
    
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    global is_bot_active
    text = update.message.text
    user_id = update.effective_user.id
    
    if not is_bot_active and user_id != ADMIN_ID: return
    if text == "🔙 Back": context.user_data.clear(); await start(update, context); return

    if user_id == ADMIN_ID:
        if text and text.startswith("Maintenance:"):
            is_bot_active = not is_bot_active
            await update.message.reply_text(f"✅ Status: {'ON' if is_bot_active else 'OFF'}", reply_markup=admin_keyboard())
        elif text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total Users: {get_total_users()}")
        elif text == "📊 Stock":
            msg = "📊 Current Stock:\n"
            for g, plans in GAME_PLANS.items():
                for p in plans: msg += f"{g} ({p}): {get_stock_count(g, p)}\n"
            await update.message.reply_text(msg)
        # कीज़ ऐड करने का लॉजिक (जैसा था)
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()], resize_keyboard=True))
        elif context.user_data.get("state") == "select_game":
            context.user_data["add_game"] = text; context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys (one per line):")
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"): save_key(context.user_data["add_game"], k.strip(), "1 Day")
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard()); context.user_data.clear()

    # पेमेंट फोटो हैंडलिंग
    if update.message.photo and user_id != ADMIN_ID:
        btns = [[InlineKeyboardButton("✅ Verify Payment", callback_data=f"acc_{user_id}"), 
                 InlineKeyboardButton("❌ Cancel Order", callback_data=f"rej_{user_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}", reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    data = query.data
    if data.startswith("acc_"):
        uid = int(data.split("_")[1])
        await context.bot.send_message(uid, "✅ Payment Verified! Your key is ready.")
        await query.edit_message_caption(caption="✅ Verified.")
    elif data.startswith("rej_"):
        uid = int(data.split("_")[1])
        await context.bot.send_message(uid, "❌ Payment Rejected.")
        await query.edit_message_caption(caption="❌ Cancelled.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
