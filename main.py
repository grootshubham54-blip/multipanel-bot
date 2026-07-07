import os, logging, asyncio, uuid
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import *

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_ID = 7908981593 
SUPPORT_USERNAME = "@IOS_HACK_S" 
PAYMENT_DETAILS = "UPI ID: yourname@upi"

is_bot_active = True 

GAME_PLANS = {
    "👑 ✦ 𝕂𝕀ℕ𝔾 𝕚𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "2000"},
    "⭐️ ✦ 𝕎𝕀ℕ𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1399"},
    "🚀 ✦ ℕ𝔼𝕏𝕋 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800"},
    "🪐 ✦ 𝕄𝕒𝕣𝕤 𝕃𝕠𝕒𝕕𝕖𝕣 ✦": {"1 Day": "130", "1 Week": "599"},
    "💀 ✦ 𝔻𝔼𝔸𝔻𝔼𝕐𝔼 ✦": {"1 Day": "200", "1 Week": "600", "1 Month": "1600"},
    "🐬 ✦ 𝔻𝕆𝕃ℙℍ𝕀ℕ 𝕀𝕆𝕊 ✦": {"1 Day": "200", "1 Week": "800", "1 Month": "1499"}
}

# --- नया फंक्शन: ऑर्डर एक्सपायरी का काम ---
async def auto_cancel_order(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id, message_id = job.data
    try:
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, 
                                             caption="❌ Order Expired! Please try again.")
    except: pass

# --- अपडेटेड Button Click (Order System Logic) ---
async def button_click(update, context):
    query = update.callback_query; await query.answer()
    
    if query.data.startswith("game_"):
        game = query.data.split("_")[1]; context.user_data["game"] = game
        kb = [[InlineKeyboardButton(f"{p} - ₹{pr}", callback_data=f"pay_{p}_{pr}")] for p, pr in GAME_PLANS[game].items()]
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_games")])
        await query.edit_message_text(f"🎮 *{game}*\nSelect your plan:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif query.data.startswith("pay_"):
        data = query.data.split("_"); plan, price = data[1], data[2]
        game = context.user_data.get("game")
        order_id = str(uuid.uuid4())[:12] # यूनिक ID
        
        caption = (f"Order Created!\n\n🆔 Order ID: {order_id}\n🎮 Item: {game} - {plan}\n"
                   f"💰 Amount: ₹{price}\n\n⚠️ Valid for 5 mins.\n1. Pay to QR.\n2. Click 'Verify Payment'.")
        
        kb = [[InlineKeyboardButton("✅ Verify Payment", callback_data=f"verify_{order_id}")],
              [InlineKeyboardButton("🚫 Cancel Order", callback_data=f"cancel_{order_id}")]]
        
        # QR भेजें
        msg = await query.message.reply_photo(photo=open("qr.JPG", "rb"), caption=caption, reply_markup=InlineKeyboardMarkup(kb))
        
        # 5 मिनट का टाइमर सेट करें
        context.job_queue.run_once(auto_cancel_order, 300, data=(query.message.chat_id, msg.message_id))

    elif query.data.startswith("verify_"):
        await query.message.reply_text("✅ Please send the payment screenshot now to verify.")

    elif query.data.startswith("cancel_"):
        await query.edit_message_caption(caption="🚫 Order Cancelled.")

    # [बाकी का पुराना Logic acc_ और rej_ वाला यहाँ जोड़ें]
    elif query.data.startswith(("acc_", "rej_")):
        # (आपका मौजूदा कोड यहाँ रखें)
        pass

# बाकी फंक्शन्स (start, message_handler, main आदि) आपके पुराने कोड जैसे ही रहेंगे।
# बस `main()` में `app.job_queue` का उपयोग सुनिश्चित करें।
