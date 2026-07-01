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
    update_payment_status,
    save_key,
    get_stock,
    get_total_users,
    get_total_purchases
)

from payment import save_payment
from admin_panel import admin_keyboard


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


    if user.id == ADMIN_ID:
        keyboard.append(
            ["⚙️ Admin Panel"]
        )


    await update.message.reply_text(
        "👑 Welcome to KING iOS Bot\n\nSelect option:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )



async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user = update.effective_user


    # ADMIN PANEL OPEN

    if text == "⚙️ Admin Panel":

        if user.id == ADMIN_ID:

            await update.message.reply_text(
                "👑 Admin Panel",
                reply_markup=admin_keyboard()
            )

        return



    # ADD KEY MODE

    if context.user_data.get("adding_key"):

        if user.id == ADMIN_ID:

            save_key(text)

            context.user_data["adding_key"] = False

            await update.message.reply_text(
                "✅ Key Added Successfully"
            )

        return



    # ADMIN BUTTONS

    if user.id == ADMIN_ID:


        if text == "🔑 Add Keys":

            context.user_data["adding_key"] = True

            await update.message.reply_text(
                "🔑 Send Key:"
            )

            return


        elif text == "📦 Stock":

            await update.message.reply_text(
                f"📦 Available Keys: {get_stock()}"
            )

            return


        elif text == "👥 Total Users":

            await update.message.reply_text(
                f"👥 Total Users: {get_total_users()}"
            )

            return


        elif text == "💰 Purchases":

            await update.message.reply_text(
                f"💰 Purchases: {get_total_purchases()}"
            )

            return


        elif text == "📊 Statistics":

            await update.message.reply_text(
                "📊 Statistics\n\n"
                f"👥 Users: {get_total_users()}\n"
                f"📦 Stock: {get_stock()}\n"
                f"💰 Purchases: {get_total_purchases()}"
            )

            return



    # USER MENU


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

        plan = context.user_data.get(
            "plan",
            "Unknown"
        )

        amount = context.user_data.get(
            "amount",
            "0"
        )


        payment_id = save_payment(
            user.id,
            plan,
            amount
        )


        await update.message.reply_text(
            "✅ Payment request sent to admin."
        )


        if ADMIN_ID:

            buttons = InlineKeyboardMarkup(
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
                    f"👤 User ID: {user.id}\n"
                    f"👑 Plan: {plan}\n"
                    f"💰 Amount: ₹{amount}"
                ),
                reply_markup=buttons
            )



    elif text == "📞 Support":

        await update.message.reply_text(
            "📞 Support\n\nContact Admin."
        )



    elif text == "👤 Profile":

        await update.message.reply_text(
            f"👤 Profile\n\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username}"
        )



    elif text == "🔑 My Keys":

        await update.message.reply_text(
            "🔑 Your Keys will appear here."
        )



    elif text == "💳 Payment":

        await update.message.reply_text(
            "💳 Go to 🎮 Games → 👑 KING iOS"
        )



async def payment_info(update):

    await update.message.reply_text(
        "💳 Payment Details\n\n"
        "Complete payment then press:\n"
        "✅ I've Paid",

        reply_markup=ReplyKeyboardMarkup(
            [
                ["✅ I've Paid"]
            ],
            resize_keyboard=True
        )
    )



async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data



    if data.startswith("accept_"):

        payment_id = int(
            data.split("_")[1]
        )

        update_payment_status(
            payment_id,
            "approved"
        )

        await query.edit_message_text(
            "✅ Payment Approved"
        )



    elif data.startswith("reject_"):

        payment_id = int(
            data.split("_")[1]
        )

        update_payment_status(
            payment_id,
            "rejected"
        )

        await query.edit_message_text(
            "❌ Payment Rejected"
        )



def main():

    create_tables()


    app = Application.builder().token(
        TOKEN
    ).build()



    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )



    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
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