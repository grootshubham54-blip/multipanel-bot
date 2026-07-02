import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# अपने डेटाबेस और एडमिन पैनल को इम्पोर्ट करें
from database import create_tables, get_user_keys, get_stock, get_total_users
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# गेम और उनके प्लान्स
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "Mars Loader": {"1 Day": "120", "1 Week": "499", "1 Month": "999"},
    "DEADEYE": {"1 Day": "150", "1 Week": "650", "1 Month": "1599"}
}

# मेन कीबोर्ड
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # एडमिन पैनल और फीचर्स
    if text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Control:", reply_markup=admin_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        await update.message.reply_text(f"🔑 Keys: {', '.join(keys) if keys else 'No keys found.'}")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact: @YourSupportHandle")
    elif text == "👤 Profile":
        await update.message.reply_text(f"👤 User: {user.username}\nID: {user.id}")
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        keyboard = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"buy_{text}_{plan}")] for plan, price in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 {text} प्लान चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        user = update.effective_user
        keyboard = [[InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user.id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]]
        await context.bot.send_photo(ADMIN_ID, photo=update.message.photo[-1].file_id, caption=f"👤 User: {user.username}\nपेमेंट चेक करें:", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है।")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        # यहाँ अपनी File ID डालें (जो टेलीग्राम से ली है)
        qr_file_id = "AgACAgQAAxkBAA..." 
        await query.message.reply_photo(photo=qr_file_id, caption="✅ इस QR पर पेमेंट करें।")
    elif query.data.startswith("accept_") or query.data.startswith("reject_"):
        user_id = query.data.split("_")[1]
        status = "एक्सेप्ट" if "accept" in query.data else "रिजेक्ट"
        await context.bot.send_message(user_id, f"✅ आपकी पेमेंट {status} हो गई है।")
        await query.edit_message_caption(caption=f"✅ पेमेंट {status} कर दी गई।")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome!", reply_markup=get_main_keyboard(u.effective_user.id))))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
