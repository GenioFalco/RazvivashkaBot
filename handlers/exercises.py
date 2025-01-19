from aiogram import Router, F, types
from aiogram.types import CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
from database.database import Database
from keyboards.exercises import ExercisesKeyboard
import aiohttp
from io import BytesIO
import re
from urllib.parse import urlencode
import aiosqlite
from datetime import datetime
from keyboards.main_menu import MainMenuKeyboard

router = Router()

# Словарь с описаниями разделов
EXERCISE_DESCRIPTIONS = {
    'neuro': {
        'title': '🧠 Нейрогимнастика',
        'description': (
            "Добро пожаловать в раздел Нейрогимнастика!\n\n"
            "Здесь ты найдешь упражнения, которые помогут тебе:\n"
            "• Улучшить память\n"
            "• Развить внимание\n"
            "• Стать более сообразительным\n\n"
            "За каждое выполненное упражнение ты получишь 🧠 Умник!\n"
            "Каждый день тебя ждет новое упражнение.\n"
            "Нажми 'Смотреть', чтобы начать тренировку!"
        ),
        'success_message': "Молодец! Ты тренируешь свой ум, как настоящий ученый! 🧠 Продолжай в том же духе, твой мозг становится сильнее с каждым днем!",
        'partial_message': "Хороший старт! Ты уже сделал шаг к тому, чтобы прокачать свой ум. Продолжай!",
        'not_done_message': "Не получилось сегодня — получится завтра. Главное — не останавливаться!"
    },
    'articular': {
        'title': '🤸 Артикулярная гимнастика',
        'description': (
            "Добро пожаловать в раздел Артикулярная гимнастика!\n\n"
            "Здесь ты найдешь упражнения, которые помогут тебе:\n"
            "• Улучшить произношение\n"
            "• Развить речевой аппарат\n"
            "• Говорить четко и красиво\n\n"
            "За каждое выполненное упражнение ты получишь 🤸 Гимнаст!\n"
            "Каждый день тебя ждет новое упражнение.\n"
            "Нажми 'Смотреть', чтобы начать тренировку!"
        ),
        'success_message': "Ты суперзвезда! Теперь твоя речь будет звучать как у настоящего диктора! 🎤",
        'partial_message': "Хорошее начало! Ты на пути к совершенству в тренировке своей артикуляции!",
        'not_done_message': "Не переживай! Завтра у тебя обязательно получится потренироваться и сделать свою речь еще лучше!"
    }
}

async def get_direct_download_link(url: str) -> str:
    """Получает прямую ссылку на скачивание файла с Google Drive"""
    # Извлекаем ID файла из URL
    file_id = url.split('/d/')[1].split('/')[0]
    # Формируем прямую ссылку для скачивания
    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"Прямая ссылка для скачивания: {direct_link}")
    return direct_link

async def send_video(bot, chat_id, video_url, caption, reply_markup=None):
    """Отправляет видео по прямой ссылке"""
    try:
        # Отправляем видео напрямую по ссылке
        await bot.send_video(
            chat_id=chat_id,
            video=video_url,
            caption=caption,
            reply_markup=reply_markup,
            supports_streaming=True
        )
        return True
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")
        try:
            # Если не удалось отправить напрямую, пробуем скачать и отправить как файл
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        video_data = await response.read()
                        video_file = BufferedInputFile(
                            video_data,
                            filename="exercise.mp4"
                        )
                        await bot.send_video(
                            chat_id=chat_id,
                            video=video_file,
                            caption=caption,
                            reply_markup=reply_markup,
                            supports_streaming=True
                        )
                        return True
        except Exception as e2:
            print(f"Ошибка при повторной попытке отправки видео: {e2}")
        return False

@router.callback_query(F.data.in_(["neuro_exercises", "articular_exercises"]))
async def show_exercise_menu(callback: CallbackQuery, state: FSMContext):
    """Показывает меню раздела упражнений"""
    exercise_type = 'neuro' if callback.data == "neuro_exercises" else 'articular'
    
    db = Database()
    # Проверяем доступ к функции
    has_access = await db.check_feature_access(callback.from_user.id, exercise_type + '_exercises')
    if not has_access:
        await callback.message.edit_text(
            "⭐ Доступ к упражнениям ограничен!\n\n"
            "Для доступа к этому разделу необходима подписка.\n"
            "Перейдите в раздел «Для мам», чтобы узнать подробности.",
            reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return
    
    info = EXERCISE_DESCRIPTIONS[exercise_type]
    
    # Сохраняем тип упражнения в состояние
    await state.update_data(exercise_type=exercise_type)
    
    await callback.message.edit_text(
        f"{info['title']}\n\n{info['description']}",
        reply_markup=ExercisesKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "watch_exercise")
async def show_exercise_video(callback: CallbackQuery, state: FSMContext):
    """Показывает видео упражнения"""
    print("Обработка нажатия кнопки 'Смотреть'")
    
    state_data = await state.get_data()
    exercise_type = state_data.get('exercise_type')
    print(f"Тип упражнения из состояния: {exercise_type}")
    
    if not exercise_type:
        print("Ошибка: тип упражнения не найден в состоянии")
        await callback.message.edit_text("Произошла ошибка. Попробуйте начать сначала.")
        return

    db = Database()
    video = await db.get_next_exercise_video(callback.from_user.id, exercise_type)
    print(f"Полученное видео из БД: {video}")
    
    if not video:
        print("Ошибка: видео не найдено в БД")
        await callback.message.edit_text("Произошла ошибка при получении видео.")
        return

    try:
        print(f"Попытка загрузки видео по URL: {video['video_url']}")
        direct_link = await get_direct_download_link(video['video_url'])
        print(f"Получена прямая ссылка: {direct_link}")
        
        # Формируем подпись для видео
        caption = f"🎥 {video['title']}\n\n{video['description']}"
        if video.get('already_viewed'):
            caption += "\n\n✅ Вы уже выполнили это упражнение сегодня!"
        else:
            caption += "\n\nОтметьте, пожалуйста, результат:"
        
        # Отправляем видео новым сообщением
        success = await send_video(
            bot=callback.message.bot,
            chat_id=callback.message.chat.id,
            video_url=direct_link,
            caption=caption,
            reply_markup=ExercisesKeyboard.get_exercise_keyboard(
                video['id'],
                show_completion=not video.get('already_viewed')
            )
        )
        
        if success:
            # Сохраняем ID видео в состоянии
            await state.update_data(current_video_id=video['id'])
        else:
            await callback.message.edit_text("Произошла ошибка при загрузке видео. Попробуйте позже.")
            
    except Exception as e:
        print(f"Ошибка при отправке видео: {e}")
        await callback.message.edit_text("Произошла ошибка при загрузке видео. Попробуйте позже.")
    await callback.answer()

@router.callback_query(F.data.startswith(("prev_video_", "next_video_")))
async def navigate_videos(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает навигацию между видео"""
    try:
        action = callback.data.split('_')[0]  # prev или next
        current_video_id = int(callback.data.split('_')[2])
        
        state_data = await state.get_data()
        exercise_type = state_data.get('exercise_type')
        
        if not exercise_type:
            await callback.message.edit_text("Произошла ошибка. Попробуйте начать сначала.")
            return
        
        db = Database()
        # Получаем следующее/предыдущее видео
        video = await db.get_next_exercise_video(callback.from_user.id, exercise_type)
        
        if not video:
            await callback.answer("Больше видео нет")
            return
            
        direct_link = await get_direct_download_link(video['video_url'])
        
        # Формируем подпись для видео
        caption = f"🎥 {video['title']}\n\n{video['description']}"
        if video.get('already_viewed'):
            caption += "\n\n✅ Вы уже выполнили это упражнение сегодня!"
        else:
            caption += "\n\nОтметьте, пожалуйста, результат:"
            
        # Отправляем видео
        success = await send_video(
            bot=callback.message.bot,
            chat_id=callback.message.chat.id,
            video_url=direct_link,
            caption=caption,
            reply_markup=ExercisesKeyboard.get_exercise_keyboard(
                video['id'],
                show_completion=not video.get('already_viewed')
            )
        )
        
        if success:
            # Удаляем старое сообщение
            await callback.message.delete()
            # Сохраняем ID видео в состоянии
            await state.update_data(current_video_id=video['id'])
        else:
            await callback.answer("Произошла ошибка при загрузке видео")
        
    except Exception as e:
        print(f"Ошибка при навигации: {e}")
        await callback.answer("Произошла ошибка при переключении видео")

@router.callback_query(F.data.startswith(("exercise_full_", "exercise_partial_", "exercise_not_done_")))
async def process_exercise_completion(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает отметку о выполнении упражнения"""
    try:
        # Определяем статус из callback_data
        data = callback.data
        if '_not_done_' in data:
            status = 'not_done'
            video_id = int(data.split('_not_done_')[1])
        else:
            parts = data.split('_')
            status = parts[1]  # full или partial
            video_id = int(parts[2])
        
        db = Database()
        # Получаем информацию о видео для определения типа упражнения
        video = await db.get_exercise_video(video_id)
        if not video:
            await callback.answer("Ошибка: видео не найдено")
            return
            
        exercise_type = video['type']
        info = EXERCISE_DESCRIPTIONS[exercise_type]
        
        # Проверяем, не получал ли пользователь уже жетоны за это упражнение сегодня
        today = datetime.now().date()
        async with aiosqlite.connect(db.db_path) as conn:
            cursor = await conn.execute("""
                SELECT COUNT(*) FROM user_exercise_views
                WHERE user_id = ? AND video_id = ?
                AND date(date) = date(?)
                AND (status = 'full' OR status = 'partial')
            """, (callback.from_user.id, video_id, today))
            count = (await cursor.fetchone())[0]
            
            if count > 0 and status in ['full', 'partial']:
                await callback.answer("Вы уже получили жетоны за это упражнение сегодня!")
                return
        
        # Записываем просмотр упражнения
        await db.record_exercise_view(callback.from_user.id, video_id, status)
        
        if status in ['full', 'partial']:  # Начисляем жетоны и за полное, и за частичное выполнение
            # Получаем информацию о токене
            token_id = 5 if exercise_type == 'neuro' else 6
            token = await db.get_token_by_id(token_id)
            
            # Обновляем достижения пользователя
            await db.update_achievement(callback.from_user.id, token_id)
            
            message = info['success_message'] if status == 'full' else info['partial_message']
            await callback.message.answer(
                f"{message}\n"
                f"Ты получаешь {token['emoji']} {token['name']}!\n"
                "Возвращайся завтра за новым упражнением.",
                reply_markup=ExercisesKeyboard.get_menu_keyboard()
            )
        else:  # status == 'not_done'
            await callback.message.answer(
                f"{info['not_done_message']}\n"
                "Возвращайся завтра за новым упражнением.",
                reply_markup=ExercisesKeyboard.get_menu_keyboard()
            )
            
    except Exception as e:
        print(f"Ошибка при обработке отметки: {e}")
        await callback.message.answer(
            "Произошла ошибка при сохранении результата. Попробуйте позже.",
            reply_markup=ExercisesKeyboard.get_menu_keyboard()
        )
    await callback.answer()

@router.callback_query(F.data == "back_to_exercise_menu")
async def back_to_exercise_menu(callback: CallbackQuery, state: FSMContext):
    """Возвращает в меню раздела упражнений"""
    try:
        # Получаем тип упражнения из состояния
        data = await state.get_data()
        exercise_type = data.get('exercise_type')
        
        if exercise_type:
            info = EXERCISE_DESCRIPTIONS[exercise_type]
            await callback.message.edit_text(
                f"{info['title']}\n\n{info['description']}",
                reply_markup=ExercisesKeyboard.get_menu_keyboard()
            )
        else:
            # Если тип упражнения не найден, возвращаем в главное меню
            from keyboards.main_menu import MainMenuKeyboard
            await callback.message.edit_text(
                "Главное меню:",
                reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
            )
    except Exception as e:
        # Если не удалось отредактировать сообщение, отправляем новое
        data = await state.get_data()
        exercise_type = data.get('exercise_type')
        
        if exercise_type:
            info = EXERCISE_DESCRIPTIONS[exercise_type]
            await callback.message.answer(
                f"{info['title']}\n\n{info['description']}",
                reply_markup=ExercisesKeyboard.get_menu_keyboard()
            )
        else:
            from keyboards.main_menu import MainMenuKeyboard
            await callback.message.answer(
                "Главное меню:",
                reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
            )
    await callback.answer() 