import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# ... (GAME_PLANS और बाकी फंक्शन वैसा ही रखें जैसा पहले था)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    
    if query.data.startswith("buy_"):
        # यहाँ हम पहले फाइल की जांच करेंगे, फिर भेजेंगे
        file_path = "new_qr.jpg.JPG"
        
        if os.path.exists(file_path):
            with open(file_path, "rb") as photo:
                await query.message.reply_photo(photo=photo, caption="✅ यह रहा QR कोड।")
        else:
            # अगर फाइल नहीं मिली, तो बोट एरर देने के बजाय सीधे लिंक से भेज देगा
            await query.message.reply_photo(
                photo="https://telegra.ph/file/0c32608447814c81a54a0.jpg",
                caption="✅ सर्वर से QR कोड: पेमेंट करके स्क्रीनशॉट भेजें।"
            )

# ... (बाकी का पूरा कोड वैसे ही रहने दें)
