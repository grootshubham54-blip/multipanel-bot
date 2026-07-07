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
        ["🔑 Add Keys", "📊 Stock"], ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"], ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"], ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    user = update.effective_user
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username or "N/A"))
    conn.commit()
    conn.close()
    
    welcome_text = (
        "🎮 *Welcome to IOS SHUBHAM License Store*\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📦 *Available Products*\n• KINGIOS\n• WINIOS\n• NEXT IOS\n• Mars Loader\n• DEADEYE\n• DOLPHIN IOS\n\n"
        "⏳ *License Durations*\n• 1 Day License\n• 7 Days License\n• 30 Days License\n\n"
        "✨ *Why Choose Us?*\n✅ Instant QR Code Generation\n✅ Automatic Payment Verification\n✅ Instant License Delivery\n✅ Real-Time Order Tracking\n✅ Fast & Reliable Support\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🚀 Select an option from the menu below to get started.\n\n"
        "Thank you for choosing IOS SHUBHAM License Store."
    )
    
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    if context.user_data.get("state") == "broadcasting":
        users = get_all_users()
        for u in users:
            try: await context.bot.send_message(u, text)
            except: pass
        await update.message.reply_text("✅ Broadcast Sent!", reply_markup=admin_keyboard())
        context.user_data.clear()
        return

    if text == "🔙 Back":
        context.user_data.clear()
        await start(update, context)
        return

    # एडमिन लॉजिक
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast": context.user_data["state"] = "broadcasting"; await update.message.reply_text("Send message:")
        elif text == "🔑 Add Keys": context.user_data["state"] = "select_game"; await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif text == "📊 Stock":
            msg = "📊 *Stock:*\n"
            for g, plans in GAME_PLANS.items():
                msg += f"*{g}:*\n"
                for p in plans: msg += f" - {p}: {get_stock_count(g, p)}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "📊 Sales Dashboard": await update.message.reply_text(f"Sold: {get_sold_keys_count()}")
        elif text == "👥 Total Users": await update.message.reply_text(f"Users: {get_total_users()}")
        # बाकी एडमिन लॉजिक (Backup, Resend आदि आप अपने पुराने कोड से यहाँ जोड़ सकते हैं)

    # यूजर लॉजिक
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if not keys: await update.message.reply_text("No keys!")
        else: await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]))
    elif text == "📞 Support": await update.message.reply_text(f"Contact: {SUPPORT_USERNAME}")
    elif text == "💳 Payment": await update.message.reply_text(f"Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}", reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nSelect plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("pay_"):
        # यहाँ QR सेंड करने वाला लॉजिक
        await query.message.reply_text("Pay to QR and send screenshot.")
    elif query.data.startswith(("acc_", "rej_")):
        # यहाँ Accept/Reject लॉजिक
        pass

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
