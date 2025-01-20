import aiosqlite
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple
from config import config
import re
import random
import asyncio
import logging
import os
import tempfile

class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self.temp_dir = tempfile.mkdtemp()  # Создаем временную директорию

    async def initialize_videos(self):
        """Инициализирует видео для упражнений и творчества"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем наличие видео в таблице
            cursor = await db.execute('SELECT COUNT(*) FROM creativity_videos')
            count = (await cursor.fetchone())[0]
            
            # Добавляем видео только если таблица пуста
            if count == 0:
                # Добавляем видео для творчества
                creativity_videos = [
                    (
                        "drawing",
                        "Рисуем цветок",
                        "Научимся рисовать красивый цветок простым карандашом",
                        "https://drive.google.com/file/d/18LJeTjNnUTVV2jQIApkSgDlJL_FC95um/view?usp=sharing",
                        1
                    ),
                    (
                        "paper",
                        "Оригами лебедь",
                        "Создаем изящного лебедя в технике оригами",
                        "https://drive.google.com/file/d/1XnvBN3xpaWDlMzR8cmf-SPXJTUVdVcMJ/view?usp=sharing",
                        1
                    ),
                    (
                        "sculpting",
                        "Лепим котика",
                        "Учимся лепить милого котика из пластилина",
                        "https://drive.google.com/file/d/1Cal7FTL6zlu55W_mBYkrCFhQmRDh47xv/view?usp=sharing",
                        1
                    )
                ]
                
                await db.executemany('''
                    INSERT INTO creativity_videos 
                    (type, title, description, video_url, sequence_number)
                    VALUES (?, ?, ?, ?, ?)
                ''', creativity_videos)
                
                await db.commit()

    async def create_tables(self):
        """Создает необходимые таблицы в базе данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем таблицу для токенов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY,
                    emoji TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')
            
            # Создаем таблицу для пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    join_date TEXT DEFAULT (date('now'))
                )
            ''')
            
            # Создаем таблицу для достижений пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_id INTEGER,
                    token_id INTEGER,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, token_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (token_id) REFERENCES tokens (id)
                )
            ''')
            
            # Создаем таблицу для ежедневных заданий
            await db.execute('''
                CREATE TABLE IF NOT EXISTS daily_tasks (
                    id INTEGER PRIMARY KEY,
                    text TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')
            
            # Создаем таблицу для выполненных ежедневных заданий
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_daily_tasks (
                    user_id INTEGER,
                    task_id INTEGER,
                    completion_date DATE,
                    PRIMARY KEY (user_id, task_id, completion_date),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (task_id) REFERENCES daily_tasks (id)
                )
            ''')
            
            # Создаем таблицу для загадок
            await db.execute('''
                CREATE TABLE IF NOT EXISTS riddles (
                    id INTEGER PRIMARY KEY,
                    text TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            ''')
            
            # Создаем таблицу для решенных загадок
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_riddles (
                    user_id INTEGER,
                    riddle_id INTEGER,
                    completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, riddle_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (riddle_id) REFERENCES riddles (id)
                )
            ''')
            
            # Создаем таблицу для видео упражнений
            await db.execute('''
                CREATE TABLE IF NOT EXISTS exercise_videos (
                    id INTEGER PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    video_url TEXT NOT NULL
                )
            ''')
            
            # Создаем таблицу для просмотренных видео
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_exercise_views (
                    user_id INTEGER,
                    video_id INTEGER,
                    view_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, video_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (video_id) REFERENCES exercise_videos (id)
                )
            ''')
            
            # Создаем таблицу для видео творчества
            await db.execute('''
                CREATE TABLE IF NOT EXISTS creativity_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    video_url TEXT NOT NULL,
                    sequence_number INTEGER
                )
            ''')
            
            # Создаем таблицу для выполненных творческих заданий
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_creativity_completions (
                    user_id INTEGER,
                    video_id INTEGER,
                    completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, video_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (video_id) REFERENCES creativity_videos (id)
                )
            ''')
            
            # Добавляем токен "Алмаз" если его нет
            await db.execute('''
                INSERT OR IGNORE INTO tokens (id, emoji, name, description)
                VALUES (9, "💎", "Алмаз", "Даётся за выполнение творческих мастер-классов")
            ''')
            
            # Создаем таблицу подписок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    duration_days INTEGER NOT NULL,
                    price REAL NOT NULL
                )
            """)
            
            # Создаем таблицу активных подписок пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    user_id INTEGER NOT NULL,
                    subscription_id INTEGER NOT NULL,
                    start_date TEXT NOT NULL DEFAULT (date('now')),
                    end_date TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id),
                    PRIMARY KEY (user_id, subscription_id)
                )
            """)
            
            # Создаем таблицу для отслеживания бесплатных попыток
            await db.execute("""
                CREATE TABLE IF NOT EXISTS free_attempts (
                    user_id INTEGER,
                    feature TEXT,
                    attempts INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, feature),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Создаем таблицу рефералов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    join_date TEXT NOT NULL DEFAULT (date('now')),
                    is_active BOOLEAN DEFAULT FALSE,
                    reward_claimed BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (referrer_id, referred_id),
                    FOREIGN KEY (referrer_id) REFERENCES users (id),
                    FOREIGN KEY (referred_id) REFERENCES users (id)
                )
            """)
            
            # Создаем таблицу puzzles для хранения изображений в двоичном формате
            await db.execute("""
                CREATE TABLE IF NOT EXISTS puzzles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_data BLOB NOT NULL,
                    answer1 TEXT NOT NULL,
                    answer2 TEXT NOT NULL,
                    answer3 TEXT NOT NULL
                )
            """)
            
            # Создаем таблицу для отслеживания прогресса пользователей в ребусах
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_puzzles (
                    user_id INTEGER,
                    puzzle_id INTEGER,
                    date DATE,
                    solved1 BOOLEAN DEFAULT FALSE,
                    solved2 BOOLEAN DEFAULT FALSE,
                    solved3 BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (user_id, puzzle_id, date),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (puzzle_id) REFERENCES puzzles (id)
                )
            """)
            
            await db.commit()

    async def initialize_subscriptions(self):
        """Инициализирует базовые подписки"""
        # Проверяем, есть ли уже тарифы
        async with aiosqlite.connect(self.db_path) as db:
            # Сначала удаляем все существующие тарифы
            await db.execute("DELETE FROM subscriptions")
            
            subscriptions = [
                {
                    'name': 'Месяц развития',
                    'description': '🌟 Полный доступ ко всем функциям на 30 дней',
                    'duration_days': 30,
                    'price': 299.0
                },
                {
                    'name': 'Квартал развития',
                    'description': '🌟 Полный доступ ко всем функциям на 90 дней\n💎 Скидка 20%',
                    'duration_days': 90,
                    'price': 719.0
                },
                {
                    'name': 'Полгода развития',
                    'description': '🌟 Полный доступ ко всем функциям на 180 дней\n💎 Скидка 30%',
                    'duration_days': 180,
                    'price': 1499.0
                },
                {
                    'name': 'Год развития',
                    'description': '🌟 Полный доступ ко всем функциям на 365 дней\n💎 Скидка 40%\n🎁 Бонусные материалы',
                    'duration_days': 365,
                    'price': 2149.0
                }
            ]
            
            for sub in subscriptions:
                await db.execute("""
                    INSERT INTO subscriptions (name, description, duration_days, price)
                    VALUES (?, ?, ?, ?)
                """, (sub['name'], sub['description'], sub['duration_days'], sub['price']))
            await db.commit()

    async def get_user_subscription(self, user_id: int) -> Optional[dict]:
        """Получает информацию об активной подписке пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT s.*, us.start_date, us.end_date
                FROM subscriptions s
                JOIN user_subscriptions us ON s.id = us.subscription_id
                WHERE us.user_id = ? AND us.is_active = TRUE
                AND date('now') <= date(us.end_date)
                ORDER BY us.end_date DESC
                LIMIT 1
            """, (user_id,))
            result = await cursor.fetchone()
            return dict(result) if result else None

    async def add_subscription(self, user_id: int, subscription_id: int) -> bool:
        """
        Добавляет или продлевает подписку пользователю
        
        Args:
            user_id (int): ID пользователя
            subscription_id (int): ID тарифа подписки
            
        Returns:
            bool: True если подписка успешно добавлена/продлена, False в случае ошибки
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Получаем информацию о тарифе
                cursor = await db.execute(
                    "SELECT duration_days FROM subscriptions WHERE id = ?",
                    (subscription_id,)
                )
                subscription = await cursor.fetchone()
                if not subscription:
                    return False
                
                duration_days = subscription[0]
                
                # Проверяем текущую подписку
                cursor = await db.execute(
                    "SELECT end_date FROM user_subscriptions WHERE user_id = ? AND is_active = TRUE",
                    (user_id,)
                )
                current_sub = await cursor.fetchone()
                
                if current_sub:
                    # Если есть активная подписка, продлеваем её
                    end_date = datetime.strptime(current_sub[0], '%Y-%m-%d')
                    new_end_date = end_date + timedelta(days=duration_days)
                else:
                    # Если нет активной подписки, создаём новую
                    new_end_date = datetime.now() + timedelta(days=duration_days)
                
                # Деактивируем старые подписки
                await db.execute(
                    "UPDATE user_subscriptions SET is_active = FALSE WHERE user_id = ?",
                    (user_id,)
                )
                
                # Добавляем новую подписку
                start_date = datetime.now().strftime('%Y-%m-%d')
                new_end_date_str = new_end_date.strftime('%Y-%m-%d')
                
                await db.execute("""
                    INSERT INTO user_subscriptions (user_id, subscription_id, start_date, end_date)
                    VALUES (?, ?, ?, ?)
                """, (user_id, subscription_id, start_date, new_end_date_str))
                
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding subscription: {e}")
            return False

    async def get_all_subscriptions(self) -> List[Dict]:
        """Получает список всех доступных подписок"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM subscriptions ORDER BY duration_days")
            return [dict(row) for row in await cursor.fetchall()]

    async def check_feature_access(self, user_id: int, feature_type: str) -> bool:
        """Проверяет доступ пользователя к функции"""
        # Сначала проверяем активную подписку
        subscription = await self.get_user_subscription(user_id)
        if subscription:
            return True

        # Если нет подписки, проверяем бесплатные попытки
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT attempts_used, last_attempt_date
                FROM free_attempts
                WHERE user_id = ? AND feature_type = ?
            """, (user_id, feature_type))
            result = await cursor.fetchone()

            # Для всех разделов кроме daily_tasks и drawing требуется подписка
            if feature_type not in ['daily_tasks', 'drawing']:
                return False

            if not result:
                # Первая попытка - разрешаем доступ
                return True

            attempts_used, last_attempt_date = result

            if feature_type == 'daily_tasks':
                # Проверяем, является ли это первым днем
                if last_attempt_date:
                    cursor = await db.execute("SELECT date('now')")
                    current_date = (await cursor.fetchone())[0]
                    if current_date == last_attempt_date:
                        return True  # Разрешаем доступ в течение первого дня
                    return False  # Блокируем доступ после первого дня
                return True  # Первый день - разрешаем доступ
            elif feature_type == 'drawing':
                # Для рисования разрешаем только один мастер-класс
                return attempts_used < 1

            return False

    async def increment_feature_attempt(self, user_id: int, feature_type: str) -> None:
        """Увеличивает счетчик использования функции"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO free_attempts (user_id, feature_type, attempts_used, last_attempt_date)
                VALUES (?, ?, 1, date('now'))
                ON CONFLICT (user_id, feature_type) DO UPDATE SET
                attempts_used = attempts_used + 1,
                last_attempt_date = date('now')
            """, (user_id, feature_type))
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
        max_retries = 3
        retry_delay = 0.1  # 100ms
        
        for attempt in range(max_retries):
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    # Создаем запись, если её нет
                    await db.execute('''
                        INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                        VALUES (?, ?, 0)
                    ''', (user_id, token_id))
                    
                    # Увеличиваем счетчик
                    await db.execute('''
                        UPDATE achievements 
                        SET count = count + 1,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND token_id = ?
                    ''', (user_id, token_id))
                    
                    await db.commit()
                    return True
            except Exception as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Database locked, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                print(f"Error in add_achievement: {e}")
                return False
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

    async def get_user_riddles(self, user_id: int) -> Tuple[List[Dict], int]:
        """Получает загадки пользователя на сегодня и количество разгаданных"""
        today = date.today()
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, есть ли у пользователя загадки на сегодня
            async with db.execute('''
                SELECT COUNT(*) FROM user_riddles 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today)) as cursor:
                count = await cursor.fetchone()
                
            if count[0] == 0:
                # Выбираем 5 случайных загадок
                async with db.execute('SELECT id, question, answer FROM riddles ORDER BY RANDOM() LIMIT 5') as cursor:
                    selected_riddles = await cursor.fetchall()
                    
                # Добавляем загадки пользователю
                for riddle in selected_riddles:
                    await db.execute('''
                        INSERT INTO user_riddles (user_id, riddle_id, date)
                        VALUES (?, ?, ?)
                    ''', (user_id, riddle[0], today))
                await db.commit()
            
            # Получаем текущие загадки пользователя
            async with db.execute('''
                SELECT r.id, r.question, r.answer, ur.completed 
                FROM riddles r
                JOIN user_riddles ur ON r.id = ur.riddle_id
                WHERE ur.user_id = ? AND ur.date = ?
                ORDER BY ur.id
            ''', (user_id, today)) as cursor:
                riddles = await cursor.fetchall()
                
            # Подсчитываем количество разгаданных загадок
            async with db.execute('''
                SELECT COUNT(*) FROM user_riddles
                WHERE user_id = ? AND date = ? AND completed = TRUE
            ''', (user_id, today)) as cursor:
                completed_count = (await cursor.fetchone())[0]
                
            return [{
                'id': riddle[0],
                'question': riddle[1],
                'answer': riddle[2],
                'completed': riddle[3]
            } for riddle in riddles], completed_count

    async def check_riddle_answer(self, user_id: int, riddle_id: int, answer: str) -> bool:
        """Проверяет ответ на загадку и отмечает её как разгаданную если ответ верный"""
        today = date.today()
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем правильный ответ
            async with db.execute('''
                SELECT r.answer FROM riddles r
                JOIN user_riddles ur ON r.id = ur.riddle_id
                WHERE ur.user_id = ? AND ur.riddle_id = ? AND ur.date = ?
            ''', (user_id, riddle_id, today)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    return False
                
                correct_answer = result[0].lower()
                user_answer = answer.lower()
                
                if correct_answer == user_answer:
                    # Отмечаем загадку как разгаданную
                    await db.execute('''
                        UPDATE user_riddles 
                        SET completed = TRUE
                        WHERE user_id = ? AND riddle_id = ? AND date = ?
                    ''', (user_id, riddle_id, today))
                    
                    # Создаем запись для токена "Мудрец" если её нет
                    await db.execute('''
                        INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                        VALUES (?, 7, 0)
                    ''', (user_id,))
                    
                    # Увеличиваем количество токенов за разгадку
                    await db.execute('''
                        UPDATE achievements 
                        SET count = count + 1,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND token_id = 7
                    ''', (user_id,))
                    
                    # Проверяем, все ли загадки разгаданы
                    async with db.execute('''
                        SELECT COUNT(*) FROM user_riddles
                        WHERE user_id = ? AND date = ? AND completed = TRUE
                    ''', (user_id, today)) as cursor:
                        completed_count = (await cursor.fetchone())[0]
                        
                        if completed_count == 5:
                            # Создаем запись для токена "Чемпион дня" если её нет
                            await db.execute('''
                                INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                                VALUES (?, 8, 0)
                            ''', (user_id,))
                            
                            # Добавляем супер-награду
                            await db.execute('''
                                UPDATE achievements 
                                SET count = count + 1,
                                    last_updated = CURRENT_TIMESTAMP
                                WHERE user_id = ? AND token_id = 8
                            ''', (user_id,))
                    
                    await db.commit()
                    return True
                return False

    async def spend_token(self, user_id: int, token_id: int) -> bool:
        """Тратит жетон пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем количество жетонов
                async with db.execute('''
                    SELECT count FROM achievements
                    WHERE user_id = ? AND token_id = ?
                ''', (user_id, token_id)) as cursor:
                    result = await cursor.fetchone()
                    if not result or result[0] <= 0:
                        return False
                    
                # Уменьшаем количество жетонов
                await db.execute('''
                    UPDATE achievements
                    SET count = count - 1
                    WHERE user_id = ? AND token_id = ?
                ''', (user_id, token_id))
                
                await db.commit()
                return True
        except Exception:
            return False 

    async def get_next_exercise_video(self, user_id: int, exercise_type: str) -> dict:
        """Получает следующее доступное видео для пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Получаем текущую дату
            today = datetime.now().date()
            
            # Получаем все видео указанного типа с информацией о просмотре
            cursor = await db.execute("""
                SELECT v.*, 
                       (SELECT status FROM user_exercise_views 
                        WHERE user_id = ? AND video_id = v.id 
                        AND date(date) = date(?) 
                        ORDER BY id DESC LIMIT 1) as view_status,
                       (SELECT COUNT(*) FROM user_exercise_views 
                        WHERE user_id = ? AND video_id = v.id 
                        AND date(date) = date(?) 
                        AND (status = 'full' OR status = 'partial')) as completed_today
                FROM exercise_videos v
                WHERE v.type = ?
                ORDER BY v.id
                LIMIT 1
            """, (user_id, today, user_id, today, exercise_type))
            
            video = await cursor.fetchone()
            if video:
                result = dict(video)
                # Добавляем информацию о статусе просмотра
                result['already_viewed'] = result.get('completed_today', 0) > 0
                result['view_status'] = result.get('view_status')
                return result
            return None

    async def record_exercise_view(self, user_id: int, video_id: int, status: str) -> None:
        """Записывает просмотр упражнения пользователем"""
        max_retries = 3
        base_delay = 0.1  # 100ms
        
        # Нормализуем статус
        if status == 'not_done':
            normalized_status = 'not_done'
        elif status == 'partial':
            normalized_status = 'partial'
        else:
            normalized_status = 'full'
        
        for attempt in range(max_retries):
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute(
                        """
                        INSERT INTO user_exercise_views (user_id, video_id, status, date)
                        VALUES (?, ?, ?, date('now'))
                        """,
                        (user_id, video_id, normalized_status)
                    )
                    await db.commit()
                    return
                    
            except Exception as e:
                delay = base_delay * (2 ** attempt)  # Экспоненциальная задержка
                print(f"Attempt {attempt + 1} failed. Retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)
                continue
                
        print(f"Failed to record exercise view after {max_retries} attempts") 

    async def get_exercise_video(self, video_id: int) -> dict:
        """Получает информацию о видео по его ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM exercise_videos WHERE id = ?",
                (video_id,)
            ) as cursor:
                video = await cursor.fetchone()
                if video:
                    return dict(video)
                return None 

    async def update_achievement(self, user_id: int, token_id: int) -> bool:
        """Обновляет достижения пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, есть ли уже запись для этого пользователя и токена
                async with db.execute(
                    'SELECT count FROM achievements WHERE user_id = ? AND token_id = ?',
                    (user_id, token_id)
                ) as cursor:
                    result = await cursor.fetchone()
                    
                if result is None:
                    # Если записи нет, создаем новую
                    await db.execute(
                        'INSERT INTO achievements (user_id, token_id, count, last_updated) VALUES (?, ?, 1, CURRENT_TIMESTAMP)',
                        (user_id, token_id)
                    )
                else:
                    # Если запись есть, увеличиваем счетчик
                    await db.execute(
                        'UPDATE achievements SET count = count + 1, last_updated = CURRENT_TIMESTAMP WHERE user_id = ? AND token_id = ?',
                        (user_id, token_id)
                    )
                
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при обновлении достижений: {e}")
            return False

    async def get_token_by_id(self, token_id: int) -> Optional[Dict]:
        """Получает информацию о токене по его ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM tokens WHERE id = ?',
                (token_id,)
            ) as cursor:
                token = await cursor.fetchone()
                if token:
                    return {
                        'id': token[0],
                        'emoji': token[1],
                        'name': token[2],
                        'description': token[3]
                    }
                return None 

    async def get_user_puzzles(self, user_id: int) -> Tuple[List[Dict], int]:
        """Получает ребусы пользователя на сегодня и количество решенных"""
        today = date.today()
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, есть ли у пользователя ребусы на сегодня
            async with db.execute('''
                SELECT p.id, p.image_data, p.answer1, p.answer2, p.answer3,
                       up.solved1, up.solved2, up.solved3
                FROM puzzles p
                LEFT JOIN user_puzzles up ON p.id = up.puzzle_id 
                    AND up.user_id = ? AND up.date = ?
                ORDER BY p.id
                LIMIT 3
            ''', (user_id, today)) as cursor:
                puzzles = await cursor.fetchall()
                
                if not puzzles:
                    return [], 0

                # Сохраняем изображения во временные файлы
                result = []
                for puzzle in puzzles:
                    # Создаем временный файл для изображения
                    temp_path = os.path.join(self.temp_dir, f"puzzle_{puzzle[0]}.png")
                    with open(temp_path, "wb") as f:
                        f.write(puzzle[1])
                    
                    result.append({
                        'id': puzzle[0],
                        'image_path': temp_path,
                        'answers': [puzzle[2], puzzle[3], puzzle[4]],
                        'solved': [
                            puzzle[5] if puzzle[5] is not None else False,
                            puzzle[6] if puzzle[6] is not None else False,
                            puzzle[7] if puzzle[7] is not None else False
                        ]
                    })

                # Подсчитываем общее количество решенных ребусов
                total_solved = sum(
                    sum(1 for solved in puzzle['solved'] if solved)
                    for puzzle in result
                )
                
                return result, total_solved

    async def check_puzzle_answer(self, user_id: int, puzzle_id: int, rebus_number: int, answer: str) -> bool:
        """Проверяет ответ на ребус и отмечает его как решенный если ответ верный"""
        today = date.today()
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем правильный ответ
            async with db.execute('''
                SELECT answer1, answer2, answer3 FROM puzzles
                WHERE id = ?
            ''', (puzzle_id,)) as cursor:
                answers = await cursor.fetchone()
                if not answers:
                    return False
                
                # Проверяем ответ
                correct_answer = answers[rebus_number - 1].lower()
                if answer.lower() != correct_answer:
                    return False
                
                # Проверяем, существует ли запись в user_puzzles
                async with db.execute('''
                    SELECT COUNT(*) FROM user_puzzles
                    WHERE user_id = ? AND puzzle_id = ? AND date = ?
                ''', (user_id, puzzle_id, today)) as cursor:
                    count = await cursor.fetchone()
                    
                if count[0] == 0:
                    # Создаем новую запись
                    await db.execute('''
                        INSERT INTO user_puzzles (user_id, puzzle_id, date)
                        VALUES (?, ?, ?)
                    ''', (user_id, puzzle_id, today))
                
                # Отмечаем ребус как решенный
                solved_field = f'solved{rebus_number}'
                await db.execute(f'''
                    UPDATE user_puzzles
                    SET {solved_field} = TRUE
                    WHERE user_id = ? AND puzzle_id = ? AND date = ?
                ''', (user_id, puzzle_id, today))
                
                await db.commit()
                
                # Проверяем, все ли ребусы на этой картинке решены
                async with db.execute('''
                    SELECT solved1, solved2, solved3
                    FROM user_puzzles
                    WHERE user_id = ? AND puzzle_id = ? AND date = ?
                ''', (user_id, puzzle_id, today)) as cursor:
                    solved = await cursor.fetchone()
                    
                if solved and all(solved):
                    # Добавляем достижение "Мастер ребусов"
                    await self.add_achievement(user_id, 3)
                    
                    # Проверяем, все ли ребусы на сегодня решены
                    async with db.execute('''
                        SELECT COUNT(*) FROM user_puzzles
                        WHERE user_id = ? AND date = ? AND
                              solved1 = TRUE AND solved2 = TRUE AND solved3 = TRUE
                    ''', (user_id, today)) as cursor:
                        all_solved_count = await cursor.fetchone()
                        
                    if all_solved_count and all_solved_count[0] == 3:
                        # Добавляем достижение "Чемпион дня"
                        await self.add_achievement(user_id, 8)
                
                return True

    async def get_user_tongue_twisters(self, user_id: int) -> Tuple[List[Dict], int]:
        """Получает скороговорки пользователя на сегодня и количество выполненных"""
        today = date.today()
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, есть ли у пользователя скороговорки на сегодня
            async with db.execute('''
                SELECT COUNT(*) FROM user_tongue_twisters 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today)) as cursor:
                count = await cursor.fetchone()
                
            if count[0] == 0:
                # Выбираем 3 случайные скороговорки
                async with db.execute('SELECT id, text FROM tongue_twisters') as cursor:
                    all_twisters = await cursor.fetchall()
                    selected_twisters = random.sample(all_twisters, 3)
                    
                # Добавляем скороговорки пользователю
                for twister in selected_twisters:
                    await db.execute('''
                        INSERT INTO user_tongue_twisters (user_id, twister_id, date)
                        VALUES (?, ?, ?)
                    ''', (user_id, twister[0], today))
                await db.commit()
            
            # Получаем текущие скороговорки пользователя
            async with db.execute('''
                SELECT tt.id, tt.text, utt.completed 
                FROM tongue_twisters tt
                JOIN user_tongue_twisters utt ON tt.id = utt.twister_id
                WHERE utt.user_id = ? AND utt.date = ?
            ''', (user_id, today)) as cursor:
                twisters = await cursor.fetchall()
                twisters_list = [{
                    'id': twister[0],
                    'text': twister[1],
                    'completed': bool(twister[2])
                } for twister in twisters]
                completed_count = sum(1 for twister in twisters_list if twister['completed'])
                
                return twisters_list, completed_count

    async def complete_tongue_twister(self, user_id: int, twister_id: int) -> bool:
        """Отмечает скороговорку как выполненную и начисляет токен"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                today = date.today()
                
                # Проверяем, не была ли скороговорка уже выполнена
                async with db.execute('''
                    SELECT completed FROM user_tongue_twisters
                    WHERE user_id = ? AND twister_id = ? AND date = ?
                ''', (user_id, twister_id, today)) as cursor:
                    result = await cursor.fetchone()
                    if result and result[0]:
                        return False  # Скороговорка уже выполнена
                
                # Отмечаем скороговорку как выполненную
                await db.execute('''
                    UPDATE user_tongue_twisters 
                    SET completed = TRUE 
                    WHERE user_id = ? AND twister_id = ? AND date = ?
                ''', (user_id, twister_id, today))
                
                # Проверяем существование записи в achievements для токена "Говорун"
                await db.execute('''
                    INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                    VALUES (?, 4, 0)
                ''', (user_id,))
                
                # Увеличиваем количество токенов за выполнение скороговорки
                await db.execute('''
                    UPDATE achievements 
                    SET count = count + 1,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND token_id = 4
                ''', (user_id,))
                
                # Проверяем, все ли скороговорки выполнены
                async with db.execute('''
                    SELECT COUNT(*) FROM user_tongue_twisters
                    WHERE user_id = ? AND date = ? AND completed = TRUE
                ''', (user_id, today)) as cursor:
                    completed_count = (await cursor.fetchone())[0]
                    
                # Если выполнены все 3 скороговорки, начисляем дополнительный токен
                if completed_count == 3:
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
                return True
        except Exception as e:
            print(f"Error in complete_tongue_twister: {e}")
            return False 

    async def get_next_creativity_video(self, user_id: int, section: str, current_id: Optional[int] = None, direction: str = "next") -> Optional[Dict]:
        """Получает следующее видео для творчества"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Получаем все видео для данного раздела
                query = """
                    SELECT id, title, description, video_url
                    FROM creativity_videos
                    WHERE type = ?
                    ORDER BY sequence_number
                """
                async with db.execute(query, (section,)) as cursor:
                    videos = await cursor.fetchall()
                    
                if not videos:
                    return None
                    
                # Если текущее видео не указано, возвращаем первое
                if current_id is None:
                    return dict(videos[0])
                    
                # Находим индекс текущего видео
                current_index = next((i for i, v in enumerate(videos) if v['id'] == current_id), -1)
                if current_index == -1:
                    return dict(videos[0])
                    
                # Определяем следующий индекс
                if direction == "next":
                    next_index = current_index + 1
                else:
                    next_index = current_index - 1
                    
                # Проверяем границы
                if 0 <= next_index < len(videos):
                    return dict(videos[next_index])
                    
                return None
                
        except Exception as e:
            print(f"Error getting next creativity video: {e}")
            return None

    async def complete_creativity_masterclass(self, user_id: int, video_id: int) -> bool:
        """Отмечает мастер-класс как выполненный"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO user_creativity_completions
                    (user_id, video_id) VALUES (?, ?)
                """, (user_id, video_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error completing creativity masterclass: {e}")
            return False

    async def get_creativity_video_by_id(self, video_id: int) -> Optional[Dict]:
        """Получает видео по ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT id, title, description, video_url, type
                    FROM creativity_videos
                    WHERE id = ?
                """, (video_id,)) as cursor:
                    video = await cursor.fetchone()
                    return dict(video) if video else None
        except Exception as e:
            print(f"Error getting creativity video by id: {e}")
            return None

    async def is_creativity_masterclass_completed(self, user_id: int, video_id: int) -> bool:
        """Проверяет, выполнен ли мастер-класс пользователем"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT COUNT(*) FROM user_creativity_completions
                    WHERE user_id = ? AND video_id = ?
                """, (user_id, video_id)) as cursor:
                    count = await cursor.fetchone()
                    return count[0] > 0
        except Exception as e:
            print(f"Error checking creativity masterclass completion: {e}")
            return False

    async def get_referral_link(self, user_id: int) -> str:
        """Генерирует или возвращает реферальную ссылку пользователя"""
        return f"https://t.me/mvpRazvivashkaBot?start=ref_{user_id}"

    async def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Добавляет реферала в базу"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO referrals (referrer_id, referred_id)
                    VALUES (?, ?)
                """, (referrer_id, referred_id))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding referral: {e}")
            return False

    async def activate_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Активирует реферала после покупки подписки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Активируем реферала
                await db.execute("""
                    UPDATE referrals 
                    SET is_active = TRUE 
                    WHERE referrer_id = ? AND referred_id = ?
                """, (referrer_id, referred_id))
                
                # Если реферал еще не активирован и награда не получена
                cursor = await db.execute("""
                    SELECT is_active, reward_claimed 
                    FROM referrals 
                    WHERE referrer_id = ? AND referred_id = ?
                """, (referrer_id, referred_id))
                result = await cursor.fetchone()
                
                if result and result[0] and not result[1]:
                    # Добавляем 5 дней к подписке реферера
                    await db.execute("""
                        UPDATE user_subscriptions 
                        SET end_date = date(end_date, '+5 days') 
                        WHERE user_id = ? AND is_active = TRUE
                    """, (referrer_id,))
                    
                    # Отмечаем награду как полученную
                    await db.execute("""
                        UPDATE referrals 
                        SET reward_claimed = TRUE 
                        WHERE referrer_id = ? AND referred_id = ?
                    """, (referrer_id, referred_id))
                
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Error activating referral: {e}")
            return False

    async def get_referral_stats(self, user_id: int) -> dict:
        """Получает статистику рефералов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем количество активных рефералов
            cursor = await db.execute("""
                SELECT COUNT(*) 
                FROM referrals 
                WHERE referrer_id = ? AND is_active = TRUE
            """, (user_id,))
            active_count = (await cursor.fetchone())[0]
            
            # Получаем общее количество рефералов
            cursor = await db.execute("""
                SELECT COUNT(*) 
                FROM referrals 
                WHERE referrer_id = ?
            """, (user_id,))
            total_count = (await cursor.fetchone())[0]
            
            return {
                'active': active_count,
                'total': total_count
            } 

    async def cleanup_temp_files(self):
        """Очищает временные файлы"""
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        try:
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Error deleting temp directory {self.temp_dir}: {e}") 

    async def add_puzzle(self, image_data: bytes, answer1: str, answer2: str, answer3: str) -> bool:
        """Добавляет новый ребус в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT INTO puzzles (image_data, answer1, answer2, answer3) VALUES (?, ?, ?, ?)',
                    (image_data, answer1, answer2, answer3)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding puzzle: {e}")
            return False 

    async def add_creativity_video(self, title: str, description: str, video_url: str, video_type: str, sequence_number: Optional[int] = None) -> bool:
        """Добавляет новое видео для творчества"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if sequence_number is None and video_type == "sculpting":
                    # Для лепки автоматически определяем следующий sequence_number
                    async with db.execute("""
                        SELECT COALESCE(MAX(sequence_number), 0) + 1
                        FROM creativity_videos
                        WHERE type = ?
                    """, (video_type,)) as cursor:
                        sequence_number = (await cursor.fetchone())[0]
                
                await db.execute("""
                    INSERT INTO creativity_videos (type, title, description, video_url, sequence_number)
                    VALUES (?, ?, ?, ?, ?)
                """, (video_type, title, description, video_url, sequence_number))
                
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding creativity video: {e}")
            return False 

    async def get_all_creativity_videos(self, video_type: str) -> List[Dict]:
        """Получает все видео творчества определенного типа"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT id, title, description, video_url, sequence_number
                    FROM creativity_videos
                    WHERE type = ?
                    ORDER BY sequence_number
                """, (video_type,)) as cursor:
                    videos = await cursor.fetchall()
                    return [dict(video) for video in videos]
        except Exception as e:
            print(f"Error getting creativity videos: {e}")
            return [] 

    async def get_all_puzzles(self) -> List[Dict]:
        """Возвращает все ребусы из базы данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT id, answer1, answer2, answer3 FROM puzzles"
                )
                puzzles = await cursor.fetchall()
                return [dict(puzzle) for puzzle in puzzles]
        except Exception as e:
            print(f"Ошибка при получении списка ребусов: {e}")
            return [] 

    async def get_all_daily_tasks(self) -> List[Dict]:
        """Возвращает все ежедневные задания из базы данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT id, task_text as text FROM daily_tasks"
                )
                tasks = await cursor.fetchall()
                return [dict(task) for task in tasks]
        except Exception as e:
            print(f"Ошибка при получении списка ежедневных заданий: {e}")
            return []

    async def get_exercise_videos(self, exercise_type: str) -> List[Dict]:
        """Возвращает все видео упражнений определенного типа"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT id, title, description, video_url FROM exercise_videos WHERE type = ?",
                    (exercise_type,)
                )
                videos = await cursor.fetchall()
                return [dict(video) for video in videos]
        except Exception as e:
            print(f"Ошибка при получении списка видео упражнений: {e}")
            return []

    async def get_all_riddles(self) -> List[Dict]:
        """Возвращает все загадки из базы данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT id, question as text, answer FROM riddles"
                )
                riddles = await cursor.fetchall()
                return [dict(riddle) for riddle in riddles]
        except Exception as e:
            print(f"Ошибка при получении списка загадок: {e}")
            return [] 

    async def get_all_creativity(self, creativity_type: str) -> List[Dict]:
        """Возвращает все элементы творчества определенного типа"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT id, title, description, video_url FROM creativity_videos WHERE type = ?",
                    (creativity_type,)
                )
                items = await cursor.fetchall()
                return [dict(item) for item in items]
        except Exception as e:
            print(f"Ошибка при получении списка элементов творчества: {e}")
            return [] 

    async def get_all_tongue_twisters(self) -> List[Dict]:
        """Возвращает все скороговорки из базы данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT id, text FROM tongue_twisters"
                )
                twisters = await cursor.fetchall()
                return [dict(twister) for twister in twisters]
        except Exception as e:
            print(f"Ошибка при получении списка скороговорок: {e}")
            return [] 

    async def add_riddle(self, question: str, answer: str) -> bool:
        """Добавляет новую загадку в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO riddles (question, answer) VALUES (?, ?)",
                    (question, answer)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении загадки: {e}")
            return False 

    async def add_daily_task(self, task_text: str) -> bool:
        """Добавляет новое ежедневное задание в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO daily_tasks (task_text) VALUES (?)",
                    (task_text,)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении ежедневного задания: {e}")
            return False

    async def add_tongue_twister(self, text: str) -> bool:
        """Добавляет новую скороговорку в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO tongue_twisters (text) VALUES (?)",
                    (text,)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении скороговорки: {e}")
            return False 

    async def add_exercise_video(self, title: str, description: str, video_url: str, video_type: str) -> bool:
        """Добавляет новое видео упражнения в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO exercise_videos (type, title, description, video_url)
                    VALUES (?, ?, ?, ?)
                """, (video_type, title, description, video_url))
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении видео упражнения: {e}")
            return False 