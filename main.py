import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593  # Integer format

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# ... (GAME_MAP और बाकी सब वैसे ही रहेगा)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id # Integer comparison
    state = context.user_data.get("state")

    # फोटो और बाकी लॉजिक...
    if text == "🔙 Back to Admin":
        context.user_data.clear()
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        return

    # एडमिन State Validation
    if user_id == ADMIN_ID:
        if state == "awaiting_game" and text not in GAME_PLANS and text != "🔙 Back to Admin":
            await update.message.reply_text("❌ Invalid selection. Choose from keyboard.")
            return
        # ... बाकी एडमिन लॉजिक ...

# बाकी के फंक्शन्स आप पिछले वर्जन के ही रखें, यह स्ट्रक्चर अब "Loop-Proof" है।
