import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_user_keys, get_stock_count, get_total_users, get_all_keys_report

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

def main_keyboard(user_id):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📜 Key Report", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True)

async def start(update, context):
    context.user_data.clear()
    await update.message.reply_text("👋 Welcome!", reply_markup=main_keyboard(update.effective_user.id))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    # एडमिन कीज जोड़ने का लॉजिक
    if user_id == ADMIN_ID:
        if text == "🔙 Back":
            context.user_data.clear()
            await update.message.reply_text("Back to Menu:", reply_markup=main_keyboard(user_id))
            return

        if state == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved Successfully!", reply_markup=admin_keyboard())
            context.user_data.clear()
            return

        if state == "select_plan":
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text(f"Selected: {text}\nअब कीज पेस्ट करें (एक लाइन में एक):", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
            return

        if state == "select_game":
            context.user_data["add_game"] = text
            context.user_data["state"] = "select_plan"
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([[p] for p in GAME_PLANS[text].keys()] + [["🔙 Back"]], resize_keyboard=True))
            return

        # मेनू ऑप्शंस
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()] + [["🔙 Back"]], resize_keyboard=True))
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total users: {get_total_users()}")
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n\n"
            for g, plans in GAME_PLANS.items():
                msg += f"*{g}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(g, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "📜 Key Report":
            report = "📜 *Key Report:*\n\n"
            for g, p, k, used, uid in get_all_keys_report():
                report += f"🎮 {g} | {p} | {'✅ Sold' if used else '🟢 Avail'}\n🔑 `{k}`\n\n"
            await update.message.reply_text(report, parse_mode="Markdown")

    # यूजर लॉजिक
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]) if keys else "No keys found!")
    elif update.message.photo and user_id != ADMIN_ID:
        # पेमेंट हैंडलिंग
        g, p = context.user_data.get("game", "N/A"), context.user_data.get("plan", "N/A")
        kb = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(kb))
        await update.message.reply_text("✅ Screenshot sent!")

# बटन हैंडलर... (बाकी कोड समान रहेगा)
