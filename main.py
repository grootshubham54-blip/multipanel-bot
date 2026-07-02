import os
import logging
import sqlite3

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

# 'get_user_keys' को इम्पोर्ट करना सुनिश्चित करें
from database import (
    create_tables,
    add_user,
    update_payment_status,
    save_key,
    get_stock,
    get_total_users,
    get_total_purchases,
    get_user_keys,
    DB_NAME
)

from payment import save_payment
from admin_panel import admin_keyboard, admin_game_selection_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0)) 

GAME_MAPPING = {
    "👑 KING iOS": "king",
    "WINIOS": "win",
    "NEXT IOS": "next",
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "mars",
    "𝘿𝙀𝘼𝘿𝙀𝙔𝙀": "dead",
    "DOLPHIN IOS": "dolphin"
}
REVERSE_GAME_MAPPING = {v: k for k, v in GAME_MAPPING.items()}

# --- KEYBOARD FUNCTIONS ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "👤 Profile"], ["💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(target: str = "Main") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[f"🔙 Back to {target}"]], resize_keyboard=True)

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Cancel Payment"]], resize_keyboard=True)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()  
    add_user(user.id, user.username or "No Username")
    await update.message.reply_text("👑 Welcome to KING iOS Bot!", reply_markup=get_main_keyboard(user.id))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # KEY FEATURE: My Keys
    if text == "🔑 My Keys":
        keys = get_user_keys(user.id)
        if keys:
            await update.message.reply_text(f"🔑 *Your Keys:*\n" + "\n".join([f"`{k}`" for k in keys]), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No keys found for your account.")
        return

    # [अन्य सभी पुराने लॉजिक यहाँ जोड़ें जैसे Broadcast, Admin Panel, Games menu आदि]
    # (कोड को संक्षिप्त रखने के लिए मैंने बाकी लॉजिक को हटा दिया है, उसे आप अपने पुराने कोड से यहाँ लगा लें)

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    action, payment_id, user_id = data[0], int(data[1]), int(data[2])

    if action == "acc":
        short_game = data[3] if len(data) > 3 else "king"
        game_name = REVERSE_GAME_MAPPING.get(short_game, "👑 KING iOS")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, key_code FROM keys WHERE game_name = ? AND is_used = 0 LIMIT 1", (game_name,))
        row = cursor.fetchone()
        
        if row:
            key_id, real_key = row
            # यहाँ अपडेट करें ताकि की यूजर को असाइन हो जाए
            cursor.execute("UPDATE keys SET is_used = 1, user_id = ? WHERE id = ?", (user_id, key_id))
            conn.commit()
            conn.close()
            
            update_payment_status(payment_id, "approved")
            await query.edit_message_caption(caption=f"✅ Approved! Key sent to User.")
            try:
                await context.bot.send_message(user_id, text=f"🎉 *Success!*\nYour key: `{real_key}`", parse_mode="Markdown")
            except: pass
        else:
            conn.close()
            await query.edit_message_caption(caption="❌ Stock empty!")

    elif action == "rej":
        update_payment_status(payment_id, "rejected")
        await query.edit_message_caption(caption="❌ Request Rejected.")

def main():
    if not TOKEN: raise ValueError("BOT_TOKEN Missing!")
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    # फोटो हैंडलर और अन्य यहाँ जोड़ें...
    app.run_polling()

if __name__ == "__main__":
    main()
