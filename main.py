import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "📜 Key Report"], 
        ["📂 Export Data", "🔄 Resend Key"],
        ["📢 Broadcast", "💾 Backup DB"],
        ["🗑 Delete Key", "🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user_id = update.effective_user.id
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # --- ADMIN SECURITY ---
    admin_cmds = ["🛠 Admin Panel", "📢 Broadcast", "🗑 Delete Key", "📊 Sales Dashboard", "📂 Export Data", "🔄 Resend Key", "💾 Backup DB", "📊 Stock", "🔑 Add Keys", "📜 Key Report"]
    if text in admin_cmds and user_id != ADMIN_ID: return

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "💾 Backup DB":
            path = create_backup()
            await update.message.reply_text(f"✅ Backup saved at: {path}")
        elif text == "📂 Export Data":
            data = get_all_keys_export()
            with open("keys.csv", "w") as f:
                f.write("ID,Game,Plan,Key,Used,UserID\n")
                for r in data: f.write(f"{','.join(map(str, r))}\n")
            await update.message.reply_document(document=open("keys.csv", "rb"))
        elif text == "🔄 Resend Key":
            context.user_data["state"] = "resend_uid"
            await update.message.reply_text("Enter Customer User ID:")
        elif context.user_data.get("state") == "resend_uid":
            try:
                uid = int(text)
                context.user_data["target_uid"] = uid
                keys = get_key_by_user_id(uid)
                if keys:
                    msg = "\n".join([f"🎮 {g} ({p}): `{k}`" for g, p, k in keys])
                    context.user_data["resend_msg"] = msg
                    context.user_data["state"] = "confirm_resend"
                    await update.message.reply_text(f"Found:\n{msg}\n\nSend this to user?", reply_markup=ReplyKeyboardMarkup([["✅ Confirm Resend", "🔙 Back"]], resize_keyboard=True))
                else: await update.message.reply_text("⚠️ No keys found."); context.user_data.clear()
            except: await update.message.reply_text("⚠️ Invalid ID."); context.user_data.clear()
        elif context.user_data.get("state") == "confirm_resend" and text == "✅ Confirm Resend":
            uid = context.user_data.get("target_uid")
            msg = context.user_data.get("resend_msg")
            await context.bot.send_message(uid, f"🔄 *Your key has been resent:*\n\n{msg}", parse_mode="Markdown")
            await update.message.reply_text("✅ Sent successfully!", reply_markup=admin_keyboard())
            context.user_data.clear()
        
        # --- (पुराने फीचर्स का लॉजिक यहाँ जारी रखें) ---
        elif text == "📊 Sales Dashboard":
            sold = get_sold_keys_count()
            await update.message.reply_text(f"📊 *Sales Dashboard*\n\n✅ Sold: {sold}\n💰 Revenue: ₹{sold * 200}", parse_mode="Markdown")
        elif text == "🔙 Back": context.user_data.clear(); await start(update, context); return

    # --- USER SECTION ---
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    # ... (बाकी सारा यूजर वाला पुराना कोड यहाँ लगा दें)

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
