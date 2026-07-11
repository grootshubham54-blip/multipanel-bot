mport os
import logging

from dotenv import load_dotenv

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import database as db


# ==============================
# CONFIG
# ==============================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

QR_IMAGE = "qr.JPG"

SUPPORT_USERNAME = "@IOS_HACK_S"


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)



# ==============================
# DEFAULT GAMES
# ==============================

GAMES = {

    "👑 KING iOS": {
        "name": "KING iOS",
        "plans": {
            "1 DAY": 200,
            "1 WEEK": 800,
            "1 MONTH": 2000
        }
    },


    "🏆 WIN iOS": {
        "name": "WIN iOS",
        "plans": {
            "1 DAY": 199,
            "1 WEEK": 699,
            "1 MONTH": 1399
        }
    },


    "🚀 NEXT iOS": {
        "name": "NEXT iOS",
        "plans": {
            "1 DAY": 250,
            "1 WEEK": 800,
            "1 MONTH": 2000
        }
    },


    "🪐 Mars Loader": {
        "name": "Mars Loader",
        "plans": {
            "1 DAY": 130,
            "1 WEEK": 499,
            "1 MONTH": 999
        }
    },


    "🎯 DEAD EYE": {
        "name": "DEAD EYE",
        "plans": {
            "1 DAY": 150,
            "1 WEEK": 600,
            "1 MONTH": 1599
        }
    },


    "🐬 DOLPHIN iOS": {
        "name": "DOLPHIN iOS",
        "plans": {
            "1 DAY": 200,
            "1 WEEK": 799,
            "1 MONTH": 2000
        }
    }

}



# ==============================
# MENUS
# ==============================


def main_menu(uid):

    menu = [

        ["🎮 Games", "🔑 My Keys"],

        ["💳 Payment", "📞 Support"],

        ["👤 Profile"]

    ]


    if uid == ADMIN_ID:

        menu.append(
            ["👑 Admin Panel"]
        )


    return ReplyKeyboardMarkup(
        menu,
        resize_keyboard=True
    )




def games_menu():


    buttons = []


    for game in GAMES:

        buttons.append(
            [
                KeyboardButton(game)
            ]
        )


    buttons.append(
        [
            KeyboardButton("⬅️ Back")
        ]
    )


    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )




def admin_menu():

    return ReplyKeyboardMarkup(

        [

            ["💳 Payment Management","📦 Stock Management"],

            ["🔑 Key Management","👥 User Management"],

            ["📊 Statistics","📢 Broadcast"],

            ["🎮 Game Management","⚙️ Bot Settings"],

            ["📂 Backup","⬅️ Back"]

        ],

        resize_keyboard=True

    )



# ==============================
# START COMMAND
# ==============================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user


    db.add_user(

        user.id,

        user.username or user.first_name

    )


    await update.message.reply_text(

"""
🎮 Welcome to IOS SHUBHAM License Store


Premium Gaming License Provider


Select option below 👇
""",

        reply_markup=main_menu(user.id)

    )
    
    
# ==============================
# PAYMENT CALLBACK
# ==============================

async def payment_callback(update, context):

    query = update.callback_query

    await query.answer()


    payment = context.user_data.get("payment")


    if not payment:

        await query.edit_message_caption(
            "❌ Payment data missing"
        )

        return



    pid = db.save_payment(

        update.effective_user.id,

        payment["game"],

        payment["plan"],

        payment["amount"]

    )



    keyboard = [

        [

            InlineKeyboardButton(
                "✅ Accept",
                callback_data=f"accept_{pid}"
            ),

            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{pid}"
            )

        ]

    ]



    await context.bot.send_message(

        ADMIN_ID,

f"""
🆕 New Payment Request


👤 User:

{update.effective_user.first_name}


🆔 ID:

{update.effective_user.id}


🎮 Game:

{payment["game"]}


📅 Plan:

{payment["plan"]}


💰 Amount:

₹{payment["amount"]}

""",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )



    await query.edit_message_caption(

        "✅ Payment Submitted\n\nWait for Admin Approval."

    )





# ==============================
# ADMIN PAYMENT ACTION
# ==============================


async def admin_payment_action(update, context):

    query = update.callback_query

    await query.answer()


    if update.effective_user.id != ADMIN_ID:

        return



    action, pid = query.data.split("_")



    payment = db.get_payment(

        int(pid)

    )



    if not payment:


        await query.edit_message_text(

            "❌ Payment Not Found"

        )

        return



    user_id = payment[0]

    game = payment[1]

    plan = payment[2]





    if action == "accept":


        key = db.get_available_key(

            game,

            plan

        )


        if not key:


            await query.edit_message_text(

                "❌ No Key Available"

            )

            return




        db.save_user_key(

            user_id,

            game,

            plan,

            key

        )



        db.update_payment(

            int(pid),

            "accepted"

        )



        await context.bot.send_message(

            user_id,

f"""
✅ Payment Approved


🎮 Game:

{game}


📅 Plan:

{plan}


🔑 Your Key:


{key}

"""

        )


        await query.edit_message_text(

            "✅ Payment Accepted\n🔑 Key Sent"

        )



    else:


        db.update_payment(

            int(pid),

            "rejected"

        )


        await context.bot.send_message(

            user_id,

            "❌ Payment Rejected"

        )


        await query.edit_message_text(

            "❌ Payment Rejected"

        )





# ==============================
# KEY MANAGEMENT
# ==============================


async def key_management(update, context):

    text = update.message.text



    if text == "🔑 Key Management":


        context.user_data["key_game_select"] = True


        await update.message.reply_text(

            "🎮 Select Game:",

            reply_markup=games_menu()

        )


        return True




    if context.user_data.get("key_game_select"):


        if text in GAMES:


            context.user_data["key_game"] = text

            context.user_data["key_game_select"] = False

            context.user_data["key_plan_select"] = True



            buttons = []



            for plan in GAMES[text]["plans"]:


                buttons.append(

                    [

                        KeyboardButton(plan)

                    ]

                )



            await update.message.reply_text(

                "📅 Select Plan:",

                reply_markup=ReplyKeyboardMarkup(

                    buttons,

                    resize_keyboard=True

                )

            )


            return True





    if context.user_data.get("key_plan_select"):


        game = context.user_data.get(

            "key_game"

        )



        if text in GAMES[game]["plans"]:


            context.user_data["key_plan"] = text

            context.user_data["key_plan_select"] = False

            context.user_data["enter_key"] = True



            await update.message.reply_text(

                "🔑 Send Key:"

            )


            return True




    if context.user_data.get("enter_key"):


        db.add_key(

            context.user_data["key_game"],

            context.user_data["key_plan"],

            text.strip()

        )



        context.user_data.clear()



        await update.message.reply_text(

            "✅ Key Added Successfully",

            reply_markup=admin_menu()

        )


        return True



    return False





# ==============================
# GAME MANAGEMENT FUNCTIONS
# ==============================


async def game_management(update, context):

    text = update.message.text



    if text == "🎮 Game Management":


        context.user_data["game_manage"] = True


        await update.message.reply_text(
"""
🎮 Game Management

Select Action:

➕ Add Game
❌ Delete Game
💰 Edit Price
🟢 Enable Game
🔴 Disable Game
"""
        )

        return True



    return False
    
    
# ==============================
# BUTTON HANDLER
# ==============================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    uid = update.effective_user.id



    # ==========================
    # ADMIN PANEL
    # ==========================

    if text == "👑 Admin Panel" and uid == ADMIN_ID:

        await update.message.reply_text(
            "👑 Admin Panel",
            reply_markup=admin_menu()
        )

        return



    # ==========================
    # SUPPORT
    # ==========================

    if text == "📞 Support":

        await update.message.reply_text(
f"""
📞 Support

Contact:

{SUPPORT_USERNAME}
"""
        )

        return



    # ==========================
    # BOT SETTINGS
    # ==========================

    if text == "⚙️ Bot Settings" and uid == ADMIN_ID:


        await update.message.reply_text(
f"""
⚙️ Bot Settings


🤖 Status:
✅ Running


💳 Payment:
QR Manual Approval


📞 Support:
{SUPPORT_USERNAME}


🗄 Database:
SQLite


👑 Admin:
{ADMIN_ID}
"""
        )

        return




    # ==========================
    # GAME MANAGEMENT
    # ==========================

    if uid == ADMIN_ID:


        if await game_management(update, context):

            return




        if text == "➕ Add Game":


            context.user_data["add_game"] = True


            await update.message.reply_text(
                "Send Game Name:"
            )

            return



        if context.user_data.get("add_game"):


            db.add_game(text)


            context.user_data.clear()


            await update.message.reply_text(
                "✅ Game Added",
                reply_markup=admin_menu()
            )

            return




        if text == "❌ Delete Game":


            context.user_data["delete_game"] = True


            await update.message.reply_text(
                "Send Game Name to Delete:"
            )

            return




        if context.user_data.get("delete_game"):


            db.delete_game(text)


            context.user_data.clear()


            await update.message.reply_text(
                "❌ Game Deleted",
                reply_markup=admin_menu()
            )

            return




        if text == "💰 Edit Price":


            context.user_data["edit_price"] = True


            await update.message.reply_text(
                "Send Plan ID and New Price\nExample:\n1 500"
            )

            return




        if context.user_data.get("edit_price"):


            try:

                plan_id, price = text.split()


                db.update_game_price(

                    int(plan_id),

                    int(price)

                )


                await update.message.reply_text(
                    "✅ Price Updated"
                )


            except:

                await update.message.reply_text(
                    "❌ Wrong Format"
                )


            context.user_data.clear()

            return





        if text == "🟢 Enable Game":


            context.user_data["enable_game"] = True


            await update.message.reply_text(
                "Send Game Name:"
            )

            return




        if text == "🔴 Disable Game":


            context.user_data["disable_game"] = True


            await update.message.reply_text(
                "Send Game Name:"
            )

            return




        if context.user_data.get("enable_game"):


            db.set_game_status(
                text,
                "active"
            )


            context.user_data.clear()


            await update.message.reply_text(
                "🟢 Game Enabled"
            )

            return




        if context.user_data.get("disable_game"):


            db.set_game_status(
                text,
                "disabled"
            )


            context.user_data.clear()


            await update.message.reply_text(
                "🔴 Game Disabled"
            )

            return




    # ==========================
    # KEY MANAGEMENT
    # ==========================

    if uid == ADMIN_ID:


        if await key_management(update, context):

            return




    # ==========================
    # GAMES
    # ==========================

    if text == "🎮 Games":

        await update.message.reply_text(
            "🎮 Select Game:",
            reply_markup=games_menu()
        )

        return




    if text in GAMES:


        buttons=[]


        for plan, price in GAMES[text]["plans"].items():

            buttons.append(
                [
                    KeyboardButton(
                        f"{plan} ₹{price}"
                    )
                ]
            )


        await update.message.reply_text(
            "📅 Select Plan:",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True
            )
        )

        return





    # ==========================
    # PAYMENT QR
    # ==========================

    for game in GAMES:


        for plan, price in GAMES[game]["plans"].items():


            if text == f"{plan} ₹{price}":


                context.user_data["payment"] = {

                    "game":game,

                    "plan":plan,

                    "amount":price

                }


                with open(QR_IMAGE,"rb") as qr:


                    await update.message.reply_photo(

                        qr,

                        caption=f"""
💳 Payment


🎮 Game:
{game}


📅 Plan:
{plan}


💰 Amount:
₹{price}


Payment के बाद

✅ I've Paid दबाएं
""",

                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "✅ I've Paid",
                                        callback_data="paid"
                                    )
                                ]
                            ]
                        )

                    )


                return





    # ==========================
    # MY KEYS
    # ==========================


    if text == "🔑 My Keys":


        keys = db.get_user_keys(uid)


        if not keys:


            await update.message.reply_text(
                "❌ No Keys Found"
            )

        else:


            msg="🔑 Your Keys\n\n"


            for k in keys:

                msg += f"""
🎮 {k[0]}

📅 {k[1]}

🔑 {k[2]}

--------------
"""


            await update.message.reply_text(msg)


        return





    # ==========================
    # PROFILE
    # ==========================


    if text == "👤 Profile":


        await update.message.reply_text(
f"""
👤 Profile

Name:
{update.effective_user.first_name}


ID:
{uid}
"""
        )

        return




    if text == "⬅️ Back":


        context.user_data.clear()


        await update.message.reply_text(
            "🏠 Main Menu",
            reply_markup=main_menu(uid)
        )

        return





# ==============================
# MAIN
# ==============================


def main():


    db.create_tables()


    app = ApplicationBuilder().token(
        BOT_TOKEN
    ).build()



    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )



    app.add_handler(
        CallbackQueryHandler(
            payment_callback,
            pattern="^paid$"
        )
    )



    app.add_handler(
        CallbackQueryHandler(
            admin_payment_action,
            pattern="^(accept|reject)_"
        )
    )



    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            buttons
        )
    )



    print("BOT RUNNING...")


    app.run_polling()




if __name__ == "__main__":

    main()