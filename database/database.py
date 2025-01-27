import aiosqlite
from logger import get_logger

logger = get_logger(__name__)

class Database:
    def __init__(self, db_name="razvivashka.db"):
        self.db_name = db_name
        
    async def create_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
            logger.info("Таблицы созданы успешно")
            
    async def initialize_videos(self):
        # Здесь будет инициализация видео
        pass
        
    async def initialize_subscriptions(self):
        # Здесь будет инициализация подписок
        pass 