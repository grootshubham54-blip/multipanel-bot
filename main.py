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
    markup.add(types.InlineKeyboardButton("👑 KING iOS",
