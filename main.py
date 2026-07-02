import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, add_user, get_user_keys

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

async def start(update, context):
    user_id = update.effective_user.id
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    # एडमिन फ्लो
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel":
            # यहाँ मैंने 'Stock' बटन जोड़ दिया है
            kb = [["🔑 Add Keys", "📊 Stock"], ["🔙 Back"]]
            await update.message.reply_text("Admin Panel:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        
        elif text == "📊 Stock":
            # यह आपके डेटाबेस से स्टॉक की जानकारी दिखाएगा
            stock_info = "📦 Current Stock:\n\n"
            for game in GAME_PLANS:
                # यहाँ आप get_user_keys या जो भी फंक्शन आपके स्टॉक के लिए है वो यूज़ कर सकते हैं
                stock_info += f"{game}: Available\n"
            await update.message.reply_text(stock_info)

        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            kb = [[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]]
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        
        # ... (बाकी एडमिन लॉजिक वही है)
        elif text == "🔙 Back":
            context.user_data.clear()
            await start(update, context)

    # यूजर फ्लो
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
        context.user_data["last_game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{game}_{p}")] for p, pr in GAME_PLANS[game].items()]
        await query.message.reply_text(f"Select Plan for {game}:", reply_markup=InlineKeyboardMarkup(kb))
        
    elif query.data.startswith("pay_"):
        parts = query.data.split("_")
        context.user_data["last_plan"] = parts[2]
        try:
            with open("qr.JPG", "rb") as qr:
                await query.message.reply_photo(photo=qr, caption="Pay and send screenshot.")
        except:
            await query.message.reply_text("⚠️ QR file not found!")
            
    elif query.data.startswith("acc_"):
        user_id = int(query.data.split("_")[1])
        g = context.user_data.get("last_game", "KING")
        p = context.user_data.get("last_plan", "1 Day")
        key = approve_and_assign_key(user_id, g, p) 
        
        if key:
            await context.bot.send_message(user_id, f"✅ Key: `{key}`", parse_mode="Markdown")
            await query.edit_message_caption(f"✅ Approved! Key: {key}")
        else:
            await query.edit_message_caption(f"⚠️ Error: No keys in stock for {g} - {p}!")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
