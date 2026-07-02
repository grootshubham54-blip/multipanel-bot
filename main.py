import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from database import create_tables, add_user, get_stock, get_total_users, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# गेम प्लान्स और कीमतें
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "120", "1 Week": "499", "1 Month": "999"},
    "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": {"1 Day": "150", "1 Week": "650", "1 Month": "1599"}
}

def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # गेम सिलेक्शन (बटन दिखाता है)
    if text in GAME_PLANS:
        keyboard = []
        for plan, price in GAME_PLANS[text].items():
            keyboard.append([InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"buy_{text}_{plan}")])
        await update.message.reply_text(f"🎮 {text} चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        await update.message.reply_text(f"🔑 Your Keys: \n{', '.join(keys) if keys else 'No keys found.'}")
    
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())

    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Panel:", reply_markup=admin_keyboard())

    elif text == "🔙 Back to Main":
        await update.message.reply_text("Welcome back!", reply_markup=get_main_keyboard(user.id))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        # यहाँ अपना QR कोड का फोटो लिंक बदलें
        qr_url = "https://i.imgur.com/YOUR_IMAGE_ID.jpg" 
        await query.message.reply_photo(photo=qr_url, caption="✅ स्क्रीनशॉट भेजें और सपोर्ट में बताएं।")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome!", reply_markup=get_main_keyboard(u.effective_user.id))))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    
    app.run_polling()

if __name__ == "__main__":
    main()
