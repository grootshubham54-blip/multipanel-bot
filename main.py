import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

# डेटा मैपिंग
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(update.effective_user.id) == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 वेलकम! कैसे मदद करूँ?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # 1. स्क्रीनशॉट हैंडलिंग (ये पार्ट सबसे ज़रूरी है)
    if update.message.photo and str(user_id) != ADMIN_ID:
        g = context.user_data.get("u_game", "Unknown")
        p = context.user_data.get("u_plan", "Unknown")
        # एडमिन को फोटो और एक्सेप्ट/रिजेक्ट बटन भेजना
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"👤 यूजर: {update.effective_user.full_name}\n🆔 ID: {user_id}\n🎮 गेम: {g}\n📦 प्लान: {p}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]
            ])
        )
        await update.message.reply_text("✅ स्क्रीनशॉट मिल गया! एडमिन जल्द ही चेक करेंगे।")
        return

    text = update.message.text
    # ... (बाकी आपके बटन्स का लॉजिक यहाँ रहेगा) ...
    if text == "🎮 Games":
        await update.message.reply_text("गेम चुनें:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_MAP:
        context.user_data.update({"u_game": text})
        await update.message.reply_text("प्लान चुनें...")
    # ... 

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("acc_"):
        parts = data.split("_")
        uid = parts[1]
        # पेमेंट कन्फर्म और की (Key) भेजना
        key = approve_and_assign_key(int(uid), parts[2], parts[3])
        if key:
            await context.bot.send_message(int(uid), f"✅ पेमेंट एक्सेप्टेड! आपकी की (Key) है: `{key}`")
            await query.edit_message_caption(caption="✅ पेमेंट स्वीकार की गई और की भेज दी गई।")
        else:
            await query.edit_message_caption(caption="⚠️ एरर: स्टॉक खत्म है।")
            
    elif data.startswith("rej_"):
        uid = data.split("_")[1]
        await context.bot.send_message(int(uid), "❌ आपकी पेमेंट रिजेक्ट कर दी गई है।")
        await query.edit_message_caption(caption="❌ पेमेंट रिजेक्टेड।")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
