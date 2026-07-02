import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}
}
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if update.effective_user.id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # 1. स्क्रीनशॉट हैंडलिंग (Validation के साथ)
    if update.message.photo and user_id != ADMIN_ID:
        last_game = context.user_data.get("last_game")
        last_plan = context.user_data.get("last_plan")
        
        if not last_game or not last_plan:
            await update.message.reply_text("⚠️ कृपया पहले गेम और प्लान चुनें।")
            return

        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
            caption=f"👤 Payment from {user_id}\n🎮 Game: {REV_GAME_MAP.get(last_game)}\n📦 Plan: {REV_PLAN_MAP.get(last_plan)}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{last_game}_{last_plan}")], [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ स्क्रीनशॉट मिल गया! एडमिन चेक कर रहे हैं।")
        return

    # 2. अन्य लॉजिक (Text handling)
    text = update.message.text
    if text == "🎮 Games": await update.message.reply_text("Choose game:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{GAME_MAP[text]}_{PLAN_MAP[p]}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text("Select plan:", reply_markup=InlineKeyboardMarkup(kb))
    # ... बाकी का Admin/User लॉजिक ...

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # CRITICAL: Loading spinner हटाने के लिए
    data = query.data
    
    if data.startswith("plan_"):
        _, g, p = data.split("_")
        context.user_data.update({"last_game": g, "last_plan": p})
        if os.path.exists("qr.JPG"):
            with open("qr.JPG", "rb") as qr: await query.message.reply_photo(qr, caption="👉 Pay and send screenshot.")
        else: await query.message.reply_text("⚠️ QR file missing.")
    elif data.startswith("acc_"):
        _, uid, g, p = data.split("_")
        key = approve_and_assign_key(int(uid), REV_GAME_MAP[g], REV_PLAN_MAP[p])
        if key: await context.bot.send_message(int(uid), f"✅ Key: `{key}`", parse_mode="Markdown")
        else: await query.message.reply_text("❌ Stock finished!")
        await query.edit_message_caption(caption="✅ Approved.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # CRITICAL: filters.ALL की जगह सही filters
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
