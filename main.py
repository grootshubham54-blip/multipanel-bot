import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import (create_tables, add_user, update_payment_status, save_key, get_stock, get_total_users, get_total_purchases, DB_NAME)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# [आपकी बाकी की Mappings यहाँ रहने दें]

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

# [यहाँ अपने पुराने बाकी सभी functions (start, payment_info, photo_handler, admin_action) वैसे ही रहने दें]

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # --- ADD KEY LOGIC (PLAN SELECTION) ---
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        
        # 1. गेम चुनने के बाद प्लान पूछें
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("🎯 Select Plan:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True))
            return
        # 2. प्लान चुनने के बाद की (Key) मांगें
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text(f"🔑 गेम: {context.user_data['selected_game']} | प्लान: {text}\n\nअब की (Key) भेजें:", reply_markup=get_back_keyboard("Admin"))
            return
        # 3. की (Key) सेव करें
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text(f"✅ Key Added!\nGame: {context.user_data['selected_game']}\nPlan: {context.user_data['selected_plan']}", reply_markup=get_back_keyboard("Admin"))
            context.user_data.pop("selected_game", None); context.user_data.pop("selected_plan", None)
            return

    # --- YOUR EXISTING LOGIC ---
    # [अपना पुराना सारा कोड (Navigation, Games, Plans, आदि) इसके नीचे यहाँ पेस्ट करें]

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    # [बाकी handlers वैसे ही रहने दें]
    app.run_polling()

if __name__ == "__main__":
    main()
