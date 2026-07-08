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
    save_user,
    is_banned,
    save_order,
    get_order,
    approve_order,
    reject_order,
    save_key,
    get_user_keys,
    get_stock,
    get_total_users
)

from admin_keyboard import (
    admin_keyboard,
    admin_game_selection_keyboard,
    admin_plan_selection_keyboard
)


# =========================
# CONFIG
# =========================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN missing")


ADMIN_ID = int(
    os.getenv("ADMIN_ID", "7908981593")
)


PAYMENT_QR = os.getenv(
    "PAYMENT_QR_FILE_ID",
    "YOUR_QR_FILE_ID"
)



GAME_PLANS = {

    "👑 KING iOS": {
        "1 Day": 200,
        "1 Week": 800,
        "1 Month": 2000
    },

    "WIN iOS": {
        "1 Day": 200,
        "1 Week": 600,
        "1 Month": 1200
    },

    "VISION": {
        "1 Day": 199,
        "1 Week": 799,
        "1 Month": 2199
    },

    "RAGE": {
        "1 Day": 150,
        "1 Week": 599,
        "1 Month": 1499
    }
}



# =========================
# ERROR HANDLER
# =========================

async def error_handler(update, context):

    logging.error(
        "BOT ERROR",
        exc_info=context.error
    )



# =========================
# KEYBOARD
# =========================

def main_keyboard(uid):

    buttons = [
        ["🎮 Games", "🔑 My Keys"],
        ["👤 Profile", "📞 Support"],
        ["💳 Payment"]
    ]


    if uid == ADMIN_ID:
        buttons.append(
            ["🛠 Admin Panel"]
        )


    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )



# =========================
# START
# =========================

async def start(update: Update, context):

    user = update.effective_user


    if is_banned(user.id):
        return


    save_user(
        user.id,
        user.username
    )


    await update.message.reply_text(
        f"👋 Welcome {user.first_name}",
        reply_markup=main_keyboard(user.id)
    )



# =========================
# BUTTON CALLBACK
# =========================

async def callback_handler(update, context):

    query = update.callback_query

    await query.answer()


    data = query.data



    # ADMIN APPROVE / REJECT

    if data.startswith(
        ("approve|", "reject|")
    ):

        if query.from_user.id != ADMIN_ID:
            return


        order_id = int(
            data.split("|")[1]
        )


        order = get_order(order_id)


        if not order:

            await query.edit_message_text(
                "❌ Order not found"
            )
            return



        if order["status"] != "pending":

            await query.edit_message_text(
                "❌ Already processed"
            )
            return



        if data.startswith("approve|"):


            key = approve_order(
                order_id,
                order["game"],
                order["plan"],
                order["user_id"]
            )


            if key:


                await context.bot.send_message(
                    order["user_id"],
                    f"""
✅ Payment Approved

🎮 Game: {order['game']}
📦 Plan: {order['plan']}

🔑 Key:
`{key}`
""",
                    parse_mode="Markdown"
                )


                await query.edit_message_text(
                    "✅ Approved & Key Sent"
                )


            else:

                await query.edit_message_text(
                    "❌ Stock Empty"
                )



        else:


            reject_order(order_id)


            await context.bot.send_message(
                order["user_id"],
                "❌ Payment Rejected"
            )


            await query.edit_message_text(
                "❌ Rejected"
            )


        return




    # GAME SELECT


    if data.startswith("game|"):


        game = data.split("|")[1]


        context.user_data["game"] = game


        buttons = []


        for plan, price in GAME_PLANS[game].items():

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"{plan} - ₹{price}",
                        callback_data=f"plan|{plan}"
                    )
                ]
            )


        await query.edit_message_text(
            f"🎮 {game}\n\nSelect Plan",
            reply_markup=InlineKeyboardMarkup(buttons)
        )



    # PLAN SELECT


    elif data.startswith("plan|"):


        plan = data.split("|")[1]


        game = context.user_data.get(
            "game"
        )


        if not game:

            await query.edit_message_text(
                "❌ Session expired"
            )

            return


        context.user_data["plan"] = plan


        price = GAME_PLANS[game][plan]


        await context.bot.send_photo(
            query.from_user.id,
            PAYMENT_QR,
            caption=f"""
💳 Payment

🎮 {game}
📦 {plan}
💰 ₹{price}

Payment के बाद screenshot भेजें.
"""
        )



# =========================
# MESSAGE HANDLER
# =========================

async def message_handler(update, context):

    user = update.effective_user



    # PHOTO PAYMENT

    if update.message.photo:


        if "game" not in context.user_data:

            await update.message.reply_text(
                "❌ पहले Game select करें"
            )

            return



        order_id = save_order(
            user.id,
            user.username,
            context.user_data["game"],
            context.user_data["plan"]
        )



        buttons = [
            [
                InlineKeyboardButton(
                    "✅ Approve",
                    callback_data=f"approve|{order_id}"
                ),

                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=f"reject|{order_id}"
                )
            ]
        ]



        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=f"""
📦 New Payment

Order ID: {order_id}

User: {user.id}

Game:
{context.user_data['game']}

Plan:
{context.user_data['plan']}
""",
            reply_markup=InlineKeyboardMarkup(buttons)
        )



        await update.message.reply_text(
            "✅ Screenshot Admin को भेज दिया गया"
        )


        context.user_data.clear()

        return




    text = update.message.text or ""



    # ADMIN

    if user.id == ADMIN_ID:


        if text == "🛠 Admin Panel":

            await update.message.reply_text(
                "⚙️ Admin Panel",
                reply_markup=admin_keyboard()
            )

            return



        if text == "📦 Stock":

            stock = get_stock()


            if not stock:

                await update.message.reply_text(
                    "❌ Stock Empty"
                )

                return


            msg = "📦 STOCK\n\n"


            for g,p,c in stock:

                msg += f"{g} | {p} | {c}\n"



            await update.message.reply_text(msg)

            return



        if text == "👥 Total Users":

            await update.message.reply_text(
                f"👥 Users: {get_total_users()}"
            )

            return




        if text == "🔑 Add Keys":

            context.user_data["admin_mode"] = "game"

            await update.message.reply_text(
                "Select Game",
                reply_markup=admin_game_selection_keyboard()
            )

            return



        if context.user_data.get("admin_mode") == "game":


            if text not in GAME_PLANS:

                await update.message.reply_text(
                    "❌ Invalid Game"
                )

                return


            context.user_data["add_game"] = text

            context.user_data["admin_mode"] = "plan"


            await update.message.reply_text(
                "Select Plan",
                reply_markup=admin_plan_selection_keyboard()
            )

            return




        if context.user_data.get("admin_mode") == "plan":


            context.user_data["add_plan"] = text

            context.user_data["admin_mode"] = "keys"


            await update.message.reply_text(
                "Send Keys"
            )

            return



        if context.user_data.get("admin_mode") == "keys":


            for k in text.split("\n"):

                if k.strip():

                    save_key(
                        context.user_data["add_game"],
                        context.user_data["add_plan"],
                        k.strip()
                    )


            context.user_data.clear()


            await update.message.reply_text(
                "✅ Keys Added",
                reply_markup=admin_keyboard()
            )


            return




    # USER


    if text == "🎮 Games":


        buttons = [

            [
                InlineKeyboardButton(
                    g,
                    callback_data=f"game|{g}"
                )
            ]

            for g in GAME_PLANS
        ]


        await update.message.reply_text(
            "Select Game",
            reply_markup=InlineKeyboardMarkup(buttons)
        )



    elif text == "🔑 My Keys":


        keys = get_user_keys(
            user.id
        )


        if not keys:

            await update.message.reply_text(
                "❌ No Keys"
            )

            return



        msg = "🔑 Your Keys\n\n"


        for g,p,k in keys:

            msg += f"{g}\n{p}\n`{k}`\n\n"



        await update.message.reply_text(
            msg,
            parse_mode="Markdown"
        )



    elif text == "👤 Profile":

        await update.message.reply_text(
            f"ID: {user.id}"
        )



    elif text == "📞 Support":

        await update.message.reply_text(
            "@YourAdminUsername"
        )



    elif text == "💳 Payment":

        await update.message.reply_text(
            "🎮 Games से plan select करें"
        )



# =========================
# MAIN
# =========================

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
        CallbackQueryHandler(
            callback_handler
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO,
            message_handler
        )
    )


    app.add_error_handler(
        error_handler
    )



    print("BOT STARTED")


    app.run_polling()



if __name__ == "__main__":
    main()