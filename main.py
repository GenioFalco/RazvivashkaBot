import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import (
    common, achievements, daily_tasks,
    riddles, exercises, puzzles, tongue_twisters,
    creativity, subscriptions, parents, admin
)
from database.database import Database
from aiogram.enums import ParseMode
from os import getenv
from dotenv import load_dotenv
from logger import get_logger

# Получаем логгер для main
logger = get_logger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Инициализируем бота
bot = Bot(token=getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем все роутеры
dp.include_router(common.router)
dp.include_router(achievements.router)
dp.include_router(daily_tasks.router)
dp.include_router(riddles.router)
dp.include_router(exercises.router)
dp.include_router(puzzles.router)
dp.include_router(tongue_twisters.router)
dp.include_router(creativity.router)
dp.include_router(subscriptions.router)
dp.include_router(parents.router)
dp.include_router(admin.router)

async def main():
    # Инициализируем базу данных
    logger.info("Инициализация базы данных...")
    db = Database()
    await db.create_tables()
    await db.initialize_videos()
    await db.initialize_subscriptions()  # Инициализируем базовые подписки
    logger.info("База данных инициализирована успешно")
    
    # Запускаем бота
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        logger.info("Запуск приложения...")
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Критическая ошибка при запуске приложения: {e}")
        raise 