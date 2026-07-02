import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import create_tables, add_user, save_key, get_stock, DB_NAME
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

def get_main_keyboard(user_id):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def get_back_keyboard(target):
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

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
            try: await context.bot.send_message(chat_id=u[0], text=f"📢 {msg}")
            except: pass
        conn.close()
        await update.message.reply_text("✅ Sent!", reply_markup=admin_keyboard())
        return

    # 2. ADD KEY LOGIC
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("Admin Panel", reply_markup=admin_keyboard())
            return
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("प्लान चुनें:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text("अब की (Key) भेजें:", reply_markup=get_back_keyboard("Admin"))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text("✅ Key Added!", reply_markup=get_back_keyboard("Admin"))
            return

    # 3. BUTTONS ROUTING
    if text == "🎮 Games":
        await update.message.reply_text("Select:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["DOLPHIN IOS", "ESING CERTIFICATE"], ["🔙 Back to Main"]], resize_keyboard=True))
    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("Admin:", reply_markup=admin_keyboard())
    elif text == "📢 Broadcast" and user.id == ADMIN_ID:
        context.user_data["broadcasting"] = True
        await update.message.reply_text("मैसेज भेजें:")
    elif text == "🔑 Add Keys" and user.id == ADMIN_ID:
        context.user_data["adding_key"] = True
        await update.message.reply_text("गेम चुनें:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔙 Back to Main":
        context.user_data.clear()
        await update.message.reply_text("Main Menu", reply_markup=get_main_keyboard(user.id))
    elif text == "ESING CERTIFICATE":
        await update.message.reply_text("ESING CERTIFICATE Section")

# 4. MAIN RUNNER (ये सबसे जरूरी है)
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()
