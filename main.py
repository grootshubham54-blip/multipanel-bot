import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import create_tables, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# गेम के नाम और उनके प्लान
GAME_PLANS = {
    "👑 KING iOS": ["1 Day - ₹200", "1 Week - ₹800", "1 Month - ₹2000"],
    "WINIOS": ["1 Day - ₹199", "1 Week - ₹600", "1 Month - ₹1299"]
}

def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        # अब बटन नीचे मेनू की तरह आएंगे, लोडिंग का कोई लफड़ा ही नहीं होगा
        keyboard = [[KeyboardButton(plan)] for plan in GAME_PLANS[text]]
        keyboard.append([KeyboardButton("🔙 Back to Main")])
        await update.message.reply_text(f"🎮 {text} प्लान चुनें:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    elif "₹" in text:
        # यह QR कोड सीधा टेलीग्राम लिंक से आएगा, बोट क्रैश नहीं होगा
        await update.message.reply_photo(
            photo="https://telegra.ph/file/0c32608447814c81a54a0.jpg",
            caption="✅ यह रहा QR कोड। पेमेंट करके स्क्रीनशॉट भेजें।"
        )
    elif text == "🔙 Back to Main":
        await update.message.reply_text("मेनू:", reply_markup=get_main_keyboard(user.id))
    else:
        await update.message.reply_text("मेनू:", reply_markup=get_main_keyboard(user.id))

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await context.bot.send_photo(ADMIN_ID, photo=update.message.photo[-1].file_id, caption=f"👤 User: {update.effective_user.username}\nपेमेंट चेक करें:")
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है।")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome!", reply_markup=get_main_keyboard(u.effective_user.id))))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment))
    app.run_polling()

if __name__ == "__main__":
    main()
