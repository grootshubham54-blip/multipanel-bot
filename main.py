import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

# Logging setup
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

# Game & Price Data
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}
}
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(update.effective_user.id) == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    # 1. पेमेंट स्क्रीनशॉट हैंडलिंग
    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "Game")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 Game: {g}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot received! Admin is verifying.")
        return

    # 2. कस्टमर और एडमिन बटन्स
    if text == "🎮 Games": await update.message.reply_text("Choose game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        context.user_data["u_game"] = text
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{GAME_MAP[text]}_{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 Select plan for {text}:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(update.effective_user.id)
        msg = "🔑 Keys:\n" + "\n".join([f"{k[0]}: {k[2]}" for k in keys]) if keys else "❌ No keys."
        await update.message.reply_text(msg)
    elif text in ["🔙 Back to Main", "🔙 Back to Admin"]: await start(update, context)
    
    # 3. एडमिन पैनल लॉजिक
    elif user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys": 
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
        elif text == "📦 Stock": await update.message.reply_text("Checking stock...")
        elif context.user_data.get("state") == "awaiting_game" and text in GAME_PLANS:
            context.user_data.update({"add_game": text, "state": "awaiting_plan"})
            await update.message.reply_text("Choose plan:", reply_markup=admin_plan_selection_keyboard())
    else: await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("pay_"): await query.message.reply_text("Send screenshot now.")
    elif query.data.startswith("acc_"):
        uid = query.data.split("_")[1]
        await context.bot.send_message(uid, "✅ Approved!")
        await query.edit_message_caption(caption="✅ Approved.")
    elif query.data.startswith("rej_"):
        await context.bot.send_message(query.data.split("_")[1], "❌ Rejected.")
        await query.edit_message_caption(caption="❌ Rejected.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
