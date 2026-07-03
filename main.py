import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "📜 Key Report"], 
        ["👥 Total Users", "📢 Broadcast"], 
        ["🗑 Delete Key", "💾 Backup DB"],
        ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user_id = update.effective_user.id
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # SECURITY: अनधिकृत एडमिन एक्सेस ब्लॉक
    admin_commands = ["🛠 Admin Panel", "📢 Broadcast", "🗑 Delete Key", "👥 Total Users", "📜 Key Report", "📊 Stock", "🔑 Add Keys", "📊 Sales Dashboard", "💾 Backup DB"]
    if text in admin_commands and user_id != ADMIN_ID:
        return

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "💾 Backup DB":
            path = create_backup()
            await update.message.reply_text(f"✅ Backup successful!\nFile saved at: {path}")
        elif text == "📢 Broadcast":
            context.user_data["state"] = "broadcast_msg"
            await update.message.reply_text("Enter message:", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
            return
        elif context.user_data.get("state") == "broadcast_msg":
            if text == "🔙 Back": context.user_data.clear(); await start(update, context); return
            context.user_data["broadcast_text"] = text
            context.user_data["state"] = "broadcast_photo"
            await update.message.reply_text("Now send the photo for broadcast:")
            return
        elif context.user_data.get("state") == "broadcast_photo" and update.message.photo:
            photo_id = update.message.photo[-1].file_id
            text_msg = context.user_data.get("broadcast_text", "")
            users = get_all_user_ids()
            count = 0
            for uid in users:
                try: await context.bot.send_photo(uid, photo=photo_id, caption=text_msg); count += 1
                except: pass
            await update.message.reply_text(f"✅ Broadcast sent to {count} users!", reply_markup=admin_keyboard())
            context.user_data.clear(); return
        
        elif text == "🗑 Delete Key":
            context.user_data["state"] = "delete_key_id"
            await update.message.reply_text("Enter ID of key to delete:")
            return
        elif context.user_data.get("state") == "delete_key_id":
            try:
                delete_key_by_id(int(text))
                await update.message.reply_text("✅ Key deleted!", reply_markup=admin_keyboard())
            except: await update.message.reply_text("⚠️ Invalid ID!", reply_markup=admin_keyboard())
            context.user_data.clear(); return
            
        elif text == "📊 Sales Dashboard":
            sold = get_sold_keys_count()
            dashboard = (f"📊 *Sales Dashboard*\n\n"
                         f"👥 Total Users: {get_total_users()}\n"
                         f"🔑 Available: {get_total_available_keys()}\n"
                         f"✅ Sold Keys: {sold}\n"
                         f"💰 Total Revenue: ₹{sold * 200}")
            await update.message.reply_text(dashboard, parse_mode="Markdown")
            
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total users: {get_total_users()}")
        elif text == "📜 Key Report":
            report = "📜 *Report:*\n\n"
            for kid, g, p, k, used, uid in get_all_keys_report_with_id():
                status = "✅ Sold" if used == 1 else "🟢 Available"
                report += f"🆔 {kid} | 🎮 {g} | {p}\n🔑 `{k}` | {status}\n\n"
            await update.message.reply_text(report, parse_mode="Markdown")
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n\n"
            # (आपका बाकी का कोड सेम है)
            # ... बाकी का लॉजिक वैसा ही रखें जैसा पहले था ...
            await update.message.reply_text(msg, parse_mode="Markdown")
        # ... बाकी के पुराने फीचर्स वैसे ही रहने दें ...
        elif text == "🔙 Back":
            context.user_data.clear(); await start(update, context); return

    # (बाकी सारा पुराना यूजर लॉजिक यहाँ जोड़ दें)

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    # ... (बाकी का हैंडलर यहाँ जोड़ दें)
    app.run_polling()

if __name__ == "__main__":
    main()
