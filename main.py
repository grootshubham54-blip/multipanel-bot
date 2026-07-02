import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
from database import create_tables, approve_and_assign_key

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": ["1 Day", "1 Week", "1 Month"],
    "WINIOS": ["1 Day", "1 Week", "1 Month"]
}

# ---------------- START BUTTON ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [["🎮 Games"]],
        resize_keyboard=True
    )
    await update.message.reply_text("Welcome!", reply_markup=keyboard)

# ---------------- MESSAGE ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # GAME BUTTON CLICK
    if text == "🎮 Games":
        buttons = [[KeyboardButton(game)] for game in GAME_PLANS.keys()]
        await update.message.reply_text(
            "Select Game:",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
        return

    # GAME SELECT
    if text in GAME_PLANS:
        context.user_data["last_game"] = text

        kb = [[InlineKeyboardButton(p, callback_data=f"plan|{p}")] for p in GAME_PLANS[text]]

        await update.message.reply_text(
            "Select Plan:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    # PAYMENT PHOTO
    if update.message.photo and user_id != ADMIN_ID:
        game = context.user_data.get("last_game")
        plan = context.user_data.get("last_plan")

        context.user_data[f"pay_{user_id}"] = {"game": game, "plan": plan}

        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=f"User: {user_id}\nGame: {game}\nPlan: {plan}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Approve", callback_data=f"acc|{user_id}")
            ]])
        )

        await update.message.reply_text("Sent to admin ✔️")

# ---------------- CALLBACK ----------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # PLAN SELECT FIX
    if data.startswith("plan|"):
        plan = data.split("|")[1]
        uid = query.from_user.id

        context.user_data["last_plan"] = plan

        await query.message.reply_text("Send payment screenshot 📸")
        return

    # APPROVE
    if data.startswith("acc|"):
        uid = int(data.split("|")[1])

        data = context.user_data.get(f"pay_{uid}")

        if not data:
            await query.edit_message_caption("No data found")
            return

        key = approve_and_assign_key(uid, data["game"], data["plan"])

        if key:
            await context.bot.send_message(uid, f"✅ Your Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_caption("Approved ✔️")
        else:
            await query.edit_message_caption("Out of stock ❌")

# ---------------- MAIN ----------------
def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_polling()

if __name__ == "__main__":
    main()