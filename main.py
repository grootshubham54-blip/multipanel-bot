import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

from database import create_tables, add_payment, get_payment, approve_payment, assign_key

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "KING iOS": ["1 Day", "1 Week", "1 Month"],
    "WINIOS": ["1 Day", "1 Week", "1 Month"]
}

# user state memory
USER_STATE = {}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send 'Games' to start.")

# ---------------- MESSAGE ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # GAME SELECT
    if text in GAME_PLANS:
        USER_STATE[uid] = {"game": text}
        kb = [[InlineKeyboardButton(p, callback_data=f"plan|{p}")] for p in GAME_PLANS[text]]
        await update.message.reply_text("Select Plan:", reply_markup=InlineKeyboardMarkup(kb))
        return

    # PAYMENT SCREENSHOT
    if update.message.photo and uid != ADMIN_ID:
        state = USER_STATE.get(uid, {})
        game = state.get("game", "NA")
        plan = state.get("plan", "NA")
        payment_id = add_payment(uid, game, plan)

        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=f"Payment #{payment_id}\nUser: {uid}\nGame: {game}\nPlan: {plan}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Approve", callback_data=f"acc|{payment_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rej|{payment_id}")
            ]])
        )
        await update.message.reply_text("Sent to admin ✔️")
        return

# ---------------- CALLBACK ----------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    # FIX 1: Loading spinner को हटाना
    await q.answer() 
    data = q.data

    # PLAN SELECT
    if data.startswith("plan|"):
        plan = data.split("|")[1]
        uid = q.from_user.id
        if uid in USER_STATE:
            USER_STATE[uid]["plan"] = plan
        await q.message.reply_photo(photo=open("qr.JPG", "rb"), caption="Send payment screenshot")
        return

    # APPROVE
    if data.startswith("acc|"):
        pid = int(data.split("|")[1])
        payment = get_payment(pid)
        if not payment:
            await q.edit_message_caption("Payment not found")
            return

        uid, game, plan = payment
        key = assign_key(uid, game, plan)

        if key:
            approve_payment(pid)
            # FIX 2: Markdown का उपयोग करके की (Key) को स्पष्ट दिखाना
            await context.bot.send_message(uid, f"✅ Your Key: `{key}`", parse_mode="Markdown")
            await q.edit_message_caption(f"Approved ✔️ Key sent to user")
        else:
            await q.edit_message_caption("❌ No stock available")
        return

    # REJECT
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
    app.run_polling()

if __name__ == "__main__":
    main()
