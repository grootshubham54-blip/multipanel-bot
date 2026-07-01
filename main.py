import os
import telebot

# बोट टोकन लोड करना
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7908981593 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot is online! Send a screenshot for approval.")

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    file_id = message.photo[-1].file_id
    user_id = message.chat.id
    
    # एडमिन को फोटो और बटन भेजना
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Accept", callback_data=f"acc_{user_id}"),
        telebot.types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
    )
    
    bot.send_photo(ADMIN_ID, file_id, caption=f"New Payment from {user_id}", reply_markup=markup)
    bot.reply_to(message, "Screenshot sent to Admin.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.data.split("_")[1]
    if "acc" in call.data:
        bot.send_message(user_id, "✅ Payment Accepted!")
        bot.edit_message_caption("✅ Accepted", call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(user_id, "❌ Payment Rejected!")
        bot.edit_message_caption("❌ Rejected", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
