import aiosqlite
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
from config import config
import re
import random
import asyncio
import logging

class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path

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
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создаем таблицу для достижений пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_id INTEGER,
                    token_id INTEGER,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, token_id),
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
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
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
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
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
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
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (video_id) REFERENCES exercise_videos (id)
                )
            ''')
            
            # Создаем таблицу для видео творчества
            await db.execute('''
                CREATE TABLE IF NOT EXISTS creativity_videos (
                    id INTEGER PRIMARY KEY,
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
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (video_id) REFERENCES creativity_videos (id)
                )
            ''')
            
            # Добавляем токен "Алмаз" если его нет
            await db.execute('''
                INSERT OR IGNORE INTO tokens (id, emoji, name, description)
                VALUES (9, "💎", "Алмаз", "Даётся за выполнение творческих мастер-классов")
            ''')
            
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

    async def get_next_creativity_video(self, user_id: int, section: str, current_id: int = None, direction: str = None) -> dict:
        """Получает следующее видео для творчества"""
        async with aiosqlite.connect(self.db_path) as db:
            if section == "sculpting":
                # Для лепки используем последовательный порядок
                if direction == "prev" and current_id:
                    query = '''
                        SELECT v.* FROM creativity_videos v
                        WHERE v.type = ? AND v.sequence_number < (
                            SELECT sequence_number FROM creativity_videos WHERE id = ?
                        )
                        ORDER BY v.sequence_number DESC LIMIT 1
                    '''
                    params = (section, current_id)
                elif direction == "next" and current_id:
                    query = '''
                        SELECT v.* FROM creativity_videos v
                        WHERE v.type = ? AND v.sequence_number > (
                            SELECT sequence_number FROM creativity_videos WHERE id = ?
                        )
                        ORDER BY v.sequence_number ASC LIMIT 1
                    '''
                    params = (section, current_id)
                else:
                    # Получаем первое видео
                    query = '''
                        SELECT v.* FROM creativity_videos v
                        WHERE v.type = ?
                        ORDER BY v.sequence_number ASC LIMIT 1
                    '''
                    params = (section,)
            else:
                # Для рисования и бумаги используем случайный порядок
                if direction and current_id:
                    # При навигации исключаем текущее видео
                    query = '''
                        SELECT v.* FROM creativity_videos v
                        WHERE v.type = ? AND v.id != ?
                        ORDER BY RANDOM() LIMIT 1
                    '''
                    params = (section, current_id)
                else:
                    # При первом показе берем любое видео
                    query = '''
                        SELECT v.* FROM creativity_videos v
                        WHERE v.type = ?
                        ORDER BY RANDOM() LIMIT 1
                    '''
                    params = (section,)
            
            try:
                async with db.execute(query, params) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return {
                            'id': row[0],
                            'type': row[1],
                            'title': row[2],
                            'description': row[3],
                            'video_url': row[4],
                            'sequence_number': row[5] if row[5] else None
                        }
                    return None
            except Exception as e:
                logging.error(f"Error getting next creativity video: {e}")
                return None

    async def complete_creativity_masterclass(self, user_id: int, video_id: int) -> bool:
        """Отмечает мастер-класс как выполненный и выдает награду"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Проверяем, не было ли уже выполнено это видео
                cursor = await db.execute('''
                    SELECT COUNT(*) FROM user_creativity_completions
                    WHERE user_id = ? AND video_id = ?
                ''', (user_id, video_id))
                count = (await cursor.fetchone())[0]
                if count > 0:
                    return True  # Видео уже было выполнено

                # Добавляем запись о выполнении
                await db.execute('''
                    INSERT INTO user_creativity_completions (user_id, video_id)
                    VALUES (?, ?)
                ''', (user_id, video_id))
                
                # Проверяем существование записи для токена "Алмаз"
                await db.execute('''
                    INSERT OR IGNORE INTO achievements (user_id, token_id, count)
                    VALUES (?, 9, 0)
                ''', (user_id,))
                
                # Увеличиваем количество алмазов
                await db.execute('''
                    UPDATE achievements 
                    SET count = count + 1,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND token_id = 9
                ''', (user_id,))
                
                await db.commit()
                return True
            except Exception as e:
                logging.error(f"Error completing creativity masterclass: {e}")
                return False

    async def get_creativity_video_by_id(self, video_id: int) -> dict:
        """Получает информацию о видео по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                cursor = await db.execute('''
                    SELECT * FROM creativity_videos WHERE id = ?
                ''', (video_id,))
                
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'type': row[1],
                        'title': row[2],
                        'description': row[3],
                        'video_url': row[4],
                        'sequence_number': row[5] if row[5] else None
                    }
                return None
            except Exception as e:
                print(f"Error getting creativity video by id: {e}")
                return None 

    async def is_creativity_masterclass_completed(self, user_id: int, video_id: int) -> bool:
        """Проверяет, выполнен ли мастер-класс пользователем"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    SELECT COUNT(*) FROM user_creativity_completions
                    WHERE user_id = ? AND video_id = ?
                ''', (user_id, video_id))
                count = (await cursor.fetchone())[0]
                return count > 0
        except Exception as e:
            logging.error(f"Error checking creativity masterclass completion: {e}")
            return False 