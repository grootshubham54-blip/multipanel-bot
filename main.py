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
    
    # सीधे आपकी एडमिन आईडी पर फोटो भेजना
    try:
        bot.send_photo(
            ADMIN_ID, 
            file_id, 
            caption=f"🔔 **New Payment Received!**\n\n👤 User ID: `{user_id}`\n🎮 Plan: KING iOS 1 DAY\n💰 Amount: ₹200",
            parse_mode="Markdown",
            reply_markup=admin_markup
        )
    except Exception as e:
        print(f"Error sending to admin: {e}")

# 5. एडमिन बटन एक्शन (Approve / Reject)
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_admin_buttons(call):
    action, customer_id = call.data.split('_')
    customer_id = int(customer_id)
    
    if action == 'approve':
        bot.send_message(customer_id, "✅ Your payment has been approved! Here is your license key: `REPLACE-WITH-KEY-STOCK`")
        bot.edit_message_caption("✅ This payment was APPROVED by you.", call.message.chat.id, call.message.message_id)
    elif action == 'reject':
        bot.send_message(customer_id, "❌ Your payment screenshot was rejected by the admin. Please contact support.")
        bot.edit_message_caption("❌ This payment was REJECTED by you.", call.message.chat.id, call.message.message_id)

# 6. पुराना एडमिन पैनल स्ट्रक्चर
@bot.message_handler(func=lambda message: message.text == "⚙️ Admin Panel" and message.chat.id == ADMIN_ID)
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("➕ Add Key"), types.KeyboardButton("📦 Stock"))
    markup.row(types.KeyboardButton("Back to Main"))
    bot.send_message(ADMIN_ID, "👑 Admin Control Panel opened:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Back to Main")
def back_to_main(message):
    start_command(message)

# बोट पोलिंग स्टार्ट
if __name__ == '__main__':
    print("🚀 Bot running...")
    bot.infinity_polling()
