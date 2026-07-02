import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from database import create_tables, approve_and_assign_key
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

# ---------------- GAME PLANS ----------------
GAME_PLANS = {
    "👑 KING iOS": ["1 Day", "1 Week", "1 Month"],
    "WINIOS": ["1 Day", "1 Week", "1 Month"],
    "NEXT IOS": ["1 Day", "1 Week", "1 Month"],
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": ["1 Day", "1 Week", "1 Month"],
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": ["1 Day", "1 Week", "1 Month"],
    "DOLPHIN IOS": ["1 Day", "1 Week", "1 Month"]
}

# ---------------- USER STATE ----------------
USER_STATE = {}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [["🎮 Games"]],
        resize_keyboard=True
    )
    await update.message.reply_text("Welcome! Click below to start.", reply_markup=keyboard)

# ---------------- MESSAGE HANDLER ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    text = update.message.text

    # ---------------- ADMIN ----------------
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel":
            await update.message.reply_text("Admin Panel", reply_markup=admin_keyboard())

        elif text == "📦 Stock":
            await update.message.reply_text("Stock checked.")

        return

    # ---------------- GAME SELECT ----------------
    if text == "🎮 Games":
        await update.message.reply_text(
            "Select Game:",
            reply_markup=admin_game_selection_keyboard()
        )
        return

    # ---------------- GAME STORE ----------------
    if text in GAME_PLANS:
        USER_STATE[user_id] = {"game": text}

        buttons = [
            [InlineKeyboardButton(plan, callback_data=f"plan|{plan}")]
            for plan in GAME_PLANS[text]
        ]

        await update.message.reply_text(
            "Select Plan:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ---------------- PAYMENT SCREENSHOT ----------------
    elif update.message.photo:
        state = USER_STATE.get(user_id, {})

        game = state.get("game", "Unknown")
        plan = state.get("plan", "Unknown")

        # store state safe (NO callback overflow issue)
        context.user_data[f"pay_{user_id}"] = {
            "game": game,
            "plan": plan
        }

        callback_data = f"acc|{user_id}"

        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=f"Payment\nUser: {user_id}\nGame: {game}\nPlan: {plan}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Approve", callback_data=callback_data)
            ]])
        )

        await update.message.reply_text("Payment sent to admin ✔️")

# ---------------- CALLBACK HANDLER ----------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # ---------------- PLAN SELECT ----------------
    if data.startswith("plan|"):
        plan = data.split("|")[1]
        user_id = query.from_user.id

        if user_id in USER_STATE:
            USER_STATE[user_id]["plan"] = plan

        await query.message.reply_photo(
            photo=open("qr.JPG", "rb"),
            caption="Send payment screenshot now"
        )
        return

    # ---------------- APPROVE PAYMENT ----------------
    if data.startswith("acc|"):
        user_id = int(data.split("|")[1])

        pay_info = context.user_data.get(f"pay_{user_id}")

        if not pay_info:
            await query.edit_message_caption("❌ No payment data found")
            return

        game = pay_info["game"]
        plan = pay_info["plan"]

        key = approve_and_assign_key(user_id, game, plan)

        if key:
            await context.bot.send_message(
                user_id,
                f"🎉 Approved!\nYour Key:\n`{key}`",
                parse_mode="Markdown"
            )
            await query.edit_message_caption("✅ Approved & Sent")
        else:
            await query.edit_message_caption("❌ Out of stock")

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