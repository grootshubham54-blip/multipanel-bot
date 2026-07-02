from telegram import ReplyKeyboardMarkup

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["📦 Stock"],
        ["🎮 Games"],
        ["🛠 Admin Panel"]
    ], resize_keyboard=True)


def admin_game_selection_keyboard():
    return ReplyKeyboardMarkup([
        ["👑 KING iOS", "WINIOS"],
        ["NEXT IOS", "𝐌𝐚𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐫"],
        ["𝘿𝙀𝘼𝘿𝙀𝙀𝙀𝙔𝙀", "DOLPHIN IOS"],
        ["🔙 Back"]
    ], resize_keyboard=True)


def admin_plan_selection_keyboard():
    return ReplyKeyboardMarkup([
        ["1 Day"],
        ["1 Week"],
        ["1 Month"],
        ["🔙 Back"]
    ], resize_keyboard=True)