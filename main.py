import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)

# Make sure to set 'BOT_TOKEN' in your Railway Environment Variables
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

# Replace this with the actual file_id of your QR code image
# To get the file_id, send the image to your bot and print the update object in logs
PAYMENT_QR_FILE_ID = "YOUR_QR_PHOTO_FILE_ID" 

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def main_keyboard(user_id):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game
        msg = f"🎮 Selected: {game}\n\n*Available Plans and Stock:*\n"
        kb = []
        for p, price in GAME_PLANS[game].items():
            stock = get_stock_count(game, p)
            msg += f"- {p} ({price}₹): {'✅' if stock > 0 else '❌'} ({stock} left)\n"
            if stock > 0: kb.append([InlineKeyboardButton(f"{p} ({price}₹)", callback_data=f"plan_{p}")])
        
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb) if kb else None)

    # --- QR LOGIC ADDED HERE ---
    elif data.startswith("plan_"):
        plan_name = data.split("_")[1]
        context.user_data["plan"] = plan_name
        
        # Sends the QR code image to the user
        await context.bot.send_photo(
            chat_id=user_id,
            photo=PAYMENT_QR_FILE_ID,
            caption=f"✅ You selected {context.user_data['game']} - {plan_name}.\n\nPlease scan the QR code to pay, then send the payment screenshot here."
        )

    # ... (rest of the callback handling remains the same)
    elif data.startswith("acc_"):
        _, uid, game, plan = data.split("_")
        key = approve_and_assign_key(int(uid), game, plan)
        if key:
            await context.bot.send_message(int(uid), f"✅ Payment Accepted!\n\n🔑 Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_text(f"✅ Key delivered: {key}")
        else: await query.edit_message_text("❌ Out of stock!")

    elif data.startswith("rej_"):
        await context.bot.send_message(data.split("_")[1], "❌ Your payment was rejected.")
        await query.edit_message_text("❌ Rejected.")

# ... (rest of your handler setup)
