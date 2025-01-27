import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
from dotenv import load_dotenv
from logger import get_logger

# Получаем логгер для main
logger = get_logger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Инициализируем бота
bot = Bot(token=getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        logger.info("Запуск приложения...")
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Критическая ошибка при запуске приложения: {e}")
        raise 