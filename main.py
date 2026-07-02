import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

# Logging setup
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593  # Integer format

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
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "User")
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    # 1. Admin Flow (Add Keys)
    if user_id == ADMIN_ID and state:
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
            return
        if state == "awaiting_game" and text in GAME_PLANS:
            context.user_data.update({"add_game": text, "state": "awaiting_plan"})
            await update.message.reply_text("Choose plan:", reply_markup=admin_plan_selection_keyboard())
            return
        elif state == "awaiting_plan":
            context.user_data.update({"add_plan": text.replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "").strip(), "state": "awaiting_keys"})
            await update.message.reply_text("Enter keys (one per line):")
            return
        elif state == "awaiting_keys":
            for key in text.split("\n"): save_key(context.user_data["add_game"], key.strip(), context.user_data["add_plan"])
            context.user_data.clear()
            await update.message.reply_text("✅ Keys added!", reply_markup=admin_keyboard())
            return

    # 2. Admin Menu
    if user_id == ADMIN_ID and text in ["🛠 Admin Panel", "🔙 Back to Admin"]:
        await update.message.reply_text("🛠 Admin Panel:", reply_markup=admin_keyboard())
        return
    elif user_id == ADMIN_ID and text == "🔑 Add Keys":
        context.user_data["state"] = "awaiting_game"
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
        return
    elif user_id == ADMIN_ID and text == "📦 Stock":
        msg = "\n".join([f"{g}: {sum([get_stock_count(g, p) for p in GAME_PLANS[g]])} left" for g in GAME_PLANS])
        await update.message.reply_text(f"📦 Stock:\n{msg}")
        return
    elif user_id == ADMIN_ID and text == "👥 Total Users":
        await update.message.reply_text(f"👥 Users: {get_total_users()}")
        return

    # 3. Customer Flow
    if update.message.photo and user_id != ADMIN_ID:
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{context.user_data.get('last_game','')}_{context.user_data.get('last_plan','')}")], [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot sent to Admin!")
        return
    
    if text == "🎮 Games": await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{GAME_MAP[text]}_{PLAN_MAP[p]}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))
    else: await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data.startswith("plan_"):
        _, g, p = data.split("_")
        context.user_data.update({"last_game": g, "last_plan": p})
        if os.path.exists("qr.JPG"): await query.message.reply_photo(open("qr.JPG", "rb"), caption="Pay here and send screenshot.")
        else: await query.message.reply_text("Error: QR image missing.")
    elif data.startswith("acc_"):
        _, uid, g, p = data.split("_")
        key = approve_and_assign_key(int(uid), REV_GAME_MAP[g], REV_PLAN_MAP[p])
        await context.bot.send_message(int(uid), f"✅ Key: `{key}`") if key else await query.message.reply_text("Out of stock!")
        await query.edit_message_caption(caption="✅ Approved.")
    elif data.startswith("rej_"):
        await context.bot.send_message(int(data.split("_")[1]), "❌ Rejected.")
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
