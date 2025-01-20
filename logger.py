import sys
from loguru import logger
import os

# Создаем директорию для логов, если её нет
if not os.path.exists("logs"):
    os.makedirs("logs")

# Удаляем стандартный обработчик
logger.remove()

# Добавляем обработчик для вывода в консоль
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Добавляем обработчик для записи в файл
logger.add(
    "logs/razvivashka_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",  # Новый файл каждый день
    retention="30 days",  # Хранить логи за последние 30 дней
    compression="zip"  # Сжимать старые логи
)

# Функция для получения логгера
def get_logger(name):
    return logger.bind(name=name) 