import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

# Game & Plan Mappings
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(update.effective_user.id) == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome! How can I help you today?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    # 1. Payment Screenshot Handling
    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "👑 KING iOS")
        p = context.user_data.get("u_plan", "1 Day")
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 Game: {g}\n📦 Plan: {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept & Send Key", callback_data=f"acc_{user_id}_{GAME_MAP[g]}_{PLAN_MAP[p]}")], [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot received! Admin is verifying.")
        return

    # 2. Customer Menu Buttons
    if text == "🎮 Games":
        await update.message.reply_text("Choose a game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_MAP:
        context.user_data["u_game"] = text
        keyboard = [[InlineKeyboardButton(f"{p}", callback_data=f"pay_{GAME_MAP[text]}_{PLAN_MAP[p]}")] for p in ["1 Day", "1 Week", "1 Month"]]
        await update.message.reply_text(f"🎮 Select plan for {text}:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == "🔑 My Keys":
        keys = get_user_keys(update.effective_user.id)
        msg = "🔑 **Your Keys:**\n" + "\n".join([f"🎮 {gk} ({pk}): `{kcode}`" for gk, pk, kcode in keys]) if keys else "❌ No keys found."
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == "📞 Support":
        await update.message.reply_text("📞 Contact admin: @IOS_HACK_S")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 Go to '🎮 Games' to select a plan and make payment.")
    
    # 3. Admin Panel Logic
    elif user_id == ADMIN_ID:
        state = context.user_data.get("state")
        if text == "🛠 Admin Panel":
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("Choose game:", reply_markup=admin_game_selection_keyboard())
        elif state == "awaiting_game" and text in GAME_MAP:
            context.user_data.update({"add_game": text, "state": "awaiting_plan"})
            await update.message.reply_text("Choose plan:", reply_markup=admin_plan_selection_keyboard())
        elif state == "awaiting_plan":
            context.user_data.update({"add_plan": text.replace("🟢 ", ""), "state": "awaiting_keys"})
            await update.message.reply_text("Send keys (one per line):")
        elif state == "awaiting_keys":
            for k in text.split("\n"): save_key(context.user_data['add_game'], k.strip(), context.user_data['add_plan'])
            context.user_data.clear()
            await update.message.reply_text("✅ Saved!")
    else:
        await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("pay_"):
        _, g_short, p_short = data.split("_")
        context.user_data.update({"u_game": REV_GAME_MAP[g_short], "u_plan": REV_PLAN_MAP[p_short]})
        with open("qr.JPG", "rb") as qr:
            await query.message.reply_photo(qr, caption=f"Pay to QR and send screenshot.")
    elif data.startswith("acc_"):
        _, uid, g_short, p_short = data.split("_")
        key = approve_and_assign_key(int(uid), REV_GAME_MAP[g_short], REV_PLAN_MAP[p_short])
        await context.bot.send_message(int(uid), f"✅ Approved! Key: {key}") if key else None
        await query.edit_message_caption(caption="✅ Approved.")
    elif data.startswith("rej_"):
        await context.bot.send_message(int(data.split("_")[1]), "❌ Rejected.")
        await query.edit_message_caption(caption="❌ Rejected.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
