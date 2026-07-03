import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_user_keys, get_stock_count, get_total_users, get_all_keys_report, get_all_user_ids # ध्यान दें: database.py में get_all_user_ids फंक्शन होना चाहिए

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📜 Key Report", "👥 Total Users"], ["📢 Broadcast", "🔙 Back"]], resize_keyboard=True)

async def start(update, context):
    user_id = update.effective_user.id
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel": await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
        elif text == "📢 Broadcast":
            context.user_data["state"] = "broadcast_msg"
            await update.message.reply_text("Please enter the message you want to broadcast:", reply_markup=ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True))
            return
        elif context.user_data.get("state") == "broadcast_msg":
            if text == "🔙 Back":
                context.user_data.clear()
                await start(update, context)
                return
            # Broadcast Logic
            users = get_all_user_ids()
            count = 0
            for uid in users:
                try:
                    await context.bot.send_message(uid, text)
                    count += 1
                except: pass
            await update.message.reply_text(f"✅ Broadcast sent to {count} users!", reply_markup=admin_keyboard())
            context.user_data.clear()
            return
        
        elif text == "👥 Total Users": await update.message.reply_text(f"👥 Total users: {get_total_users()}")
        elif text == "📜 Key Report":
            report = "📜 *Status Report:*\n\n"
            for g, p, k, used, uid in get_all_keys_report():
                status = "✅ Sold" if used == 1 else "🟢 Available"
                report += f"🎮 {g} | {p}\n🔑 `{k}` | {status}\n\n"
            await update.message.reply_text(report, parse_mode="Markdown")
        elif text == "📊 Stock":
            msg = "📊 *Current Stock:*\n\n"
            for g, plans in GAME_PLANS.items():
                msg += f"*{g}:*\n"
                for p in plans: msg += f"  - {p}: {get_stock_count(g, p)} keys\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "select_game"
            await update.message.reply_text("Select Game:", reply_markup=ReplyKeyboardMarkup([[g] for g in GAME_PLANS.keys()], resize_keyboard=True))
        elif context.user_data.get("state") == "select_game":
            context.user_data["add_game"] = text
            context.user_data["state"] = "select_plan"
            await update.message.reply_text("Select Plan:", reply_markup=ReplyKeyboardMarkup([[p] for p in GAME_PLANS[text].keys()], resize_keyboard=True))
        elif context.user_data.get("state") == "select_plan":
            context.user_data["add_plan"] = text
            context.user_data["state"] = "add_keys"
            await update.message.reply_text("Enter keys (one per line):")
        elif context.user_data.get("state") == "add_keys":
            for k in text.split("\n"):
                if k.strip(): save_key(context.user_data["add_game"], k.strip(), context.user_data["add_plan"])
            await update.message.reply_text("✅ Keys Saved!", reply_markup=admin_keyboard())
            context.user_data.clear()
        elif text == "🔙 Back":
            context.user_data.clear()
            await start(update, context)
            return

    # User Logic
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if not keys: await update.message.reply_text("No keys found!")
        else: await update.message.reply_text("\n".join([f"{g} ({p}): {k}" for g, p, k in keys]))
    elif text == "📞 Support":
        await update.message.reply_text(f"📞 Contact Support: {SUPPORT_USERNAME}")
    elif text == "💳 Payment":
        await update.message.reply_text(f"💳 Payment Details:\n{PAYMENT_DETAILS}")
    elif update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("game", "N/A")
        p = context.user_data.get("plan", "N/A")
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, 
                                     caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", 
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}")]]))
        await update.message.reply_text("✅ Screenshot sent!")

# ... (बाकी button_click और main फंक्शन वही रहेंगे)
