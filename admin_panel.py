from telegram import ReplyKeyboardMarkup

def admin_keyboard():
    # नाम बिल्कुल वही रखें जो main.py में if-elif में हैं
    keyboard = [["🔑 Add Keys", "📦 Stock"], ["👥 Total Users", "🔙 Back to Admin"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_game_selection_keyboard():
    games = [["👑 KING iOS", "WINIOS"], ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"], ["𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀"], ["🔙 Back to Admin"]]
    return ReplyKeyboardMarkup(games, resize_keyboard=True)
