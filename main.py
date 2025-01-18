import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from handlers import (
    common, achievements, daily_tasks,
    riddles, exercises, puzzles, tongue_twisters
)

async def main():
    # Включаем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Создаем объекты бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    dp.include_router(common.router)
    dp.include_router(achievements.router)
    dp.include_router(daily_tasks.router)
    dp.include_router(riddles.router)
    dp.include_router(exercises.router)
    dp.include_router(puzzles.router)
    dp.include_router(tongue_twisters.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 