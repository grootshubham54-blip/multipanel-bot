import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from database import create_tables, save_key, get_stock, DB_NAME
from admin_panel import admin_keyboard 

# Logging Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# कीबोर्ड लेआउट (इसे यहाँ रखना जरूरी है ताकि बोट क्रैश न हो)
def main_keyboard():
    return ReplyKeyboardMarkup([
        ["👑 KING iOS", "WINIOS", "NEXT IOS"],
        ["ESING CERTIFICATE", "👤 Profile", "💳 Payment"]
    ], resize_keyboard=True)

# /start कमांड - यह सबसे जरूरी है
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 स्वागत है! नीचे दिए गए बटन्स का उपयोग करें:", reply_markup=main_keyboard())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. एडमिन मोड (Add Keys)
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
            return
        
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("🎯 अब प्लान चुनें (1 DAY, 1 WEEK, 1 MONTH):", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text("🔑 अब License Key भेजें:", reply_markup=ReplyKeyboardMarkup([["🔙 Back to Admin"]], resize_keyboard=True))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            context.user_data.pop("selected_game", None)
            context.user_data.pop("selected_plan", None)
            await update.message.reply_text("✅ Key saved! अगली की भेजें:", reply_markup=ReplyKeyboardMarkup([["🔙 Back to Admin"]], resize_keyboard=True))
            return

    # 2. मेनू बटन्स
    elif text == "👑 KING iOS":
        await update.message.reply_text(f"👑 KING iOS\nAvailable Keys: {get_stock('KING iOS')}")
    elif text == "WINIOS":
        await update.message.reply_text(f"WINIOS\nAvailable Keys: {get_stock('WINIOS')}")
    elif text == "NEXT IOS":
        await update.message.reply_text(f"NEXT IOS\nAvailable Keys: {get_stock('NEXT IOS')}")
    elif text == "ESING CERTIFICATE":
        await update.message.reply_text("📜 ESING Certificate: संपर्क करें @IOS_HACK_S")
    elif text == "👤 Profile":
        await update.message.reply_text(f"👤 ID: <code>{user.id}</code>\nUser: @{user.username}", parse_mode="HTML")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Payment के लिए @IOS_HACK_S पर मैसेज करें।")
    
    # अगर एडमिन एडमिन पैनल का बटन दबाए
    elif text == "⚙️ Admin Panel" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
    
    else:
        await update.message.reply_text("❌ कृपया सही बटन का उपयोग करें।", reply_markup=main_keyboard())

if __name__ == "__main__":
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
