import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = "7908981593"

# आपकी दी गई नई प्राइसिंग के साथ अपडेटेड कोड:
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(update.effective_user.id) == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    state = context.user_data.get("state")

    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "👑 KING iOS")
        p = context.user_data.get("u_plan", "1 Day")
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 Game: {g}\n📦 Plan: {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{GAME_MAP[g]}_{PLAN_MAP[p]}")], [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot received!")
        return

    if user_id == ADMIN_ID and state:
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
            return
        if state == "awaiting_game":
            if text in GAME_PLANS:
                context.user_data.update({"add_game": text, "state": "awaiting_plan"})
                await update.message.reply_text("Now choose the plan:", reply_markup=admin_plan_selection_keyboard())
            return
        elif state == "awaiting_plan":
            context.user_data.update({"add_plan": text, "state": "awaiting_keys"})
            await update.message.reply_text("📝 Enter the Keys:")
            return
        elif state == "awaiting_keys":
            keys = [k.strip() for k in text.split("\n") if k.strip()]
            for key in keys: save_key(context.user_data["add_game"], key, context.user_data["add_plan"])
            context.user_data.clear()
            await update.message.reply_text("✅ Saved!", reply_markup=admin_keyboard())
            return

    if user_id == ADMIN_ID:
        if text in ["🛠 Admin Panel", "🔙 Back to Admin"]:
            await update.message.reply_text("Admin:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("Choose game:", reply_markup=admin_game_selection_keyboard())
        return

    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{GAME_MAP[text]}_{PLAN_MAP[p]}_{pr}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(update.effective_user.id)
        msg = "\n".join([f"🎮 {k[0]} ({k[1]}): `{k[2]}`" for k in keys]) if keys else "❌ No keys."
        await update.message.reply_text(msg, parse_mode="Markdown")
    else: await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data.startswith("pay_"):
        _, g, p, pr = data.split("_")
        context.user_data.update({"u_game": REV_GAME_MAP[g], "u_plan": REV_PLAN_MAP[p]})
        await query.message.reply_text(f"Send screenshot of ₹{pr}")
    elif data.startswith("acc_"):
        _, uid, g, p = data.split("_")
        key = approve_and_assign_key(int(uid), REV_GAME_MAP[g], REV_PLAN_MAP[p])
        await context.bot.send_message(int(uid), f"✅ Key: `{key}`" if key else "⚠️ Out of stock!")
        await query.edit_message_caption(caption="✅ Approved.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
