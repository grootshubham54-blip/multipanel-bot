from telegram import ReplyKeyboardMarkup

def admin_keyboard():
    keyboard = [
        ["🔑 Add Keys", "📦 Stock"],
        ["👥 Total Users", "🔙 Back to Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_game_selection_keyboard():
    # यहाँ वही नाम रखें जो main.py की GAME_PLANS डिक्शनरी में हैं
    games = [
        ["👑 KING iOS", "WINIOS"], 
        ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"], 
        ["𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀"], 
        ["🔙 Back to Admin"]
    ]
    return ReplyKeyboardMarkup(games, resize_keyboard=True)

def admin_plan_selection_keyboard():
    plans = [["1 Day", "1 Week", "1 Month"], ["🔙 Back to Admin"]]
    return ReplyKeyboardMarkup(plans, resize_keyboard=True)
