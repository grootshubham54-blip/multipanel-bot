import os, logging, uuid
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

is_bot_active = True 

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

async def start(update, context):
    user = update.effective_user
    await update.message.reply_text("Welcome to IOS SHUBHAM Store! Use the menu below.")

async def message_handler(update, context):
    text = update.message.text
    if text == "🔙 Back": await start(update, context)

async def auto_cancel_order(context: ContextTypes.DEFAULT_TYPE):
    chat_id, message_id = context.job.data
    try: await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption="❌ Order Expired!")
    except: pass

async def button_click(update, context):
    query = update.callback_query; await query.answer()
    
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}_{game}")] for p, pr in GAME_PLANS[game].items()]
        await query.edit_message_text(f"🎮 {game}\nSelect plan:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif query.data.startswith("pay_"):
        data = query.data.split("_"); plan, price, game = data[1], data[2], data[3]
        order_id = str(uuid.uuid4())[:8]
        msg = await query.message.reply_photo(photo=open("qr.JPG", "rb"), caption=f"Order: {game} ({plan})\nAmount: ₹{price}\nOrder ID: {order_id}\n\n1. Pay & 2. Verify", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Verify Payment", callback_data=f"ver_{order_id}_{game}_{plan}")],
            [InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]
        ]))
        context.job_queue.run_once(auto_cancel_order, 300, data=(query.message.chat_id, msg.message_id))
    
    elif query.data.startswith("ver_"):
        await query.message.reply_text("Please send screenshot for verification.")
    
    elif query.data == "cancel": await query.message.delete()

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
