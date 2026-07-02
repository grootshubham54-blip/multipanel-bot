import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, approve_and_assign_key
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"
SUPPORT_LINK = "@YOUR_USERNAME" # अपना यूजरनेम यहाँ डालें

# (बाकी GAME_PLANS और start फंक्शन पहले जैसा ही रहेगा)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # अगर यूजर फोटो (स्क्रीनशॉट) भेजता है
    if update.message.photo:
        if str(update.effective_user.id) != ADMIN_ID:
            # फोटो एडमिन को भेजें
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                caption=f"👤 यूजर: {update.effective_user.id}\nपेमेंट का स्क्रीनशॉट आया है।",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Accept", callback_data=f"acc_{update.effective_user.id}")],
                    [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{update.effective_user.id}")]
                ])
            )
            await update.message.reply_text("✅ स्क्रीनशॉट मिल गया! एडमिन चेक कर रहे हैं।")
        return

    # बाकी आपका पुराना कोड (गेम्स, सपोर्ट आदि) यहीं रहेगा...
    text = update.message.text
    # ... बाकी लॉजिक ...

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith("acc_"):
        user_id = data.split("_")[1]
        # यहाँ हम की (Key) असाइन करेंगे (इसे अपनी लॉजिक के हिसाब से एडजस्ट करें)
        await context.bot.send_message(user_id, "✅ पेमेंट अप्रूव हो गया! आपकी की ये रही: [KEY_CODE]")
        await query.edit_message_caption("✅ पेमेंट स्वीकार कर लिया गया है।")
        
    elif data.startswith("rej_"):
        user_id = data.split("_")[1]
        await context.bot.send_message(user_id, f"❌ पेमेंट रिजेक्ट हुआ। कृपया सहायता के लिए यहाँ संपर्क करें: {SUPPORT_LINK}")
        await query.edit_message_caption("❌ पेमेंट रिजेक्ट कर दिया गया है।")

# main() फंक्शन में handlers वैसे ही रहेंगे
