import aiosqlite
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
from config import config
import re
import random

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
                    FOREIGN KEY (token_id) REFERENCES tokens (id),
                    UNIQUE(user_id, token_id)
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

            # Создание таблицы ежедневных заданий
            await db.execute('''
                CREATE TABLE IF NOT EXISTS daily_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_text TEXT NOT NULL
                )
            ''')

            # Создание таблицы для отслеживания выполненных заданий
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_daily_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task_id INTEGER,
                    completed BOOLEAN DEFAULT FALSE,
                    date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (task_id) REFERENCES daily_tasks (id)
                )
            ''')

            # Добавляем начальные задания, если таблица пуста
            async with db.execute('SELECT COUNT(*) FROM daily_tasks') as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    default_tasks = [
                        ("Сделай аппликацию из веток",),
                        ("Нарисуй свою любимую игрушку",),
                        ("Сделай зарядку вместе с родителями",),
                        ("Спой свою любимую песенку",),
                        ("Собери пазл",),
                        ("Построй домик из подушек",),
                        ("Нарисуй радугу",),
                        ("Сделай открытку для друга",),
                        ("Покорми птичек",),
                        ("Помоги маме полить цветы",)
                    ]
                    await db.executemany(
                        'INSERT INTO daily_tasks (task_text) VALUES (?)',
                        default_tasks
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

    async def update_token(self, token_id: int, new_emoji: str, new_name: str) -> bool:
        """Обновление токена"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE tokens SET emoji = ?, name = ? WHERE id = ?',
                    (new_emoji, new_name, token_id)
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

    async def get_user_daily_tasks(self, user_id: int) -> Tuple[List[Dict], int]:
        """Получает задания пользователя на сегодня и количество выполненных"""
        today = date.today()
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, есть ли у пользователя задания на сегодня
            async with db.execute('''
                SELECT COUNT(*) FROM user_daily_tasks 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today)) as cursor:
                count = await cursor.fetchone()
                
            if count[0] == 0:
                # Проверяем, достаточно ли заданий в базе данных
                async with db.execute('SELECT COUNT(*) FROM daily_tasks') as cursor:
                    total_tasks = (await cursor.fetchone())[0]
                    if total_tasks < 5:
                        return [], 0  # Возвращаем пустой список, если заданий недостаточно
                
                # Выбираем 5 случайных заданий
                async with db.execute('SELECT id, task_text FROM daily_tasks') as cursor:
                    all_tasks = await cursor.fetchall()
                    selected_tasks = random.sample(all_tasks, 5)
                    
                # Добавляем задания пользователю
                for task in selected_tasks:
                    await db.execute('''
                        INSERT INTO user_daily_tasks (user_id, task_id, date)
                        VALUES (?, ?, ?)
                    ''', (user_id, task[0], today))
                await db.commit()
            
            # Получаем текущие задания пользователя
            async with db.execute('''
                SELECT dt.id, dt.task_text, udt.completed 
                FROM daily_tasks dt
                JOIN user_daily_tasks udt ON dt.id = udt.task_id
                WHERE udt.user_id = ? AND udt.date = ?
            ''', (user_id, today)) as cursor:
                tasks = await cursor.fetchall()
                tasks_list = [{
                    'id': task[0],
                    'text': task[1],
                    'completed': bool(task[2])
                } for task in tasks]
                completed_count = sum(1 for task in tasks_list if task['completed'])
                
                return tasks_list, completed_count

    async def get_token_count(self, user_id: int, token_id: int) -> int:
        """Получает количество определенных токенов у пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT count FROM achievements
                WHERE user_id = ? AND token_id = ?
            ''', (user_id, token_id)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

    async def debug_achievements(self, user_id: int):
        """Отладочный метод для проверки таблицы achievements"""
        async with aiosqlite.connect(self.db_path) as db:
            print("\nDebug achievements table:")
            async with db.execute('''
                SELECT a.user_id, a.token_id, a.count, t.name
                FROM achievements a
                JOIN tokens t ON a.token_id = t.id
                WHERE a.user_id = ?
            ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    print(f"User {row[0]}, Token {row[1]} ({row[3]}): {row[2]} шт.")
            
            print("\nDebug user_daily_tasks table:")
            today = date.today()
            async with db.execute('''
                SELECT task_id, completed
                FROM user_daily_tasks
                WHERE user_id = ? AND date = ?
            ''', (user_id, today)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    print(f"Task {row[0]}: {'Completed' if row[1] else 'Not completed'}")

    async def complete_daily_task(self, user_id: int, task_id: int) -> bool:
        """Отмечает задание как выполненное и начисляет токен"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                today = date.today()
                
                # Проверяем, не было ли задание уже выполнено
                async with db.execute('''
                    SELECT completed FROM user_daily_tasks
                    WHERE user_id = ? AND task_id = ? AND date = ?
                ''', (user_id, task_id, today)) as cursor:
                    result = await cursor.fetchone()
                    if result and result[0]:
                        return False  # Задание уже выполнено
                
                # Отмечаем задание как выполненное
                await db.execute('''
                    UPDATE user_daily_tasks 
                    SET completed = TRUE 
                    WHERE user_id = ? AND task_id = ? AND date = ?
                ''', (user_id, task_id, today))
                
                # Проверяем существование записи в achievements для токена "Звезда дня"
                await db.execute('''
                    INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                    VALUES (?, 2, 0)
                ''', (user_id,))
                
                # Увеличиваем количество токенов за выполнение задания
                await db.execute('''
                    UPDATE achievements 
                    SET count = count + 1,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND token_id = 2
                ''', (user_id,))
                
                # Проверяем, все ли задания выполнены
                async with db.execute('''
                    SELECT COUNT(*) FROM user_daily_tasks
                    WHERE user_id = ? AND date = ? AND completed = TRUE
                ''', (user_id, today)) as cursor:
                    completed_count = (await cursor.fetchone())[0]
                    
                # Если выполнены все 5 заданий, начисляем дополнительный токен
                if completed_count == 5:
                    # Проверяем существование записи для токена "Чемпион дня"
                    await db.execute('''
                        INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                        VALUES (?, 8, 0)
                    ''', (user_id,))
                    
                    await db.execute('''
                        UPDATE achievements 
                        SET count = count + 1,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND token_id = 8
                    ''', (user_id,))
                
                await db.commit()
                print(f"Completing task {task_id} for user {user_id}")
                print(f"Task completion success: True")
                print(f"Completed tasks count: {completed_count}")
                return True
        except Exception as e:
            print(f"Error in complete_daily_task: {e}")
            return False 

    async def get_token_by_id(self, token_id: int) -> dict:
        """Получает информацию о токене по его id."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tokens WHERE id = ?",
                (token_id,)
            ) as cursor:
                token = await cursor.fetchone()
                if token:
                    return dict(token)
                return None 

    async def add_achievement(self, user_id: int, token_id: int) -> bool:
        """Добавляет достижение пользователю."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, есть ли уже такое достижение
                async with db.execute(
                    "SELECT count FROM achievements WHERE user_id = ? AND token_id = ?",
                    (user_id, token_id)
                ) as cursor:
                    result = await cursor.fetchone()
                    
                if result:
                    # Если достижение существует, увеличиваем счетчик
                    await db.execute(
                        "UPDATE achievements SET count = count + 1 WHERE user_id = ? AND token_id = ?",
                        (user_id, token_id)
                    )
                else:
                    # Если достижения нет, создаем новое
                    await db.execute(
                        "INSERT INTO achievements (user_id, token_id, count) VALUES (?, ?, 1)",
                        (user_id, token_id)
                    )
                await db.commit()
                return True
        except Exception as e:
            print(f"Error in add_achievement: {e}")
            return False 

    async def get_random_token(self) -> dict:
        """Возвращает случайный токен из базы данных."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM tokens WHERE id != 8 ORDER BY RANDOM() LIMIT 1"
                ) as cursor:
                    token = await cursor.fetchone()
                    if token:
                        return dict(token)
                    return None
        except Exception as e:
            print(f"Error in get_random_token: {e}")
            return None 