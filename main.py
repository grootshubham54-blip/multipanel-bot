import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from database import create_tables, add_user, save_key, get_stock, DB_NAME
from admin_panel import admin_keyboard, admin_game_selection_keyboard

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. BROADCAST LOGIC
    if context.user_data.get("broadcasting"):
        msg = text
        context.user_data["broadcasting"] = False
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()
        for u in users:
            try: await context.bot.send_message(chat_id=u[0], text=f"📢 *Announcement:*\n\n{msg}", parse_mode="Markdown")
            except: continue
        await update.message.reply_text("✅ Announcement sent!", reply_markup=admin_keyboard())
        return

    # 2. ADD KEY LOGIC (PLAN SELECTION)
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
            return
        
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text(f"🎮 {text} चुना गया.\nअब प्लान चुनें:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text(f"📋 {text} चुना गया.\nअब की (Key) भेजें:", reply_markup=get_back_keyboard("Admin"))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            await update.message.reply_text(f"✅ Key Added!\nGame: {context.user_data['selected_game']}\nPlan: {context.user_data['selected_plan']}\nKey: {text}", reply_markup=get_back_keyboard("Admin"))
            return

    # 3. NAVIGATION & BUTTONS
    if text == "🔙 Back to Main":
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
        return

    if text == "🎮 Games":
        await update.message.reply_text("🎮 Games:", reply_markup=ReplyKeyboardMarkup([
            ["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], 
            ["DOLPHIN IOS", "ESING CERTIFICATE"], ["🔙 Back to Main"]
        ], resize_keyboard=True))
        return

    if text == "ESING CERTIFICATE":
        await update.message.reply_text("📄 ESING CERTIFICATE details here.")
        return

    # 4. ADMIN PANEL ACTIONS
    if user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel":
            await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast":
            context.user_data["broadcasting"] = True
            await update.message.reply_text("📢 मैसेज टाइप करें:", reply_markup=get_back_keyboard("Admin"))
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("🎯 गेम चुनें:", reply_markup=admin_game_selection_keyboard())
        return

    # 5. OTHER EXISTING FEATURES
    # यहाँ आप अपने पुराने बाकी सारे elif कंडीशंस लगा सकते हैं
