import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import create_tables, save_key, approve_and_assign_key, get_stock_count, get_total_users, add_user, get_user_keys
from admin_panel import admin_keyboard, admin_game_selection_keyboard, admin_plan_selection_keyboard

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7908981593"

# आपकी ओरिजिनल गेम्स और प्राइसिंग लिस्ट
GAME_PLANS = {
    "👑 KING iOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "WINIOS": {"1 Day": "199", "1 Week": "600", "1 Month": "1299"},
    "NEXT IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "𝘿𝙀𝘼𝘿𝙀𝙀𝙔𝙀": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "DOLPHIN IOS": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"}
}

# Callback Data को छोटा रखने के लिए मैपिंग (64-byte limit)
GAME_MAP = {"👑 KING iOS": "KING", "WINIOS": "WIN", "NEXT IOS": "NEXT", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫": "MARS", "𝘿𝙀𝘼𝘿𝙀𝙀𝙔𝙀": "DEAD", "DOLPHIN IOS": "DOLP"}
REV_GAME_MAP = {v: k for k, v in GAME_MAP.items()}
PLAN_MAP = {"1 Day": "1D", "1 Week": "1W", "1 Month": "1M"}
REV_PLAN_MAP = {"1D": "1 Day", "1W": "1 Week", "1M": "1 Month"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "No Username"
    add_user(update.effective_user.id, username)
    
    keyboard = [["🎮 Games", "🔑 My Keys"], ["📞 Support", "💳 Payment"]]
    if user_id == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel"])
        
    await update.message.reply_text("👋 Welcome!", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    state = context.user_data.get("state")

    # 1. कस्टमर अगर फोटो (स्क्रीनशॉट) भेजता है
    if update.message.photo and user_id != ADMIN_ID:
        g = context.user_data.get("u_game", "👑 KING iOS")
        p = context.user_data.get("u_plan", "1 Day")
        
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id, 
            caption=f"👤 Payment Screenshot From User: {user_id}\n🎮 Game: {g}\n📦 Plan: {p}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Accept & Send Key", callback_data=f"acc_{user_id}_{GAME_MAP[g]}_{PLAN_MAP[p]}")],
                [InlineKeyboardButton("❌ Reject Payment", callback_data=f"rej_{user_id}")]
            ])
        )
        await update.message.reply_text("✅ आपका स्क्रीनशॉट एडमिन को भेज दिया गया है। वेरिफिकेशन के बाद की (Key) अपने आप मिल जाएगी।")
        return

    # 2. एडमिन का 'Add Keys' स्टेप-बाय-स्टेप फ्लो
    if user_id == ADMIN_ID and state:
        if text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
            return
            
        if state == "awaiting_game":
            if text in GAME_PLANS:
                context.user_data["add_game"] = text
                context.user_data["state"] = "awaiting_plan"
                await update.message.reply_text(f"🎮 Selected: {text}\nअब इस गेम का प्लान चुनें:", reply_markup=admin_plan_selection_keyboard())
            return
            
        elif state == "awaiting_plan":
            clean_plan = text.replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "").strip()
            if clean_plan in ["1 Day", "1 Week", "1 Month"]:
                context.user_data["add_plan"] = clean_plan
                context.user_data["state"] = "awaiting_keys"
                await update.message.reply_text(f"📝 {context.user_data['add_game']} ({clean_plan}) के लिए Keys पेस्ट करें (एक लाइन में एक ही Key डालें):")
            return
            
        elif state == "awaiting_keys":
            keys = [k.strip() for k in text.split("\n") if k.strip()]
            g_name = context.user_data["add_game"]
            p_name = context.user_data["add_plan"]
            for key in keys:
                save_key(g_name, key, p_name)
            context.user_data.clear()
            await update.message.reply_text(f"✅ {len(keys)} Keys सफलतापूर्वक {g_name} [{p_name}] में सेव कर दी गई हैं!", reply_markup=admin_keyboard())
            return

    # 3. एडमिन मुख्य बटन्स लॉजिक
    if user_id == ADMIN_ID:
        if text == "🛠 Admin Panel" or text == "🔙 Back to Admin":
            context.user_data.clear()
            await update.message.reply_text("🛠 Admin Panel:", reply_markup=admin_keyboard())
            return
        elif text == "🔑 Add Keys":
            context.user_data["state"] = "awaiting_game"
            await update.message.reply_text("🎮 उस गेम को चुनें जिसकी Keys आप जोड़ना चाहते हैं:", reply_markup=admin_game_selection_keyboard())
            return
        elif text == "📦 Stock":
            msg = "📦 **Current Live Stock:**\n\n"
            for g in GAME_PLANS:
                msg += f"🔹 {g}:\n"
                for p in GAME_PLANS[g]:
                    msg += f"  - {p}: {get_stock_count(g, p)} left\n"
            await update.message.reply_text(msg)
            return
        elif text == "👥 Total Users":
            await update.message.reply_text(f"👥 Total registered users: {get_total_users()}")
            return
        elif text == "🔙 Back to Main":
            await start(update, context)
            return

    # 4. कस्टमर मुख्य बटन्स लॉजिक
    if text == "🎮 Games":
        await update.message.reply_text("गेम चुनें जिसका प्लान आप खरीदना चाहते हैं:", reply_markup=admin_game_selection_keyboard())
    elif text in GAME_PLANS:
        # यहाँ कस्टमर को प्राइसिंग के साथ Inline Keyboard शो होगा!
        keyboard = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{GAME_MAP[text]}_{PLAN_MAP[p]}_{pr}")] for p, pr in GAME_PLANS[text].items()]
        await update.message.reply_text(f"🎮 {text} का प्लान चुनें:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == "🔑 My Keys":
        my_keys = get_user_keys(update.effective_user.id)
        if my_keys:
            msg = "🔑 **Your Keys:**\n\n"
            for gk, pk, kcode in my_keys:
                msg += f"🎮 {gk} ({pk}): `{kcode}`\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ आपने अभी तक कोई Key नहीं खरीदी है।")
    elif text == "🔙 Back to Main":
        await start(update, context)
    elif text == "📞 Support":
        await update.message.reply_text("📞 सहायता के लिए एडमिन से संपर्क करें: @IOS_HACK_S")
    elif text == "💳 Payment":
        await update.message.reply_text("💳 पेमेंट करने के लिए पहले '🎮 Games' बटन दबाएं और अपना पसंदीदा प्लान चुनें।")
    else:
        await start(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # कस्टमर द्वारा प्लान चुनने पर QR कोड दिखाना
    if data.startswith("pay_"):
        _, g_short, p_short, price = data.split("_")
        game = REV_GAME_MAP[g_short]
        plan = REV_PLAN_MAP[p_short]
        context.user_data["u_game"] = game
        context.user_data["u_plan"] = plan
        
        with open("qr.JPG", "rb") as qr:
            await query.message.reply_photo(
                photo=qr, 
                caption=f"✅ आपने चुना: {game} ({plan})\n\n💰 अमाउंट: ₹{price}\n\n👉 ऊपर दिए गए QR कोड पर पेमेंट करें और उसका **स्क्रीनशॉट यहाँ चैट में भेजें**।"
            )
            
    # एडमिन द्वारा पेमेंट स्वीकार करने पर (Auto Key Delivery)
    elif data.startswith("acc_"):
        _, uid, g_short, p_short = data.split("_")
        game = REV_GAME_MAP[g_short]
        plan = REV_PLAN_MAP[p_short]
        
        key = approve_and_assign_key(int(uid), game, plan)
        if key:
            await context.bot.send_message(
                chat_id=int(uid), 
                text=f"✅ आपका पेमेंट स्वीकार कर लिया गया है!\n\n🎮 गेम: {game}\n📦 प्लान: {plan}\n🔑 आपकी Key: `{key}`\n\nइसे कॉपी करने के लिए टैप करें।"
            )
            await query.edit_message_caption(caption=f"✅ Approved! Key sent to user {uid} for {game} ({plan}).")
        else:
            await query.edit_message_caption(caption=f"⚠️ Error: {game} ({plan}) का स्टॉक खत्म हो गया है! पहले 'Add Keys' करें।")
            
    # एडमिन द्वारा पेमेंट रिजेक्ट करने पर
    elif data.startswith("rej_"):
        uid = data.split("_")[1]
        await context.bot.send_message(
            chat_id=int(uid), 
            text="❌ आपका पेमेंट रिकॉर्ड रिजेक्ट कर दिया गया है।\n\nअगर आपको लगता है कि यह गलती से हुआ है, तो कृपया एडमिन से संपर्क करें: @IOS_HACK_S"
        )
        await query.edit_message_caption(caption=f"❌ Rejected for user {uid}.")

def main():
    create_tables()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot is successfully running...")
    app.run_polling()

if __name__ == "__main__":
    main()
