import aiosqlite
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
from config import config
import re
import random
import asyncio

class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path

    async def initialize_videos(self):
        """Инициализирует таблицу видео, если она пуста"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, есть ли уже видео в таблице
            async with db.execute("SELECT COUNT(*) FROM exercise_videos") as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    # Добавляем видео только если таблица пуста
                    await db.executemany(
                        "INSERT INTO exercise_videos (type, title, description, video_url) VALUES (?, ?, ?, ?)",
                        [
                            ('neuro', 'Упражнение "Ленивые восьмерки"', 
                             'Это упражнение помогает улучшить координацию и активизировать оба полушария мозга.',
                             'https://drive.google.com/file/d/14saDv4CTTVuDpX6gtIK_O5ISVP6ypq5P/view?usp=sharing'),
                            ('articular', 'Упражнение "Веселый язычок"',
                             'Гимнастика для языка, которая поможет улучшить произношение звуков.',
                             'https://drive.google.com/file/d/1gpzwEbZS9SIFyvgm6rz4ItChgrXW7pLV/view?usp=sharing')
                        ]
                    )
                    await db.commit()

    async def create_tables(self):
        """Создает необходимые таблицы в базе данных"""
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

            # Создание таблицы загадок
            await db.execute('''
                CREATE TABLE IF NOT EXISTS riddles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            ''')

            # Создание таблицы для отслеживания загадок пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_riddles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    riddle_id INTEGER,
                    completed BOOLEAN DEFAULT FALSE,
                    date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (riddle_id) REFERENCES riddles (id)
                )
            ''')

            # Добавляем начальные загадки, если таблица пуста
            async with db.execute('SELECT COUNT(*) FROM riddles') as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    default_riddles = [
                        ("Не лает, не кусает, а в дом не пускает?", "Замок"),
                        ("Два кольца, два конца, а посередине гвоздик.", "Ножницы"),
                        ("Сидит дед, во сто шуб одет. Кто его раздевает, тот слезы проливает.", "Лук"),
                        ("Зимой и летом одним цветом.", "Ёлка"),
                        ("Без окон, без дверей, полна горница людей.", "Огурец"),
                        ("Красная девица сидит в темнице, а коса на улице.", "Морковь"),
                        ("Висит груша, нельзя скушать.", "Лампочка"),
                        ("Не ездок, а со шпорами, не сторож, а всех будит.", "Петух"),
                        ("Кто приходит, кто уходит, все ее за ручку водят.", "Дверь"),
                        ("Стоит дуб, в нем двенадцать гнезд, в каждом гнезде по четыре яйца, в каждом яйце по семь цыпленков.", "Год")
                    ]
                    await db.executemany(
                        'INSERT INTO riddles (question, answer) VALUES (?, ?)',
                        default_riddles
                    )

            # Создаем таблицу для видео упражнений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS exercise_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,  -- 'neuro' или 'articular'
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    video_url TEXT NOT NULL
                )
            """)
            
            # Создаем таблицу для отслеживания просмотров упражнений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_exercise_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    video_id INTEGER,
                    status TEXT NOT NULL,  -- 'full', 'partial', или 'not_done'
                    date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (video_id) REFERENCES exercise_videos (id)
                )
            """)
            
            # Создание таблицы ребусов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS puzzles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    answer1 TEXT NOT NULL,
                    answer2 TEXT NOT NULL,
                    answer3 TEXT NOT NULL
                )
            ''')

            # Создание таблицы для отслеживания решенных ребусов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_puzzles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    puzzle_id INTEGER,
                    solved1 BOOLEAN DEFAULT FALSE,
                    solved2 BOOLEAN DEFAULT FALSE,
                    solved3 BOOLEAN DEFAULT FALSE,
                    date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (puzzle_id) REFERENCES puzzles (id)
                )
            ''')

            # Добавляем начальные ребусы, если таблица пуста
            async with db.execute('SELECT COUNT(*) FROM puzzles') as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    default_puzzles = [
                        ('1.jpg', 'водопад', 'листопад', 'снегопад'),
                        ('2.jpg', 'подвал', 'подъезд', 'подъем'),
                        ('3.jpg', 'заслонка', 'застава', 'заставка')
                    ]
                    await db.executemany(
                        'INSERT INTO puzzles (image_path, answer1, answer2, answer3) VALUES (?, ?, ?, ?)',
                        default_puzzles
                    )

            # Создание таблицы скороговорок
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tongue_twisters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL
                )
            ''')

            # Создание таблицы для отслеживания выполненных скороговорок
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_tongue_twisters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    twister_id INTEGER,
                    completed BOOLEAN DEFAULT FALSE,
                    date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (twister_id) REFERENCES tongue_twisters (id)
                )
            ''')

            # Добавляем начальные скороговорки, если таблица пуста
            async with db.execute('SELECT COUNT(*) FROM tongue_twisters') as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    default_twisters = [
                        ("Шла Саша по шоссе и сосала сушку",),
                        ("Карл у Клары украл кораллы, а Клара у Карла украла кларнет",),
                        ("На дворе трава, на траве дрова",),
                        ("Ехал Грека через реку, видит Грека в реке рак",),
                        ("Четыре чёрненьких чумазеньких чертёнка чертили чёрными чернилами чертёж",),
                        ("От топота копыт пыль по полю летит",),
                        ("Бык тупогуб, тупогубенький бычок, у быка бела губа была тупа",),
                        ("Три сороки-тараторки тараторили на горке",),
                        ("Рыла свинья белорыла, тупорыла; полдвора рылом изрыла, вырыла, подрыла",),
                        ("Всех скороговорок не перескороговоришь, не перевыскороговоришь",)
                    ]
                    await db.executemany(
                        'INSERT INTO tongue_twisters (text) VALUES (?)',
                        default_twisters
                    )
            
            await db.commit()
            
        # Инициализируем видео после создания таблиц
        await self.initialize_videos()

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
                SELECT COUNT(*) FROM user_puzzles 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today)) as cursor:
                count = await cursor.fetchone()
                
            if count[0] == 0:
                # Выбираем 3 случайных ребуса
                async with db.execute('SELECT id, image_path, answer1, answer2, answer3 FROM puzzles ORDER BY RANDOM() LIMIT 3') as cursor:
                    selected_puzzles = await cursor.fetchall()
                    
                # Добавляем ребусы пользователю
                for puzzle in selected_puzzles:
                    await db.execute('''
                        INSERT INTO user_puzzles (user_id, puzzle_id, date)
                        VALUES (?, ?, ?)
                    ''', (user_id, puzzle[0], today))
                await db.commit()
            
            # Получаем текущие ребусы пользователя
            async with db.execute('''
                SELECT p.id, p.image_path, p.answer1, p.answer2, p.answer3,
                       up.solved1, up.solved2, up.solved3
                FROM puzzles p
                JOIN user_puzzles up ON p.id = up.puzzle_id
                WHERE up.user_id = ? AND up.date = ?
                ORDER BY up.id
            ''', (user_id, today)) as cursor:
                puzzles = await cursor.fetchall()
                
            # Подсчитываем общее количество решенных ребусов
            total_solved = sum(
                sum(1 for solved in puzzle[5:8] if solved)
                for puzzle in puzzles
            )
                
            return [{
                'id': puzzle[0],
                'image_path': puzzle[1],
                'answers': [puzzle[2], puzzle[3], puzzle[4]],
                'solved': [puzzle[5], puzzle[6], puzzle[7]]
            } for puzzle in puzzles], total_solved

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
                
                correct_answer = answers[rebus_number - 1].lower()
                user_answer = answer.lower()
                
                if correct_answer == user_answer:
                    # Отмечаем ребус как решенный
                    solved_field = f'solved{rebus_number}'
                    await db.execute(f'''
                        UPDATE user_puzzles 
                        SET {solved_field} = TRUE
                        WHERE user_id = ? AND puzzle_id = ? AND date = ?
                    ''', (user_id, puzzle_id, today))
                    
                    # Проверяем, все ли ребусы на картинке решены
                    async with db.execute('''
                        SELECT solved1, solved2, solved3
                        FROM user_puzzles
                        WHERE user_id = ? AND puzzle_id = ? AND date = ?
                    ''', (user_id, puzzle_id, today)) as cursor:
                        solved_status = await cursor.fetchone()
                        all_solved = all(solved_status)
                        
                        if all_solved:
                            # Создаем запись для токена "Мастер ребусов" если её нет
                            await db.execute('''
                                INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                                VALUES (?, 3, 0)
                            ''', (user_id,))
                            
                            # Увеличиваем количество токенов
                            await db.execute('''
                                UPDATE achievements 
                                SET count = count + 1,
                                    last_updated = CURRENT_TIMESTAMP
                                WHERE user_id = ? AND token_id = 3
                            ''', (user_id,))
                    
                    await db.commit()
                    return True
                return False 

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