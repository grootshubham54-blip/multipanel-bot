import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}
}
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username or "User")
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if str(update.effective_user.id) == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 वेलकम! मैं आपकी क्या मदद कर सकता हूँ?", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    # 1. पेमेंट स्क्रीनशॉट हैंडलिंग (अगर फोटो है और एडमिन नहीं है)
    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "Game")
        p = context.user_data.get("u_plan", "Plan")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
            caption=f"👤 पेमेंट फ्रॉम: {user_id}\n🎮 गेम: {g}\n📦 प्लान: {p}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{GAME_MAP.get(g,'KING')}_{PLAN_MAP.get(p,'1D')}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]))
        await update.message.reply_text("✅ स्क्रीनशॉट मिल गया! एडमिन चेक कर रहे हैं।")
        return

    # 2. यूनिवर्सल बटन्स (जो हर जगह काम करेंगे)
    if text == "🎮 Games": await update.message.reply_text("गेम चुनें:", reply_markup=admin_game_selection_keyboard())
    elif text == "🔑 My Keys":
        keys = get_user_keys(update.effective_user.id)
        msg = "🔑 **आपकी Keys:**\n" + "\n".join([f"🎮 {k[0]}: `{k[2]}`" for k in keys]) if keys else "❌ कोई की नहीं है।"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text in ["📞 Support", "💳 Payment"]: await update.message.reply_text("📞 एडमिन से संपर्क करें: @IOS_HACK_S")
    
    # 3. गेम सिलेक्शन (प्राइस के साथ)
    elif text in GAME_PLANS:
        context.user_data["u_game"] = text
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"plan_{p}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 प्लान चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    
    # 4. एडमिन पैनल लॉजिक
    elif user_id == ADMIN_ID and text in ["🛠 Admin Panel", "🔙 Back to Admin", "🔙 Back to Main"]:
        await update.message.reply_text("🛠 एडमिन पैनल:", reply_markup=admin_keyboard())
    elif user_id == ADMIN_ID and text == "🔑 Add Keys":
        context.user_data["state"] = "awaiting_game"
        await update.message.reply_text("गेम चुनें:", reply_markup=admin_game_selection_keyboard())
    else: await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("plan_"):
        context.user_data["u_plan"] = data.split("_")[1]
        with open("qr.JPG", "rb") as qr: await query.message.reply_photo(qr, caption="👉 QR पर पेमेंट करें और स्क्रीनशॉट भेजें।")
    elif data.startswith("acc_"):
        parts = data.split("_")
        key = approve_and_assign_key(int(parts[1]), REV_GAME_MAP.get(parts[2]), parts[3])
        await context.bot.send_message(parts[1], f"✅ पेमेंट कन्फर्म! आपकी की: `{key}`") if key else None
        await query.edit_message_caption(caption="✅ पेमेंट स्वीकार की गई।")
    elif data.startswith("rej_"):
        await context.bot.send_message(data.split("_")[1], "❌ पेमेंट रिजेक्टेड।")
        await query.edit_message_caption(caption="❌ रिजेक्टेड।")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
