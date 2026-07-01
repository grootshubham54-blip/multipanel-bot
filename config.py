import os

# BOT_TOKEN should remain as a string
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ADMIN_ID is cast to an integer to ensure comparison with user.id works perfectly.
# A default value (your ID) is provided as a fallback if the environment variable is missing.
ADMIN_ID = int(os.getenv("ADMIN_ID", 7908981593))
