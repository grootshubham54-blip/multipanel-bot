import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

from database import (
    create_tables,
    add_user,
    create_payment,
    get_payment,
    approve_payment,
    assign_key
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "KING iOS": ["1 Day", "1 Week", "1 Month"],
    "WINIOS": ["1 Day", "1 Week", "1 Month"],
    "NEXT IOS": ["1 Day", "1 Week", "1 Month"],
}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    add_user(uid, update.effective_user.username or "user")

    await update.message.reply_text("Send 'Games' to start.")

# ---------------- MESSAGE ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text or ""

    add_user(uid, update.effective_user.username or "user")

    # ---------------- GAME SELECT ----------------
    if text in GAME_PLANS:
        kb = [[InlineKeyboardButton(p, callback_data=f"plan|{text}|{p}")] for p in GAME_PLANS[text]]

        await update.message.reply_text(
            "Select Plan:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    # ---------------- PAYMENT SCREENSHOT ----------------
    if update.message.photo and uid != ADMIN_ID:
        payment_id = create_payment(uid)

        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=f"Payment ID: {payment_id}\nUser: {uid}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Approve", callback_data=f"acc|{payment_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rej|{payment_id}")
            ]])
        )

        await update.message.reply_text("Payment sent to admin ✔️")
        return

# ---------------- CALLBACK ----------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    data = q.data

    # ---------------- PLAN SELECT ----------------
    if data.startswith("plan|"):
        _, game, plan = data.split("|")

        payment_id = create_payment(q.from_user.id, game, plan)

        await q.message.reply_text("Now send payment screenshot.")
        return

    # ---------------- APPROVE ----------------
    if data.startswith("acc|"):
        payment_id = int(data.split("|")[1])

        payment = get_payment(payment_id)
        if not payment:
            await q.edit_message_caption("Payment not found")
            return

        uid, game, plan = payment

        key = assign_key(uid, game, plan)

        if key:
            approve_payment(payment_id)

            await context.bot.send_message(
                uid,
                f"🎉 Approved!\n🔑 Key:\n`{key}`",
                parse_mode="Markdown"
            )

            await q.edit_message_caption("Approved ✔️ Key sent")
        else:
            await q.edit_message_caption("❌ No stock")

    # ---------------- REJECT ----------------
    if data.startswith("rej|"):
        payment_id = int(data.split("|")[1])
        approve_payment(payment_id, status="rejected")
        await q.edit_message_caption("❌ Rejected")

# ---------------- MAIN ----------------
def main():
    create_tables()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()