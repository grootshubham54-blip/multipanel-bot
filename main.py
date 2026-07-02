import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# अपनी फाइल्स से इम्पोर्ट्स
from database import create_tables, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Config
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

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in GAME_PLANS:
        keyboard = [[InlineKeyboardButton(f"{plan} - ₹{price}", callback_data=f"buy_{text}_{plan}")] for plan, price in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 {text} प्लान चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
    elif text == "⚙️ Admin Panel" and update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Control:", reply_markup=admin_keyboard())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # यह Loading... हटाने के लिए जरूरी है
    
    if query.data.startswith("buy_"):
        # QR कोड: यहाँ आपको अपने फोटो की File ID डालनी है
        # फाइल ID पाने के लिए: फोटो को बॉट को भेजें और बॉट से उसकी ID कॉपी करें
        qr_file_id = "AgACAgQAAxkBAA..." # अपनी वाली File ID यहाँ डालें
        
        await query.message.reply_photo(
            photo=qr_file_id, 
            caption="✅ कृपया इस QR पर पेमेंट करें और स्क्रीनशॉट भेजें।"
        )
    elif query.data.startswith("accept_") or query.data.startswith("reject_"):
        user_id = query.data.split("_")[1]
        status = "एक्सेप्ट" if "accept" in query.data else "रिजेक्ट"
        await context.bot.send_message(user_id, f"✅ आपकी पेमेंट {status} कर दी गई है।")
        await query.edit_message_caption(caption=f"✅ {status} कर दिया गया।")

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        user = update.effective_user
        keyboard = [[InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user.id}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]]
        await context.bot.send_photo(ADMIN_ID, photo=update.message.photo[-1].file_id, caption=f"👤 User: @{user.username}\nपेमेंट चेक करें:", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है।")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome!", reply_markup=ReplyKeyboardMarkup([["🎮 Games", "🔑 My Keys"]], resize_keyboard=True))))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
