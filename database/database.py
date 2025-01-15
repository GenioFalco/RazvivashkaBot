import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict
from config import config
import re

class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path

    async def create_tables(self):
        """Создание необходимых таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создание таблицы пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создание таблицы достижений
            await db.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    token_id INTEGER,
                    count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (token_id) REFERENCES tokens (id)
                )
            ''')

            # Создание таблицы токенов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emoji TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')

            # Инициализация токенов, если таблица пуста
            async with db.execute('SELECT COUNT(*) FROM tokens') as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    default_tokens = [
                        ("🔑", "Ключ доступа", "Даётся за ежедневный вход"),
                        ("⭐", "Звезда дня", "Даётся за выполнение заданий на день"),
                        ("🧩", "Мастер ребусов", "Даётся за выполнение ребусов"),
                        ("👄", "Говорун", "Даётся за выполнение скороговорок"),
                        ("🧠", "Умник", "Даётся за выполнение нейрогимнастики"),
                        ("🤸", "Гимнаст", "Даётся за выполнение артикулярной гимнастики"),
                        ("❓", "Мудрец", "Даётся за выполнение загадок"),
                        ("🏆", "Чемпион дня", "Даётся за выполнение всех заданий на день")
                    ]
                    await db.executemany(
                        'INSERT INTO tokens (emoji, name, description) VALUES (?, ?, ?)',
                        default_tokens
                    )
            await db.commit()

    async def get_all_tokens(self) -> List[Dict]:
        """Получение списка всех токенов"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT * FROM tokens') as cursor:
                tokens = await cursor.fetchall()
                return [{
                    'id': token[0],
                    'emoji': token[1],
                    'name': token[2],
                    'description': token[3]
                } for token in tokens]

    async def update_token(self, token_id: int, emoji: str, name: str) -> bool:
        """Обновление токена"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE tokens SET emoji = ?, name = ? WHERE id = ?',
                    (emoji, name, token_id)
                )
                await db.commit()
                return True
        except Exception:
            return False

    @staticmethod
    def is_valid_emoji(text: str) -> bool:
        """Проверка, является ли текст эмодзи"""
        # Простая проверка на эмодзи (может потребоваться улучшение)
        return len(text) == 1 and ord(text) > 1000

    @staticmethod
    def is_valid_name(text: str) -> bool:
        """Проверка валидности названия токена"""
        return bool(re.match(r'^[а-яА-Яa-zA-Z\s]+$', text))

    async def add_user(self, telegram_id: int, username: Optional[str], full_name: str) -> bool:
        """Добавление нового пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR IGNORE INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)',
                    (telegram_id, username, full_name)
                )
                await db.commit()
                return True
        except Exception:
            return False

    async def get_user(self, telegram_id: int) -> Optional[dict]:
        """Получение информации о пользователе"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM users WHERE telegram_id = ?',
                (telegram_id,)
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'telegram_id': result[1],
                        'username': result[2],
                        'full_name': result[3],
                        'registration_date': result[4]
                    }
                return None

    async def get_all_users(self) -> List[dict]:
        """Получение списка всех пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT * FROM users') as cursor:
                users = await cursor.fetchall()
                return [{
                    'id': user[0],
                    'telegram_id': user[1],
                    'username': user[2],
                    'full_name': user[3],
                    'registration_date': user[4]
                } for user in users]

    async def get_user_achievements(self, user_id: int) -> Dict[int, int]:
        """Получение количества всех жетонов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем записи достижений для пользователя, если их нет
            tokens = await self.get_all_tokens()
            for token in tokens:
                await db.execute('''
                    INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                    VALUES (?, ?, 0)
                ''', (user_id, token['id']))
            await db.commit()

            # Получаем количество жетонов
            async with db.execute('''
                SELECT token_id, count FROM achievements
                WHERE user_id = ?
            ''', (user_id,)) as cursor:
                achievements = await cursor.fetchall()
                return {ach[0]: ach[1] for ach in achievements} 