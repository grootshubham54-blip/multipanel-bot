import os, logging, uuid
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 

# मेंटेनेंस मोड के लिए वेरिएबल
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
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], ["📜 Key Report", "🔄 Resend Key"], ["📂 Export Data", "📢 Broadcast"], ["💾 Backup DB", "🗑 Delete Key"], [f"Maintenance: {status}"], ["🔙 Back"]], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text("🎮 Welcome to IOS SHUBHAM Store!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    global is_bot_active
    text = update.message.text
    user_id = update.effective_user.id
    
    # एडमिन कमांड्स और पुराने फीचर्स (जो आपने दिए थे)
    if user_id == ADMIN_ID and text.startswith("Maintenance:"):
        is_bot_active = not is_bot_active
        await update.message.reply_text(f"✅ Maintenance: {'ON' if is_bot_active else 'OFF'}", reply_markup=admin_keyboard())
        return

    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    
    # यहाँ आप अपने बाकी पुराने if-elif (Add keys, Stock आदि) पेस्ट करें
    elif text == "🔙 Back": await start(update, context)
    elif user_id == ADMIN_ID and text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    data = query.data
    
    if data.startswith("game_"):
        game = data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}_{game}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nSelect plan:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data.startswith("pay_"):
        parts = data.split("_"); plan, price, game = parts[1], parts[2], parts[3]
        await query.message.reply_photo(photo=open("qr.JPG", "rb"), caption=f"Pay ₹{price} for {game} ({plan}) & send screenshot.")
    
    # यहाँ अपना पुराना acc_ / rej_ वाला लॉजिक पेस्ट करें
    elif data.startswith(("acc_", "rej_")):
        # अपना कोड यहाँ डालें
        pass

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
