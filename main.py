import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_user_keys, get_stock_count, get_total_users, get_all_keys_report, save_user

# Setup
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593

# Game Configuration
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "130", "1 Week": "599"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# --- Keyboards ---
def main_keyboard(user_id):
    kb = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID: kb.append(["🛠 Admin Panel"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([["🔑 Add Keys", "📊 Stock"], ["📜 Key Report", "👥 Total Users"], ["🔙 Back"]], resize_keyboard=True)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username) # Save user to DB
    context.user_data.clear()
    await update.message.reply_text("👋 स्वागत है! गेम चुनें या पेमेंट चेक करें।", reply_markup=main_keyboard(user.id))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game
        kb = [[InlineKeyboardButton(p, callback_data=f"plan_{p}")] for p in GAME_PLANS[game].keys()]
        await query.edit_message_text(f"🎮 {game} चुना। अब प्लान चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data.startswith("plan_"):
        plan = data.split("_")[1]
        context.user_data["plan"] = plan
        await query.edit_message_text(f"✅ आपने {context.user_data['game']} का {plan} चुना है।\n\nकृपया अब पेमेंट का स्क्रीनशॉट भेजें।")

    elif data.startswith("acc_"):
        _, uid, game, plan = data.split("_")
        # Direct call to your database function
        key = approve_and_assign_key(int(uid), game, plan)
        
        if key:
            await context.bot.send_message(int(uid), f"✅ पेमेंट स्वीकार हो गई!\n\n🔑 आपकी की: `{key}`", parse_mode="Markdown")
            await query.edit_message_text(f"✅ की (Key) सफलतापूर्वक भेज दी गई है।\n\nKey: {key}")
        else:
            await query.edit_message_text("❌ स्टॉक खत्म हो गया है! की उपलब्ध नहीं है।")

    elif data.startswith("rej_"):
        uid = data.split("_")[1]
        await context.bot.send_message(int(uid), "❌ आपकी पेमेंट अस्वीकार (Reject) कर दी गई है।")
        await query.edit_message_text("❌ पेमेंट रिजेक्ट कर दी गई।")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get("state")

    # --- ADMIN LOGIC ---
    if user_id == ADMIN_ID:
        if text == "🔙 Back":
            context.user_data.clear()
            await update.message.reply_text("Back to Menu:", reply_markup=main_keyboard(user_id))
            return
        
        # Admin Add Keys State Machine
        if state == "add_keys":
            for k in text.split("\n"):
                if k.strip(): 
                    save_key(context.user_data["add_game"], context.user_data["add_plan"], k.strip())
            await update.message.reply_text("✅ सारी कीज सेव हो गई हैं!", reply_markup=admin_keyboard())
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

        # Main Admin Menu
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
            return

    # --- USER LOGIC ---
    if text == "🎮 Games":
        kb = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in GAME_PLANS.keys()]
        await update.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif text == "🔑 My Keys":
        keys = get_user_keys(user_id)
        if keys:
            msg = "🔑 *Your Keys:*\n\n"
            for g, p, k in keys: msg += f"🎮 {g} ({p}): `{k}`\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("No keys found!")
            
    elif update.message.photo and "plan" in context.user_data:
        g, p = context.user_data["game"], context.user_data["plan"]
        kb = [[InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}_{g}_{p}"), InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")]]
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=f"Payment from {user_id}\nGame: {g}\nPlan: {p}", reply_markup=InlineKeyboardMarkup(kb))
        await update.message.reply_text("✅ स्क्रीनशॉट एडमिन को भेज दिया गया है!")

if __name__ == '__main__':
    create_tables() # Initialize Database
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.run_polling()
