import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = "YOUR_BOT_TOKEN_HERE" # यहाँ अपना टोकन डालें
ADMIN_ID = 7908981593
PAYMENT_QR_FILE_ID = "YOUR_PHOTO_FILE_ID" # अपने QR की फाइल आईडी डालें

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

def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📜 Key Report", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True)

async def start(update, context):
    save_user(update.effective_user.id, update.effective_user.username)
    await update.message.reply_text("👋 स्वागत है! गेम चुनें:", reply_markup=main_keyboard(update.effective_user.id))

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game
        msg = f"🎮 {game} चुना।\n\n*उपलब्ध प्लान और स्टॉक:*\n"
        kb = []
        for p, price in GAME_PLANS[game].items():
            stock = get_stock_count(game, p)
            msg += f"- {p} ({price}₹): {'✅' if stock > 0 else '❌'} ({stock} उपलब्ध)\n"
            if stock > 0: kb.append([InlineKeyboardButton(f"{p} ({price}₹)", callback_data=f"plan_{p}")])
        
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb) if kb else None)

    elif data.startswith("plan_"):
        context.user_data["plan"] = data.split("_")[1]
        await context.bot.send_photo(user_id, photo=PAYMENT_QR_FILE_ID, caption="✅ QR पर पेमेंट करें और स्क्रीनशॉट भेजें।")

    elif data.startswith("acc_"):
        _, uid, game, plan = data.split("_")
        key = approve_and_assign_key(int(uid), game, plan)
        if key:
            await context.bot.send_message(int(uid), f"✅ पेमेंट स्वीकार! आपकी की: `{key}`", parse_mode="Markdown")
            await query.edit_message_text(f"✅ की भेज दी गई है: {key}")
        else: await query.edit_message_text("❌ स्टॉक खत्म हो गया!")

    elif data.startswith("rej_"):
        await context.bot.send_message(data.split("_")[1], "❌ पेमेंट रिजेक्ट कर दी गई।")
        await query.edit_message_text("❌ रिजेक्टेड।")

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # एडमिन लॉजिक (सा संक्षिप्त किया है)
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            await update.message.reply_text("गेम चुनें:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()], resize_keyboard=True))
        elif text in GAME_PLANS:
            context.user_data["add_game"] = text
            await update.message.reply_text("प्लान चुनें:", reply_markup=ReplyKeyboardMarkup([[p] for p in GAME_PLANS[text].keys()], resize_keyboard=True))
        elif text in [p for sub in [plans.keys() for plans in GAME_PLANS.values()] for p in sub]:
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text("कीज पेस्ट करें (एक लाइन में एक):")
            return
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"): save_key(context.user_data["add_game"], context.user_data["add_plan"], k.strip())
            await update.message.reply_text("✅ कीज सेव हो गई!", reply_markup=admin_keyboard())
            context.user_data.clear()
            return
        elif text == "📊 Stock":
            msg = "📊 स्टॉक:\n"
            for g, plans in GAME_PLANS.items():
                for p in plans: msg += f"{g} - {p}: {get_stock_count(g, p)}\n"
            await update.message.reply_text(msg)

    # यूजर लॉजिक
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("गेम चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    elif update.message.photo and "plan" in context.user_data:
        g, p = context.user_data["game"], context.user_data["plan"]
        kb = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\n{g} | {p}", reply_markup=InlineKeyboardMarkup(kb))
        await update.message.reply_text("✅ स्क्रीनशॉट भेज दिया गया है।")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
app.run_polling()
