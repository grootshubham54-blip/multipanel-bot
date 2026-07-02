import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# अपनी फाइल्स से इम्पोर्ट्स
from database import (
    create_tables, add_user, get_stock, get_total_users, get_user_keys
)
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# गेम्स और कीमतें
GAME_PRICES = {
    "👑 KING iOS": "1 Day: ₹200 | 1 Week: ₹800 | 1 Month: ₹2000",
    "WINIOS": "1 Day: ₹199 | 1 Week: ₹600 | 1 Month: ₹1299",
    "NEXT IOS": "1 Day: ₹200 | 1 Week: ₹800",
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "1 Day: ₹120 | 1 Week: ₹499 | 1 Month: ₹999",
    "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "1 Day: ₹150 | 1 Week: ₹650 | 1 Month: ₹1599",
    "DOLPHIN IOS": "Contact Support for Pricing"
}

def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # --- MAIN NAVIGATION ---
    if text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        await update.message.reply_text(f"🔑 *Your Keys:*\n" + ("\n".join([f"`{k}`" for k in keys]) if keys else "No keys found."), parse_mode="Markdown")
    
    elif text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())

    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())

    # --- GAME SELECTION & PRICES ---
    elif text in GAME_PRICES:
        await update.message.reply_text(f"🎮 *{text}*\n\n{GAME_PRICES[text]}\n\n✅ पेमेंट का स्क्रीनशॉट भेजें।", parse_mode="Markdown")

    # --- ADMIN ACTIONS ---
    elif text == "📦 Stock" and user.id == ADMIN_ID:
        await update.message.reply_text(f"📦 Total Stock: {get_stock()}", reply_markup=admin_game_selection_keyboard())

    elif text == "👥 Total Users" and user.id == ADMIN_ID:
        await update.message.reply_text(f"👥 Total Users: {get_total_users()}")

    # --- BACK BUTTONS ---
    elif text == "🔙 Back to Main":
        await update.message.reply_text("Welcome back!", reply_markup=get_main_keyboard(user.id))
    
    elif text == "🔙 Back to Admin":
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN missing!")
        return
        
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome!", reply_markup=get_main_keyboard(u.effective_user.id))))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
