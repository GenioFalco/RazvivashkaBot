import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from handlers import common, achievements
from database.database import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация роутеров
dp.include_router(common.router)
dp.include_router(achievements.router)

async def main():
    """Основная функция запуска бота"""
    # Инициализация базы данных
    db = Database()
    await db.create_tables()
    
    # Удаляем все обновления, которые произошли после последнего выключения бота
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        # Запускаем бота
        await dp.start_polling(bot)
    finally:
        # Закрываем сессию бота при завершении работы
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main()) 