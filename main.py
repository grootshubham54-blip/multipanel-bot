import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from database import (
    create_tables,
    add_user,
    add_payment,
    get_payment,
    approve_payment,
    assign_key,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

# ---------------- GAME DATA ----------------
GAME_PLANS = {
    "KING iOS": ["1 Day", "1 Week", "1 Month"],
    "WINIOS": ["1 Day", "1 Week", "1 Month"],
    "NEXT IOS": ["1 Day", "1 Week", "1 Month"],
}

# ---------------- MEMORY (safe + simple) ----------------
USER_STATE = {}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "unknown")

    await update.message.reply_text(
        "🎮 Welcome!\nSend *Games* to start.",
        parse_mode="Markdown"
    )

# ---------------- MESSAGE HANDLER ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # auto-add user
    add_user(uid, update.effective_user.username or "unknown")

    # avoid crash
    text = update.message.text if update.message.text else ""

    # ---------------- GAME SELECT ----------------
    if text in GAME_PLANS:
        USER_STATE[uid] = {"game": text}

        kb = [
            [InlineKeyboardButton(p, callback_data=f"plan|{p}")]
            for p in GAME_PLANS[text]
        ]

        await update.message.reply_text(
            "📦 Select Plan:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    # ---------------- PAYMENT SCREENSHOT ----------------
    if update.message.photo and uid != ADMIN_ID:
        state = USER_STATE.get(uid, {})
        game = state.get("game", "NA")
        plan = state.get("plan", "NA")

        payment_id = add_payment(uid, game, plan)

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Approve", callback_data=f"acc|{payment_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"rej|{payment_id}")
        ]])

        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=f"💰 Payment #{payment_id}\nUser: {uid}\nGame: {game}\nPlan: {plan}",
            reply_markup=kb
        )

        await update.message.reply_text("✅ Payment sent to admin.")
        return

# ---------------- CALLBACK HANDLER ----------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()  # important fix

    data = q.data

    # ---------------- PLAN SELECT ----------------
    if data.startswith("plan|"):
        plan = data.split("|")[1]
        uid = q.from_user.id

        if uid in USER_STATE:
            USER_STATE[uid]["plan"] = plan

        await q.message.reply_text("📸 Now send payment screenshot.")
        return

    # ---------------- APPROVE ----------------
    if data.startswith("acc|"):
        pid = int(data.split("|")[1])

        payment = get_payment(pid)
        if not payment:
            await q.edit_message_caption("❌ Payment not found")
            return

        uid, game, plan = payment

        key = assign_key(uid, game, plan)

        if key:
            approve_payment(pid)

            await context.bot.send_message(
                uid,
                f"🎉 Approved!\n\n🔑 Your Key:\n`{key}`",
                parse_mode="Markdown"
            )

            await q.edit_message_caption("✅ Approved & Key Sent")
        else:
            await q.edit_message_caption("❌ No stock available")

        return

    # ---------------- REJECT ----------------
    if data.startswith("rej|"):
        pid = int(data.split("|")[1])
        await q.edit_message_caption("❌ Rejected")
        return

# ---------------- MAIN ----------------
def main():
    create_tables()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()