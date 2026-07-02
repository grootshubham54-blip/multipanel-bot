import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# इम्पोर्ट्स
from database import (
    create_tables, save_key, get_stock, DB_NAME
)
from admin_panel import admin_keyboard

# लॉगिंग और सेटिंग्स
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # 1. एडमिन 'Add Key' मोड
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("👑 Admin Control Panel", reply_markup=admin_keyboard())
            return
        
        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text
            await update.message.reply_text("🎯 अब प्लान चुनें:", reply_markup=ReplyKeyboardMarkup([["1 DAY", "1 WEEK", "1 MONTH"], ["🔙 Back to Admin"]], resize_keyboard=True))
            return
        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text
            await update.message.reply_text("🔑 अब License Key भेजें:", reply_markup=ReplyKeyboardMarkup([["🔙 Back to Admin"]], resize_keyboard=True))
            return
        else:
            save_key(context.user_data["selected_game"], text, context.user_data["selected_plan"])
            context.user_data.pop("selected_game", None)
            context.user_data.pop("selected_plan", None)
            await update.message.reply_text(f"✅ Key saved!\nSend next key or 'Back to Admin'.", reply_markup=ReplyKeyboardMarkup([["🔙 Back to Admin"]], resize_keyboard=True))
            return

    # 2. गेम स्टॉक चेकर्स
    elif text == "👑 KING iOS":
        stock = get_stock("👑 KING iOS")
        await update.message.reply_text(f"👑 KING iOS\nAvailable Keys: {stock}")
    elif text == "WINIOS":
        stock = get_stock("WINIOS")
        await update.message.reply_text(f"WINIOS\nAvailable Keys: {stock}")
    elif text == "NEXT IOS":
        stock = get_stock("NEXT IOS")
        await update.message.reply_text(f"NEXT IOS\nAvailable Keys: {stock}")

    # 3. फीचर्स
    elif text == "ESING CERTIFICATE":
        await update.message.reply_text("📜 ESING Certificate Service\n\nयहाँ से आप अपना सर्टिफिकेट प्राप्त कर सकते हैं।")
    
    elif text == "👤 Profile":
        await update.message.reply_text(
            f"👤 <b>User Profile</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"👤 <b>Username:</b> @{user.username if user.username else 'None'}\n\n"
            f"📢 <b>Support:</b> @IOS_HACK_S", 
            parse_mode="HTML"
        )
        
    elif text == "💳 Payment":
        await update.message.reply_text(
            "💳 <b>Payment Section</b>\n\n"
            "प्रीमियम प्लांस खरीदने के लिए सपोर्ट से संपर्क करें।\n\n"
            "👑 <b>Support:</b> @IOS_HACK_S",
            parse_mode="HTML"
        )

    # 4. गलत इनपुट
    else:
        await update.message.reply_text("❌ Please use the menu buttons.")

if __name__ == "__main__":
    create_tables()  # डेटाबेस टेबल बनाना
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()
