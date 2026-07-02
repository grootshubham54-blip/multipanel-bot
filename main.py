import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from database import (create_tables, add_user, update_payment_status, save_key, get_stock, get_total_users, get_total_purchases, DB_NAME)
from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- KEYBOARDS ---
def get_main_keyboard(user_id):
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID: keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target="Main"):
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard():
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)

# --- HANDLERS ---
async def start(update, context):
    user = update.effective_user
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot", reply_markup=get_main_keyboard(user.id))

async def message_handler(update, context):
    text = update.message.text
    user = update.effective_user

    # Broadcast Mode
    if user.id == ADMIN_ID and context.user_data.get("broadcasting"):
        msg = text
        context.user_data.pop("broadcasting", None)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")

        for row in cursor.fetchall():
            try:
                await context.bot.send_message(
                    chat_id=row[0],
                    text=f"📢 Announcement\n\n{msg}"
                )
            except:
                pass

        conn.close()

        await update.message.reply_text(
            "✅ Broadcast Sent!",
            reply_markup=admin_keyboard()
        )
        return

    # Add Key Mode
    if user.id == ADMIN_ID and context.user_data.get("adding_key"):
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text(
                "👑 Admin Panel",
                reply_markup=admin_keyboard()
            )
            return

        if not context.user_data.get("selected_game"):
            context.user_data["selected_game"] = text

            await update.message.reply_text(
                "🎯 Select Plan:",
                reply_markup=ReplyKeyboardMarkup(
                    [["1 DAY", "1 WEEK", "1 MONTH"],
                     ["🔙 Back to Admin"]],
                    resize_keyboard=True
                )
            )
            return

        elif not context.user_data.get("selected_plan"):
            context.user_data["selected_plan"] = text

            await update.message.reply_text(
                "🔑 Send Key:",
                reply_markup=get_back_keyboard("Admin")
            )
            return

        else:
            save_key(
                context.user_data["selected_game"],
                text,
                context.user_data["selected_plan"]
            )

            context.user_data.pop("selected_game", None)
            context.user_data.pop("selected_plan", None)

            await update.message.reply_text(
                "✅ Key Added Successfully!",
                reply_markup=get_back_keyboard("Admin")
            )
            return

    # User Navigation
    if text == "🎮 Games":
        await update.message.reply_text(
            "Select Game:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["👑 KING iOS"],
                    ["WINIOS", "NEXT IOS"],
                    ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"],
                    ["DOLPHIN IOS"],
                    ["🔙 Back to Main"]
                ],
                resize_keyboard=True
            )
        )

    elif text == "👑 KING iOS":
    stock = get_stock("👑 KING iOS")
    await update.message.reply_text(
        f"👑 KING iOS\n\n"
        f"💰 1 DAY : ₹200\n"
        f"💰 1 WEEK : ₹800\n"
        f"💰 1 MONTH : ₹2000\n\n"
        f"📦 Available Keys: {stock}"
    )

elif text == "WINIOS":
    stock = get_stock("WINIOS")
    await update.message.reply_text(
        f"WINIOS\n\n"
        f"💰 1 DAY : ₹199\n"
        f"💰 1 WEEK : ₹600\n"
        f"💰 1 MONTH : ₹1399\n\n"
        f"📦 Available Keys: {stock}"
    )

elif text == "NEXT IOS":
    stock = get_stock("NEXT IOS")
    await update.message.reply_text(
        f"NEXT IOS\n\n"
        f"💰 1 DAY : ₹200\n"
        f"💰 1 WEEK : ₹799\n\n"
        f"📦 Available Keys: {stock}"
    )

elif text == "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫":
    stock = get_stock("𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫")
    await update.message.reply_text(
        f"🚀 Mars Loader\n\n"
        f"💰 1 DAY : ₹120\n"
        f"💰 1 WEEK : ₹500\n"
        f"💰 1 MONTH : ₹999\n\n"
        f"📦 Available Keys: {stock}"
    )

elif text == "𝘿𝙀𝘼𝘿𝙀𝙔𝙀":
    stock = get_stock("𝘿𝙀𝘼𝘿𝙀𝙔𝙀")
    await update.message.reply_text(
        f"🎯 DEADEYE\n\n"
        f"💰 1 DAY : ₹150\n"
        f"💰 1 WEEK : ₹600\n"
        f"💰 1 MONTH : ₹1500\n\n"
        f"📦 Available Keys: {stock}"
    )

elif text == "DOLPHIN IOS":
    stock = get_stock("DOLPHIN IOS")
    await update.message.reply_text(
        f"🐬 DOLPHIN IOS\n\n"
        f"💰 1 DAY : ₹200\n"
        f"💰 1 WEEK : ₹800\n"
        f"💰 1 MONTH : ₹1600\n\n"
        f"📦 Available Keys: {stock}"
    )

    elif text == "🔑 My Keys":
        await update.message.reply_text("🔑 My Keys")

    elif text == "📞 Support":
        await update.message.reply_text(
            "📞 Support: @IOS_HACK_S"
        )

    elif text == "👤 Profile":
        await update.message.reply_text(
            f"👤 Profile\n\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username or 'None'}"
        )

    elif text == "💳 Payment":
        await update.message.reply_text(
            "💳 Payment Section",
            reply_markup=get_payment_keyboard()
        )

    elif text == "🔙 Back to Main" or text == "❌ Cancel Payment":
        context.user_data.clear()

        await update.message.reply_text(
            "👑 Main Menu",
            reply_markup=get_main_keyboard(user.id)
        )

    # Admin Panel
    elif user.id == ADMIN_ID:

        if text == "⚙️ Admin Panel":
            await update.message.reply_text(
                "👑 Admin Panel",
                reply_markup=admin_keyboard()
            )

        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True

            await update.message.reply_text(
                "Select Game:",
                reply_markup=admin_game_selection_keyboard()
            )

        elif text == "👥 Total Users":
            await update.message.reply_text(
                f"👥 Users: {get_total_users()}"
            )

        elif text == "📦 Stock":
            await update.message.reply_text(
                f"📦 Stock: {get_stock()}"
            )

        elif text == "💰 Purchases":
            await update.message.reply_text(
                f"💰 Purchases: {get_total_purchases()}"
            )

        elif text == "📊 Statistics":
            await update.message.reply_text(
                f"📊 Statistics\n\n"
                f"👥 Users: {get_total_users()}\n"
                f"📦 Stock: {get_stock()}\n"
                f"💰 Purchases: {get_total_purchases()}"
            )

        elif text == "📢 Broadcast":
            context.user_data["broadcasting"] = True

            await update.message.reply_text(
                "📢 Send Broadcast Message"
            )

    else:
        await update.message.reply_text(
            "Please use the menu buttons."
        )

    # 2. USER & ADMIN NAVIGATION
    if text == "🎮 Games":
        await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([["👑 KING iOS"], ["WINIOS", "NEXT IOS"], ["𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫", "𝘿𝙀𝘼𝘿𝙀𝙔𝙀"], ["DOLPHIN IOS"], ["🔙 Back to Main"]], resize_keyboard=True))
    elif text == "🔙 Back to Main" or text == "❌ Cancel Payment":
        context.user_data.clear()
        await update.message.reply_text("👑 Main Menu", reply_markup=get_main_keyboard(user.id))
    
    # ADMIN PANEL NAVIGATION
    elif user.id == ADMIN_ID:
        if text == "⚙️ Admin Panel": await update.message.reply_text("👑 Admin Panel", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["adding_key"] = True
            await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
        elif text == "👥 Total Users": await update.message.reply_text(f"Total Users: {get_total_users()}")
        # [यहाँ अपने बाकी पुराने elif जैसे 👑 KING iOS, WINIOS आदि पेस्ट कर दें]
    
    else:
        await update.message.reply_text("Please use the menu buttons.")

# --- MAIN RUNNER ---
def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
