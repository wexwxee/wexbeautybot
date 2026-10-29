import os

# Токен берётся только из переменной окружения (Railway → Variables, локально — export BOT_TOKEN=...)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан: добавь его в переменные окружения")

ADMIN_ID = int(os.environ.get("ADMIN_ID", "5842837744"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003853097806"))
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/wexbeauty")
SCHEDULE_CHANNEL_ID = int(os.environ.get("SCHEDULE_CHANNEL_ID", "-1003853097806"))

DEFAULT_TIME_SLOTS = [
    "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00",
    "17:00", "18:00", "19:00"
]

DB_PATH = os.environ.get("DB_PATH", "manicure.db")
TIMEZONE = "Europe/Copenhagen"
