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

    if text == "📞 Support":
        await update.message.reply_text(
            "📞 Support\n\nPlease contact admin for help."
        )

    elif text == "👤 Profile":
        user = update.effective_user

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
        await update.message.reply_text(
            "💳 Payment section coming soon."
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