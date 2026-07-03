import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

# (आपका पुराना LOGGING, TOKEN, GAME_PLANS कोड वैसा ही रहेगा)
# ... [GAME_PLANS, TOKEN, आदि यहाँ रखें] ...

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "📜 Key Report"], 
        ["📂 Export Data", "🔄 Resend Key"],
        ["📢 Broadcast", "💾 Backup DB"],
        ["🗑 Delete Key", "🔙 Back"]
    ], resize_keyboard=True)

# message_handler के अंदर ये नया लॉजिक जोड़ें:
async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # --- Export Data ---
    if text == "📂 Export Data":
        keys_data = get_all_keys_export()
        with open("keys_export.csv", "w") as f:
            f.write("ID,Game,Plan,Key,Used,UserID\n")
            for row in keys_data: f.write(f"{','.join(map(str, row))}\n")
        await update.message.reply_document(document=open("keys_export.csv", "rb"))
    
    # --- Resend Key ---
    elif text == "🔄 Resend Key":
        context.user_data["state"] = "resend_uid"
        await update.message.reply_text("Enter the User ID of the customer:")
    elif context.user_data.get("state") == "resend_uid":
        try:
            uid = int(text)
            keys = get_key_by_user_id(uid)
            if keys:
                msg = "\n".join([f"🎮 {g} ({p}): `{k}`" for g, p, k in keys])
                await update.message.reply_text(f"✅ Found keys for {uid}:\n\n{msg}", parse_mode="Markdown")
            else: await update.message.reply_text("⚠️ No keys found for this user.")
        except: await update.message.reply_text("⚠️ Invalid User ID.")
        context.user_data.clear()

    # (बाकी आपका पुराना सारा कोड यहाँ नीचे ऐसे ही रखें)
