import os
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from database import create_tables
from admin_panel import admin_game_selection_keyboard

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

# Games & Plans
GAME_PLANS = {
    "👑 KING iOS": {
        "1 Day": "200",
        "1 Week": "800",
        "1 Month": "2000"
    },

    "WINIOS": {
        "1 Day": "199",
        "1 Week": "600",
        "1 Month": "1299"
    }
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🎮 Games", "🔑 My Keys"],
        ["📞 Support", "💳 Payment"]
    ]

    await update.message.reply_text(
        "👋 Welcome!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎮 Games":

        await update.message.reply_text(
            "गेम चुनें:",
            reply_markup=admin_game_selection_keyboard()
        )

    elif text in GAME_PLANS:

        keyboard = []

        for plan, price in GAME_PLANS[text].items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{plan} - ₹{price}",
                    callback_data=f"qr_{price}"
                )
            ])

        await update.message.reply_text(
            f"🎮 {text} का प्लान चुनें:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    else:
        await start(update, context)


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    try:
        if query.data.startswith("qr_"):

            with open("qr.JPG", "rb") as qr:
                await query.message.reply_photo(
                    photo=qr,
                    caption="✅ यह रहा QR कोड। पेमेंट करके स्क्रीनशॉट भेजें।"
                )

    except Exception as e:
        logging.error(f"QR Error: {e}")

        await query.message.reply_text(
            f"QR Error:\n{e}"
        )


def main():
    create_tables()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    app.add_handler(
        CallbackQueryHandler(button_click)
    )

    app.run_polling()


if __name__ == "__main__":
    main()