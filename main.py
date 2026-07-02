import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# इम्पोर्ट्स (सुनिश्चित करें कि database.py में get_user_keys मौजूद है)
from database import create_tables, add_user, get_stock, get_total_users, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "120", "1 Week": "499", "1 Month": "999"},
    "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": {"1 Day": "150", "1 Week": "650", "1 Month": "1599"}
}

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # गेम सिलेक्शन (Inline Buttons)
    if text in GAME_PLANS:
        keyboard = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"buy_{text}_{plan}")] for plan, price in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 {text} के लिए प्लान चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # अन्य मेनू
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Panel:", reply_markup=admin_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        await update.message.reply_text(f"🔑 Keys: {', '.join(keys) if keys else 'No keys found.'}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # यह बहुत जरूरी है, वरना बटन घूमता रहेगा
    
    if query.data and query.data.startswith("buy_"):
        # QR कोड का लिंक
        qr_url = "https://telegra.ph/file/a4d3b84f33d1c4e95155f.jpg"
        await query.message.reply_photo(photo=qr_url, caption="✅ इस QR पर पेमेंट करें और स्क्रीनशॉट भेजें।")
    
    elif query.data.startswith("accept_") or query.data.startswith("reject_"):
        # एडमिन एक्शन
        action = "एक्सेप्ट" if "accept" in query.data else "रिजेक्ट"
        user_id = query.data.split("_")[1]
        await context.bot.send_message(user_id, f"✅ आपकी पेमेंट {action} कर दी गई है।")
        await query.edit_message_caption(caption=f"✅ पेमेंट {action} कर दी गई।")

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        user = update.effective_user
        keyboard = [[InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user.id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]]
        await context.bot.send_photo(ADMIN_ID, photo=photo_id, caption=f"👤 User: {user.username}\nपेमेंट चेक करें:", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है।")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome!", reply_markup=ReplyKeyboardMarkup([["🎮 Games", "🔑 My Keys"]], resize_keyboard=True))))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment))
    app.add_handler(CallbackQueryHandler(button_click)) # यह यहाँ होना जरूरी है
    app.run_polling()

if __name__ == "__main__":
    main()
