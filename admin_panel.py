from telegram import ReplyKeyboardMarkup, KeyboardButton

def admin_keyboard():
    keyboard = [
        ["🔑 Add Keys", "📦 Stock"],
        ["👥 Total Users", "🔙 Back to Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_game_selection_keyboard():
    # आपके main.py में मौजूद गेम्स के अनुसार
    games = [["👑 KING iOS", "WINIOS"], ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"], ["𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀", "DOLPHIN IOS"], ["🔙 Back to Admin"]]
    return ReplyKeyboardMarkup(games, resize_keyboard=True)

def admin_plan_selection_keyboard():
    plans = [["1 Day", "1 Week", "1 Month"], ["🔙 Back to Admin"]]
    return ReplyKeyboardMarkup(plans, resize_keyboard=True)
