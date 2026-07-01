import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from database import create_tables, add_user

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username or "No Username"
    )

    await update.message.reply_text(
        "👑 Welcome to KING iOS Bot\n\n"
        "Your account has been created."
    )

def main():
    create_tables()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    print("Bot is running...")

    app.run_polling()

if __name__ == "__main__":
    main()