import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, add_user, update_payment_status, save_key, get_stock, get_total_users, get_total_purchases, DB_NAME
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- FUNCTIONS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot\nSelect an option:", reply_markup=get_main_keyboard(user.id))

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
        await update.message.reply_text("✅ Announcement sent!", reply_markup=get_main_keyboard(user.id))
        return

    # 2. NAVIGATION
    if text in ["🔙 Back to Main", "❌ Cancel Payment"]:
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
    
    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
    
    elif text == "📢 Broadcast" and user.id == ADMIN_ID:
        context.user_data["broadcasting"] = True
        await update.message.reply_text("📢 Type your message for broadcast:", reply_markup=get_back_keyboard("Admin"))

    # 3. GAMES MENU
    elif text == "🎮 Games":
        await update.message.reply_text("🎮 Select Game:", reply_markup=ReplyKeyboardMarkup([
            ["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"], ["🔙 Back to Main"]
        ], resize_keyboard=True))

    # 4. KING iOS PLANS
    elif text == "👑 KING iOS":
        await update.message.reply_text("👑 KING iOS Plans:", reply_markup=ReplyKeyboardMarkup([
            ["👑 KING iOS 1 DAY - ₹200"], ["👑 KING iOS 1 WEEK - ₹800"], ["👑 KING iOS 1 MONTH - ₹2000"], ["🔙 Back to Games"]
        ], resize_keyboard=True))
    
    elif "KING iOS" in text and "₹" in text:
        context.user_data["base_game"] = "👑 KING iOS"
        context.user_data["plan"] = text.split(" - ")[0]
        context.user_data["amount"] = text.split("₹")[1]
        context.user_data["awaiting_screenshot"] = True
        await update.message.reply_text(f"Please pay ₹{context.user_data['amount']} and send screenshot.")

    # 5. WINIOS PLANS
    elif text == "WINIOS":
        await update.message.reply_text("WINIOS Plans:", reply_markup=ReplyKeyboardMarkup([
            ["WINIOS 1 DAY - ₹199"], ["WINIOS 1 WEEK - ₹599"], ["WINIOS 1 MONTH - ₹1399"], ["🔙 Back to Games"]
        ], resize_keyboard=True))
    
    elif "WINIOS" in text and "₹" in text:
        context.user_data["base_game"] = "WINIOS"
        context.user_data["plan"] = text.split(" - ")[0]
        context.user_data["amount"] = text.split("₹")[1]
        context.user_data["awaiting_screenshot"] = True
        await update.message.reply_text(f"Please pay ₹{context.user_data['amount']} and send screenshot.")

    # (इसी तरह बाकी सभी गेम्स का लॉजिक यहाँ जोड़ें...)
    
    else:
        await update.message.reply_text("Please select a valid option from the menu.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
