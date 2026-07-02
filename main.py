import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# इम्पोर्ट्स सुनिश्चित करें
from database import create_tables, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# मेन कीबोर्ड फंक्शन
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# एडमिन और अन्य फीचर्स के लिए हैंडलर
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    
    if text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Control:", reply_markup=admin_keyboard())
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact: @Support")
    elif text == "👤 Profile":
        await update.message.reply_text(f"👤 User: {user.username}\nID: {user.id}")
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
    elif text == "💳 Payment":
        await update.message.reply_text("Please select a game to pay.")
    elif text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        await update.message.reply_text(f"🔑 Your Keys: {', '.join(keys) if keys else 'No keys yet.'}")

# पेमेंट स्क्रीनशॉट हैंडलर (एडमिन के लिए)
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        user = update.effective_user
        keyboard = [[InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user.id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]]
        await context.bot.send_photo(ADMIN_ID, photo=update.message.photo[-1].file_id, caption=f"👤 User: {user.username}\nपेमेंट कन्फर्म करें:", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है।")

# बटन क्लिक हैंडलर (QR के लिए)
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        # QR FILE ID का उपयोग करें (इसे अपनी ID से बदलें)
        qr_id = "YOUR_FILE_ID_HERE" 
        await query.message.reply_photo(photo=qr_id, caption="✅ इस QR पर पेमेंट करें।")
    elif query.data.startswith("accept_") or query.data.startswith("reject_"):
        user_id = query.data.split("_")[1]
        action = "एक्सेप्ट" if "accept" in query.data else "रिजेक्ट"
        await context.bot.send_message(user_id, f"✅ आपकी पेमेंट {action} कर दी गई है।")
        await query.edit_message_caption(caption=f"✅ पेमेंट {action} हो गई।")

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
