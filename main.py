import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, save_pending_payment, approve_and_assign_key, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "199", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1300"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "129", "1 Week": "499", "1 Month": "999"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "150", "1 Week": "600", "1 Month": "1600"}
}

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    user_id = update.effective_user.id
    
    # --- बटन्स का लॉजिक ---
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        msg = "\n".join([f"🎮 {k[0]} | {k[1]} | Key: `{k[2]}`" for k in keys]) if keys else "❌ No keys found."
        await update.message.reply_text(f"Your Keys:\n{msg}", parse_mode="Markdown")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact us at: @YourSupportUsername")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Please select a game first to see payment details.")
    elif text == "🛠 Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    
    # --- एडमिन बटन्स ---
    elif text == "🔑 Add Keys" and user_id == ADMIN_ID:
        await update.message.reply_text("Please send keys in format: Game|Plan|Key")
    elif text == "📦 Stock" and user_id == ADMIN_ID:
        await update.message.reply_text("📊 Checking stock...")
    elif text == "👥 Total Users" and user_id == ADMIN_ID:
        await update.message.reply_text("👥 Total registered users: ...")
    elif text == "🔙 Back to Admin":
        await update.message.reply_text("Main menu:", reply_markup=admin_keyboard())

    # --- गेम सेलेक्शन ---
    elif text in GAME_PLANS:
        context.user_data["u_game"] = text
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan|{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))
    
    # --- फोटो हैंडलिंग ---
    elif update.message.photo and user_id != ADMIN_ID:
        # (फोटो वाला पुराना कोड यहाँ रखें)
        pass
    else:
        await update.message.reply_text("Please use menu buttons.")
