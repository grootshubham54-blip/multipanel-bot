import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# गेम के नाम और प्लान
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    await update.message.reply_text("👋 वेलकम! गेम चुनें:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎮 Games":
        await update.message.reply_text("गेम चुनें:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        # बटन (Inline) प्लान दिखाएंगे
        keyboard = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"qr_{price}")] for plan, price in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 {text} का प्लान चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("qr_"):
        # यहाँ QR का पक्का लिंक है, यह कभी फेल नहीं होगा
        qr_url = "https://telegra.ph/file/0c32608447814c81a54a0.jpg"
        await query.message.reply_photo(
            photo=qr_url,
            caption="✅ यह रहा QR कोड। पेमेंट करके स्क्रीनशॉट भेजें।"
        )

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
