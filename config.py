from os import getenv
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен бота
BOT_TOKEN = getenv("BOT_TOKEN")

# ID администраторов (список)
ADMIN_IDS = [int(id.strip()) for id in getenv("ADMIN_IDS", "").split(",") if id.strip()]

# ID канала для фотографий
PHOTO_CHANNEL_ID = getenv("PHOTO_CHANNEL_ID") 