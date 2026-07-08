import os
import logging
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
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"],
        ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"],
        [f"Maintenance: {status}"],
        ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update: Update, context):
    user = update.effective_user
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text("Welcome to IOS SHUBHAM License Store!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update: Update, context):
    global is_bot_active
    text = update.message.text
    user_id = update.effective_user.id
    
    # मेंटेनेंस चेक
    if not is_bot_active and user_id != ADMIN_ID: return

    # एडमिन मेंटेनेंस टॉगल
    if user_id == ADMIN_ID and text and text.startswith("Maintenance:"):
        is_bot_active = not is_bot_active
        await update.message.reply_text(f"✅ Maintenance: {'ON' if is_bot_active else 'OFF'}", reply_markup=admin_keyboard())
        return

    # कीज़ ऐड करने का फिक्स लॉजिक
    if context.user_data.get("state") == "add_keys":
        keys = [k.strip() for k in text.split("\n") if k.strip()]
        for k in keys: save_key(context.user_data["add_game"], k, context.user_data["add_plan"])
        await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard())
        context.user_data.clear()
        return

    # बटन्स और नेविगेशन
    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦" and user_id == ADMIN_ID:
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    elif text == "🔙 Back":
        await start(update, context)
    # [यहाँ आपके अन्य सभी पुराने कंडीशन्स वैसे ही रहेंगे]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    # सुनिश्चित करें कि CallbackQueryHandler यहाँ रजिस्टर है
    app.add_handler(CallbackQueryHandler(button_click)) 
    app.run_polling()

if __name__ == "__main__":
    main()