import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, add_user, get_user_keys, get_stock_count, get_total_users

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["👥 Total Users", "🔙 Back to Admin"]], resize_keyboard=True)

def admin_game_selection_keyboard():
    return ReplyKeyboardMarkup([["👑 KING iOS", "WINIOS"], ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"], ["𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀", "DOLPHIN IOS"], ["🔙 Back to Admin"]], resize_keyboard=True)

def admin_plan_selection_keyboard():
    return ReplyKeyboardMarkup([["1 Day", "1 Week", "1 Month"], ["🔙 Back to Admin"]], resize_keyboard=True)

async def start(update, context):
    user_id = update.effective_user.id
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel":
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "📊 Stock":
            msg = "📊 *Current Stock Available:*\n\n"
            for game, plans in GAME_PLANS.items():
                msg += f"*{game}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(game, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "👥 Total Users":
            await update.message.reply_text(f"👥 Total registered users: {get_total_users()}")
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            await update.message.reply_text("Select Game:", reply_markup=admin_game_selection_keyboard())
        elif state == "select_game" and text in GAME_PLANS.keys():
            context.user_data["add_game"] = text
            context.user_data["state"] = "select_plan"
            await update.message.reply_text("Select Plan:", reply_markup=admin_plan_selection_keyboard())
        elif state == "select_plan":
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys (one per line):", reply_markup=ReplyKeyboardMarkup([["🔙 Back to Admin"]], resize_keyboard=True))
        elif state == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard())
            context.user_data.clear()
        elif text == "🔙 Back to Admin":
            context.user_data.clear()
            await start(update, context)
            return

    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif update.message.photo and user_id != ADMIN_ID:
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}")]]))
        await update.message.reply_text("✅ Screenshot sent!")

async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]
        context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        await query.message.reply_text(f"🎮 *{game}*\nSelect your plan:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif query.data.startswith("pay_"):
        data = query.data.split("_")
        plan, price, game = data[1], data[2], context.user_data.get("game")
        context.user_data["plan"] = plan
        invoice_msg = f"✅ *Plan:* {game} ({plan})\n💰 *Amount:* ₹{price}\n\n👉 *Pay to this QR and send the screenshot here.*"
        try:
            with open("qr.JPG", "rb") as qr: await query.message.reply_photo(photo=qr, caption=invoice_msg, parse_mode="Markdown")
        except: await query.message.reply_text("⚠️ QR file not found!")
    elif query.data.startswith("acc_"):
        uid = int(query.data.split("_")[1])
        key = approve_and_assign_key(uid, context.user_data.get("game"), context.user_data.get("plan"))
        if key:
            await context.bot.send_message(uid, f"✅ *Payment Approved!*\n\n🎮 {context.user_data.get('game')}\n🔑 *Key:* `{key}`", parse_mode="Markdown")
            await query.edit_message_caption(caption=f"✅ Approved! Key delivered.")
        else: await query.edit_message_caption(caption="⚠️ Error: No keys available!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
