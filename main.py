import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from database import (create_tables, add_user, update_payment_status, save_key, get_stock, get_total_users, get_total_purchases, DB_NAME)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Mappings
GAME_MAPPING = {"👑 KING iOS": "king", "WINIOS": "win", "NEXT IOS": "next", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead", "DOLPHIN IOS": "dolphin"}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

# --- KEYBOARDS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. BROADCAST
    if context.user_data.get("broadcasting"):
        msg = text
        context.user_data["broadcasting"] = False
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        for u in cursor.fetchall():
            try: await context.bot.send_message(chat_id=u[0], text=f"📢 *Announcement:*\n\n{msg}", parse_mode="Markdown")
            except: continue
        conn.close()
        await update.message.reply_text("✅ Announcement Sent!", reply_markup=admin_keyboard())
        return

    # 2. ADD KEY LOGIC (With Plan)
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
            return
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("🎯 Select Plan:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text("🔑 Send the Key:", reply_markup=get_back_keyboard("Admin"))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text("✅ Key Added Successfully!", reply_markup=get_back_keyboard("Admin"))
            context.user_data.pop("selected_game", None); context.user_data.pop("selected_plan", None)
            return

    # 3. BUTTON NAVIGATION
    if text == "🎮 Games":
        await update.message.reply_text("🎮 Games:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["DOLPHIN IOS", "ESING CERTIFICATE"], ["🔙 Back to Main"]], resize_keyboard=True))
    elif text == "ESING CERTIFICATE":
        await update.message.reply_text("📄 ESING CERTIFICATE feature is here.")
    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
    elif text == "📢 Broadcast" and user.id == ADMIN_ID:
        context.user_data["broadcasting"] = True
        await update.message.reply_text("📢 Send your announcement:")
    elif text == "🔑 Add Keys" and user.id == ADMIN_ID:
        context.user_data["adding_key"] = True
        await update.message.reply_text("🎯 Select Game:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔙 Back to Main":
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
    
    # (यहाँ अपने पुराने बाकी सारे elif plans वैसे ही पेस्ट कर दें)

# --- MAIN ---
if __name__ == "__main__":
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    # ये सबसे महत्वपूर्ण लाइन है, इसके बिना कुछ काम नहीं करेगा
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot is running...")
    app.run_polling()
