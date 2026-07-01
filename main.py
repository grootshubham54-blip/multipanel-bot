import os
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import create_tables, add_user
from payment import save_payment

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username or "No Username"
    )

    keyboard = [
        ["🎮 Games", "🔑 My Keys"],
        ["📞 Support", "👤 Profile"],
        ["💳 Payment"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👑 Welcome to KING iOS Bot\n\n"
        "Select an option:",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "📞 Support":
        await update.message.reply_text(
            "📞 Support\n\nContact admin for help."
        )

    elif text == "👤 Profile":
        await update.message.reply_text(
            f"👤 Profile\n\n"
            f"User ID: {user.id}\n"
            f"Username: @{user.username}"
        )

    elif text == "🎮 Games":
        await update.message.reply_text(
            "🎮 Games section coming soon."
        )

    elif text == "🔑 My Keys":
        await update.message.reply_text(
            "🔑 You don't have any keys yet."
        )

    elif text == "💳 Payment":
        keyboard = [
            ["✅ I've Paid"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "💳 Payment\n\n"
            "Complete your payment and press the button below.",
            reply_markup=reply_markup
        )

    elif text == "✅ I've Paid":
        save_payment(
            user.id,
            "Pending"
        )

        await update.message.reply_text(
            "✅ Your payment request has been sent."
        )


def main():
    create_tables()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()