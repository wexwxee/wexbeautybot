import os

# Токен берётся из переменной окружения Railway (или напрямую для локального запуска)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8408390967:AAERpuaN2by1V6PunW-w0xdQCWnQsVdAxUI")

ADMIN_ID = 5842837744
CHANNEL_ID = -1003853097806
CHANNEL_LINK = "https://t.me/wexbeauty"
SCHEDULE_CHANNEL_ID = -1003853097806

DEFAULT_TIME_SLOTS = [
    "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00",
    "17:00", "18:00", "19:00"
]

DB_PATH = os.environ.get("DB_PATH", "manicure.db")
TIMEZONE = "Europe/Copenhagen"
