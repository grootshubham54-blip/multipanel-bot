import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
from database import create_tables, approve_and_assign_key, get_stock_count, get_total_users, add_user
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

# आपका पुराना गेम प्लान स्ट्रक्चर (बिल्कुल वैसा ही है)
GAME_PLANS = {
    "👑 KING iOS": ["1 Day", "1 Week", "1 Month"],
    "WINIOS": ["1 Day", "1 Week", "1 Month"],
    "NEXT IOS": ["1 Day", "1 Week", "1 Month"],
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": ["1 Day", "1 Week", "1 Month"],
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": ["1 Day", "1 Week", "1 Month"],
    "DOLPHIN IOS": ["1 Day", "1 Week", "1 Month"]
}

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # पुरानी फंक्शनैलिटी बरकरार (Admin & User flow)
    if update.message.photo and user_id != ADMIN_ID:
        game = context.user_data.get("last_game", "Unknown")
        plan = context.user_data.get("last_plan", "Unknown")
        
        # FIX 1: CALLBACK LIMIT फिक्स करने के लिए डेटा को context में स्टोर किया
        context.user_data[f"pay_{user_id}"] = {"game": game, "plan": plan}
        callback_data = f"acc_{user_id}" 
        
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
            caption=f"Payment from {user_id}\nGame: {game}\nPlan: {plan}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=callback_data)]]))
        await update.message.reply_text("✅ Screenshot sent!")
        return

    # बाकी का पुराना लॉजिक वैसे ही रहने दिया है
    if text == "🎮 Games":
        await update.message.reply_text("Select game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        context.user_data["last_game"] = text
        await update.message.reply_text("Select plan:", reply_markup=admin_plan_selection_keyboard())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # FIX 2: Loading spinner हटाने के लिए जरूरी
    await query.answer() 
    data = query.data
    
    if data.startswith("acc_"):
        # FIX 3: डेटा state से उठाएं (Callback Limit Fix)
        uid = int(data.split("_")[1])
        pay_info = context.user_data.get(f"pay_{uid}")
        
        if pay_info:
            key = approve_and_assign_key(uid, pay_info["game"], pay_info["plan"])
            if key:
                # FIX 4: Markdown का उपयोग करके की (Key) को साफ़ दिखाना
                await context.bot.send_message(uid, f"✅ Approved! Key: `{key}`", parse_mode="Markdown")
                await query.edit_message_caption(caption="✅ Approved.")
            else:
                await query.edit_message_caption(caption="❌ No keys available.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
