from dataclasses import dataclass, field
from os import getenv
from dotenv import load_dotenv
from typing import List

load_dotenv()

@dataclass
class Config:
    """Конфигурация бота"""
    BOT_TOKEN: str = getenv("BOT_TOKEN")
    ADMIN_IDS: List[int] = field(default_factory=lambda: [int(id.strip()) for id in getenv("ADMIN_IDS", "").split(",") if id.strip()])
    DATABASE_PATH: str = "database/razvivashka.db"

config = Config() 