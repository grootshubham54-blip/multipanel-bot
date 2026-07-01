import os
import logging
from telebot import TeleBot, types
from telebot.util import quick_markup

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variables from Railway environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
# आपकी कन्फर्म की हुई एडमिन आईडी (7908981593)
ADMIN_ID = int(os.getenv("ADMIN_ID", "7908981593"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")

bot = TeleBot(BOT_TOKEN)

# डमी डेटाबेस लॉजिक - ताकि आपका बाकी का कोड बिना एरर के चले
def save_payment(user_id, plan_name, amount, file_id):
    # डेटाबेस करप्शन से बचने के लिए सीधे एक फेक पेमेंट आईडी रिटर्न कर रहे हैं
    return "PAY12345"

def add_key_to_db(game_name, key_string):
    return True

# --- बोट कमांड्स ---

@bot.message_list_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    
    # मुख्य मेनू बटन्स
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🎮 Games"), types.KeyboardButton("🔑 My Keys"))
    markup.row(types.KeyboardButton("📞 Support"), types.KeyboardButton("👤 Profile"))
    markup.row(types.KeyboardButton("💳 Payment"))
    
    # अगर आप (मालिक) स्टार्ट करते हैं, तो आपको एडमिन पैनल का बटन भी दिखेगा
    if user_id == ADMIN_ID:
        markup.row(types.KeyboardButton("⚙️ Admin Panel"))
        
    bot.send_message(user_id, "👋 Welcome to IOS SHUBHAM BOT! Choose an option below:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🎮 Games")
def show_games(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 KING iOS", callback_data="game_king_ios"))
    bot.send_message(message.chat.id, "🎯 Select the game you want to buy keys for:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "game_king_ios")
def show_plans(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 KING iOS 1 DAY - ₹200", callback_data="buy_king_1day"))
    bot.edit_message_text("🛒 Select your preferred plan:",
