from loguru import logger
import sys
import os

# Создаем директорию для логов, если её нет
if not os.path.exists("logs"):
    os.makedirs("logs")

# Настраиваем логирование
logger.remove()  # Удаляем стандартный обработчик
logger.add(
    "logs/razvivashka_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    rotation="1 day",
    compression="zip"
)
logger.add(sys.stderr, level="INFO")  # Добавляем вывод в консоль

def get_logger(name):
    """Возвращает логгер с указанным именем."""
    return logger.bind(name=name) 