import os
import telebot
from telebot import types

# 1. वेरिएबल्स सेटअप
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593  # आपकी कन्फर्म की हुई एडमिन आईडी

bot = telebot.TeleBot(BOT_TOKEN)

# डमी डेटाबेस फंक्शन ताकि आपका पुराना स्ट्रक्चर न टूटे
def save_payment(user_id, plan_name, amount, file_id):
    return "PAY12345"

# 2. स्टार्ट कमांड और मुख्य मेनू
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🎮 Games"), types.KeyboardButton("🔑 My Keys"))
    markup.row(types.KeyboardButton("📞 Support"), types.KeyboardButton("👤 Profile"))
    markup.row(types.KeyboardButton("💳 Payment"))
    
    if user_id == ADMIN_ID:
        markup.row(types.KeyboardButton("⚙️ Admin Panel"))
        
    bot.send_message(user_id, "👋 Welcome to IOS SHUBHAM BOT!", reply_markup=markup)

# 3. बटन रिस्पॉन्स (Games & Plans)
@bot.message_handler(func=lambda message: message.text == "🎮 Games")
def show_games(message):
    markup = types.InlineKeyboardMarkup()
    # यहाँ ब्रैकेट एरर को बिल्कुल फिक्स कर दिया गया है
    markup.add(types.InlineKeyboardButton("👑 KING iOS", callback_data="game_king_ios"))
    bot.send_message(message.chat.id, "🎯 Select the game you want to buy keys for:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "game_king_ios")
def show_plans(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 KING iOS 1 DAY - ₹200", callback_data="buy_king_1day"))
    bot.edit_message_text("🛒 Select your preferred plan:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "buy_king_1day")
def send_payment_details(call):
    text = (
        "💳 **Payment Details**\n\n"
        "👑 **Plan:** KING iOS 1 DAY\n"
        "💰 **Amount:** ₹200\n\n"
        "1. Scan the QR Code or send money via UPI.\n"
        "2. 📸 **Next Step:** Send the payment success screenshot directly into this chat now."
    )
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

# 4. स्क्रीनशॉट रिसीव करना और एडमिन को फॉरवर्ड करना
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = message.chat.id
    file_id = message.photo[-1].file_id
    
    # यूजर को तुरंत जवाब
    bot.send_message(user_id, "⏳ Your screenshot has been sent to the Admin for approval. Please wait...")
    
    # एडमिन के लिए Accept / Reject बटन बनाना
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_approve = types.InlineKeyboardButton("✅ Accept", callback_data=f"approve_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    admin_markup.add(btn_approve, btn_reject)
    
    # सीधे आपकी एडमिन
