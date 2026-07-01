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

from database import (
    create_tables,
    add_user,
    update_payment_status
)

from payment import save_payment

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))


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

        await update.message.reply_text(
            "🎮 Games\n\nSelect Game:",
            reply_markup=ReplyKeyboardMarkup(
                [["👑 KING iOS"]],
                resize_keyboard=True
            )
        )


    elif text == "👑 KING iOS":

        await update.message.reply_text(
            "👑 KING iOS Plans:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["👑 1 DAY - ₹200"],
                    ["👑 1 WEEK - ₹800"],
                    ["👑 1 MONTH - ₹2000"]
                ],
                resize_keyboard=True
            )
        )


    elif text.startswith("👑 1 DAY"):

        context.user_data["plan"] = "1 DAY"
        context.user_data["amount"] = "200"

        await payment_info(update)


    elif text.startswith("👑 1 WEEK"):

        context.user_data["plan"] = "1 WEEK"
        context.user_data["amount"] = "800"

        await payment_info(update)


    elif text.startswith("👑 1 MONTH"):

        context.user_data["plan"] = "1 MONTH"
        context.user_data["amount"] = "2000"

        await payment_info(update)


    elif text == "✅ I've Paid":

        plan = context.user_data.get("plan", "Unknown")
        amount = context.user_data.get("amount", "0")

        payment_id = save_payment(
            user.id,
            plan,
            amount
        )

        await update.message.reply_text(
            "✅ Payment request sent to admin."
        )


        if ADMIN_ID:

            admin_keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ Accept",
                            callback_data=f"accept_{payment_id}"
                        ),
                        InlineKeyboardButton(
                            "❌ Reject",
                            callback_data=f"reject_{payment_id}"
                        )
                    ]
                ]
            )


            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "🔔 New Payment Request\n\n"
                    f"👤 User: @{user.username}\n"
                    f"🆔 ID: {user.id}\n\n"
                    f"👑 Plan: {plan}\n"
                    f"💰 Amount: ₹{amount}\n\n"
                    "Status: Pending"
                ),
                reply_markup=admin_keyboard
            )


    elif text == "📞 Support":

        await update.message.reply_text(
            "📞 Support\n\nContact admin for help."
        )


    elif text == "👤 Profile":

        await update.message.reply_text(
            f"👤 Profile\n\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username}"
        )


    elif text == "🔑 My Keys":

        await update.message.reply_text(
            "🔑 No keys available."
        )


    elif text == "💳 Payment":

        await update.message.reply_text(
            "💳 Payment\n\nGo to 🎮 Games → 👑 KING iOS"
        )


async def payment_info(update):

    await update.message.reply_text(
        "💳 Payment Details\n\n"
        "Complete payment and press:\n"
        "✅ I've Paid",

        reply_markup=ReplyKeyboardMarkup(
            [["✅ I've Paid"]],
            resize_keyboard=True
        )
    )


async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data.startswith("accept_"):

        payment_id = int(data.split("_")[1])

        update_payment_status(
            payment_id,
            "approved"
        )

        await query.edit_message_text(
            "✅ Payment Approved"
        )


    elif data.startswith("reject_"):

        payment_id = int(data.split("_")[1])

        update_payment_status(
            payment_id,
            "rejected"
        )

        await query.edit_message_text(
            "❌ Payment Rejected"
        )


def main():

    create_tables()

    app = Application.builder().token(TOKEN).build()


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            button_handler
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            admin_action
        )
    )


    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()