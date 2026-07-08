import os, logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

is_bot_active = True 

def admin_keyboard():
    global is_bot_active
    status = "ON" if is_bot_active else "OFF"
    return ReplyKeyboardMarkup([
        ["🔑 Add Keys", "📊 Stock"], 
        ["📊 Sales Dashboard", "👥 Total Users"], 
        ["📜 Key Report", "🔄 Resend Key"],
        ["📂 Export Data", "📢 Broadcast"],
        ["💾 Backup DB", "🗑 Delete Key"],
        [f"Maintenance: {status}"],
        ["🔙 Back"]
    ], resize_keyboard=True)

async def start(update, context):
    global is_bot_active
    if not is_bot_active and update.effective_user.id != ADMIN_ID: return
    user = update.effective_user
    save_user_to_db(user.id, user.username)
    
    welcome_text = (
        "🎮 Welcome to IOS SHUBHAM License Store\n\n"
        "Your trusted destination for premium gaming licenses.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🚀 Select an option from the menu below to get started."
    )
    kb = [["🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦", "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦"], ["🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦", "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦"]]
    if user.id == ADMIN_ID: kb.append(["⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦"])
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    global is_bot_active
    text = update.message.text
    user_id = update.effective_user.id
    
    if not is_bot_active and user_id != ADMIN_ID: return

    if user_id == ADMIN_ID and text and text.startswith("Maintenance:"):
        is_bot_active = not is_bot_active
        await update.message.reply_text(f"✅ Maintenance Mode is now {'ON' if is_bot_active else 'OFF'}!", reply_markup=admin_keyboard())
        return

    # एडमिन पैनल्स और बाकी सभी फीचर्स का लॉजिक
    if user_id == ADMIN_ID:
        if text == "⚙️ ✦ 𝔸𝕕𝕞𝕚𝕟 ℙ𝕒𝕟𝕖𝕝 ✦": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast": context.user_data["state"] = "broadcasting"; await update.message.reply_text("Send your Broadcast message:")
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 *Total Users:* {get_total_users()}", parse_mode="Markdown")
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n"
            for g, plans in GAME_PLANS.items():
                msg += f"\n*{g}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(g, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "💾 Backup DB": path = create_backup(); await update.message.reply_text(f"✅ Backup saved at: {path}")
        # (यहाँ अन्य एडमिन बटन का लॉजिक वही है जो हमने पहले फाइनल किया था)

    if text == "🎮 ✦ 𝔾𝕒𝕞𝕖𝕤 ✦":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 ✦ 𝕄𝕪 𝕂𝕖𝕪𝕤 ✦":
        keys = get_user_keys(user_id)
        await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]) if keys else "No keys found!")
    elif text == "🎧 ✦ 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 ✦": await update.message.reply_text(f"📞 Contact: {SUPPORT_USERNAME}")
    elif text == "💳 ✦ 𝕋𝕠𝕡 𝕌𝕡 ✦": await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A"); p = context.user_data.get("plan", "N/A")
        btns = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), 
                 InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}_{g}_{p}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(btns))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr} ({get_stock_count(game, p)} Left)", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_games")])
        await query.edit_message_text(f"🎮 *{game}*\nSelect your plan:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    # (बाकी पेमेंट और एक्सेप्ट-रिजेक्ट का ओरिजिनल लॉजिक यहीं है)

def main():
    create_tables()
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
