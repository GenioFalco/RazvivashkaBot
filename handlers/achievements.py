from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.achievements import AchievementsKeyboard
from keyboards.main_menu import MainMenuKeyboard
from database.database import Database
from config import config

router = Router()

class TokenEditStates(StatesGroup):
    """Состояния для редактирования токена"""
    waiting_for_emoji = State()
    waiting_for_name = State()

@router.callback_query(F.data == "achievements")
async def show_achievements_menu(callback: CallbackQuery):
    """Показывает главное меню раздела достижений"""
    await callback.message.edit_text(
        "✨ Добро пожаловать в волшебную комнату достижений! ✨\n"
        "Здесь ты найдёшь все свои награды за старания и успехи.",
        reply_markup=AchievementsKeyboard.get_main_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "photo_album")
async def show_photo_album(callback: CallbackQuery):
    """Показывает фотоальбом"""
    await callback.message.edit_text(
        "📸 Твой волшебный фотоальбом пока пуст.\n"
        "Скоро здесь появятся твои замечательные рисунки из раздела «Творчество»!",
        reply_markup=AchievementsKeyboard.get_back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "achievements_rating")
async def show_achievements_rating(callback: CallbackQuery):
    """Показывает рейтинг пользователей"""
    await callback.message.edit_text(
        "📊 Рейтинг волшебников\n\n"
        "🚧 Этот раздел пока в разработке.\n"
        "Скоро здесь появится список самых старательных учеников!",
        reply_markup=AchievementsKeyboard.get_back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "achievements_list")
async def show_achievements_list(callback: CallbackQuery):
    """Показывает список всех токенов"""
    db = Database()
    tokens = await db.get_all_tokens()
    user_achievements = await db.get_user_achievements(callback.from_user.id)
    
    text = (
        "🌈 Твоя волшебная коллекция наград! 🌈\n\n"
        "Привет, юный волшебник! Давай посмотрим, какие чудесные награды "
        "ты уже собрал за свои старания.\n\n"
    )
    
    # Группируем достижения по категориям
    categories = {
        "Ежедневные": ["Ключ доступа", "Звезда дня", "Чемпион дня"],
        "Развитие речи": ["Говорун", "Мудрец"],
        "Гимнастика": ["Гимнаст", "Умник"],
        "Логика": ["Мастер ребусов"]
    }
    
    for category, token_names in categories.items():
        category_tokens = [t for t in tokens if t['name'] in token_names]
        if category_tokens:
            text += f"\n🎯 {category}:\n"
            for token in category_tokens:
                count = user_achievements.get(token['id'], 0)
                stars = "⭐" * min(count, 5) if count > 0 else "❌"
                text += (
                    f"{token['emoji']} {token['name']}\n"
                    f"└ Собрано: {count} шт. {stars}\n"
                    f"└ {token['description']}\n\n"
                )
    
    # Добавляем мотивационное сообщение в конце
    total_achievements = sum(user_achievements.values())
    if total_achievements == 0:
        text += "\n🌟 Начни своё путешествие! Выполняй задания и собирай награды!"
    elif total_achievements < 5:
        text += "\n🌟 Отличное начало! Продолжай в том же духе!"
    elif total_achievements < 10:
        text += "\n🌟 Ты уже настоящий коллекционер! Так держать!"
    else:
        text += "\n🌟 Вау! Ты настоящий чемпион! Продолжай собирать награды!"
    
    await callback.message.edit_text(
        text,
        reply_markup=AchievementsKeyboard.get_back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "manage_tokens")
async def show_tokens_management(callback: CallbackQuery):
    """Показывает меню управления токенами"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к этому разделу")
        return

    db = Database()
    tokens = await db.get_all_tokens()
    
    await callback.message.edit_text(
        "Выберите токен для редактирования:",
        reply_markup=AchievementsKeyboard.get_admin_tokens_keyboard(tokens)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_token_"))
async def start_token_edit(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс редактирования токена"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к этому действию")
        return

    token_id = int(callback.data.split("_")[2])
    await state.update_data(token_id=token_id)
    
    await callback.message.edit_text(
        "Отправьте новый эмодзи для токена.\n"
        "Пример: 🌟, 🎨, 🏆\n\n"
        "Для отмены нажмите кнопку Назад",
        reply_markup=AchievementsKeyboard.get_back_button()
    )
    await state.set_state(TokenEditStates.waiting_for_emoji)
    await callback.answer()

@router.message(TokenEditStates.waiting_for_emoji)
async def process_token_emoji(message: Message, state: FSMContext):
    """Обрабатывает полученный эмодзи"""
    db = Database()
    if not db.is_valid_emoji(message.text):
        await message.answer(
            "❌ Это не похоже на эмодзи. Пожалуйста, отправьте один эмодзи.\n"
            "Примеры: 🌟, 🎨, 🏆",
            reply_markup=AchievementsKeyboard.get_back_button()
        )
        return

    await state.update_data(emoji=message.text)
    await message.answer(
        "Отлично! Теперь введите новое название для токена.\n"
        "Можно использовать только русские и английские буквы.\n"
        "Пример: Звезда творчества",
        reply_markup=AchievementsKeyboard.get_back_button()
    )
    await state.set_state(TokenEditStates.waiting_for_name)

@router.message(TokenEditStates.waiting_for_name)
async def process_token_name(message: Message, state: FSMContext):
    """Обрабатывает полученное название токена"""
    db = Database()
    if not db.is_valid_name(message.text):
        await message.answer(
            "❌ Недопустимое название. Используйте только русские и английские буквы.\n"
            "Пример: Звезда творчества",
            reply_markup=AchievementsKeyboard.get_back_button()
        )
        return

    data = await state.get_data()
    success = await db.update_token(data['token_id'], data['emoji'], message.text)
    
    if success:
        await message.answer(
            "✅ Токен успешно обновлен!",
            reply_markup=MainMenuKeyboard.get_keyboard(user_id=message.from_user.id)
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при обновлении токена",
            reply_markup=MainMenuKeyboard.get_keyboard(user_id=message.from_user.id)
        )
    await state.clear()

@router.callback_query(F.data.in_({"back_to_main", "back_to_achievements", "back_to_admin"}))
async def process_back_button(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие кнопки "Назад" """
    await state.clear()
    
    if callback.data == "back_to_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
        )
    elif callback.data == "back_to_achievements":
        await callback.message.edit_text(
            "Выберите раздел:",
            reply_markup=AchievementsKeyboard.get_main_keyboard()
        )
    elif callback.data == "back_to_admin":
        # Возвращаемся в админ-панель
        await callback.message.edit_text(
            "Админ-панель:",
            reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
        )
    
    await callback.answer() 