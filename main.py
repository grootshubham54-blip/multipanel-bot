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

    await update.message.reply_text(
        "👑 Welcome to KING iOS Bot\n\nSelect an option:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user


    if text == "🎮 Games":

        keyboard = [
            ["👑 KING iOS"]
        ]

        await update.message.reply_text(
            "🎮 Games\n\nSelect Game:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )


    elif text == "👑 KING iOS":

        keyboard = [
            ["👑 1 DAY - ₹200"],
            ["👑 1 WEEK - ₹800"],
            ["👑 1 MONTH - ₹2000"]
        ]

        await update.message.reply_text(
            "👑 KING iOS Plans\n\nSelect your plan:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )


    elif text == "👑 1 DAY - ₹200":

        context.user_data["plan"] = "1 DAY"
        context.user_data["amount"] = "200"

        await payment_message(update)


    elif text == "👑 1 WEEK - ₹800":

        context.user_data["plan"] = "1 WEEK"
        context.user_data["amount"] = "800"

        await payment_message(update)


    elif text == "👑 1 MONTH - ₹2000":

        context.user_data["plan"] = "1 MONTH"
        context.user_data["amount"] = "2000"

        await payment_message(update)


    elif text == "✅ I've Paid":

        plan = context.user_data.get("plan", "Unknown")
        amount = context.user_data.get("amount", "0")

        save_payment(
            user.id,
            plan,
            amount
        )

        await update.message.reply_text(
            "✅ Payment request submitted."
        )


    elif text == "📞 Support":

        await update.message.reply_text(
            "📞 Support\n\nContact admin for help."
        )


    elif text == "👤 Profile":

        await update.message.reply_text(
            f"👤 Profile\n\n"
            f"User ID: {user.id}\n"
            f"Username: @{user.username}"
        )


    elif text == "🔑 My Keys":

        await update.message.reply_text(
            "🔑 You don't have any keys yet."
        )


    elif text == "💳 Payment":

        await update.message.reply_text(
            "💳 Payment\n\nPlease select a plan from Games → KING iOS."
        )


async def payment_message(update):

    await update.message.reply_text(
        "💳 Payment Details\n\n"
        "Complete your payment and press:\n"
        "✅ I've Paid",

        reply_markup=ReplyKeyboardMarkup(
            [["✅ I've Paid"]],
            resize_keyboard=True
        )
    )


def main():

    create_tables()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            button_handler
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()