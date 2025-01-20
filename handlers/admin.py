from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import Database
from keyboards.admin import AdminKeyboard
from keyboards.main_menu import MainMenuKeyboard
from config import config
import math

router = Router()
db = Database()

# Состояния для редактирования тарифов
class TariffStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()

# Состояния для добавления контента
class ContentStates(StatesGroup):
    waiting_for_puzzle_image = State()
    waiting_for_puzzle_answers = State()
    waiting_for_twister = State()
    waiting_for_riddle = State()
    waiting_for_riddle_answer = State()
    waiting_for_daily_task = State()
    waiting_for_creativity_title = State()
    waiting_for_creativity_description = State()
    waiting_for_creativity_video = State()
    waiting_for_exercise_title = State()
    waiting_for_exercise_description = State()
    waiting_for_exercise_video = State()

# Состояния для редактирования токенов
class TokenStates(StatesGroup):
    waiting_for_emoji = State()
    waiting_for_name = State()

ITEMS_PER_PAGE = 5

@router.callback_query(F.data == "admin_panel")
async def show_admin_menu(callback: CallbackQuery):
    """Показывает главное меню админ-панели"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👨‍💼 Админ-панель\n\n"
        "Здесь вы можете:\n"
        "• Управлять пользователями\n"
        "• Управлять жетонами\n"
        "• Управлять подписками\n"
        "• Управлять контентом\n\n"
        "Выберите нужный раздел:",
        reply_markup=AdminKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_users")
async def show_users_list(callback: CallbackQuery, page: int = 1):
    """Показывает список пользователей"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    db = Database()
    users = await db.get_all_users()
    
    total_pages = math.ceil(len(users) / ITEMS_PER_PAGE)
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    current_users = users[start_idx:end_idx]
    
    await callback.message.edit_text(
        f"👥 Список пользователей (страница {page}/{total_pages}):",
        reply_markup=AdminKeyboard.get_users_keyboard(current_users, page, total_pages)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("users_page_"))
async def navigate_users(callback: CallbackQuery):
    """Обрабатывает навигацию по страницам пользователей"""
    page = int(callback.data.split("_")[2])
    await show_users_list(callback, page)

@router.callback_query(F.data == "admin_subscriptions")
async def show_subscriptions_list(callback: CallbackQuery, page: int = 1):
    """Показывает список подписок"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    db = Database()
    subscriptions = await db.get_all_user_subscriptions()
    
    total_pages = math.ceil(len(subscriptions) / ITEMS_PER_PAGE)
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    current_subscriptions = subscriptions[start_idx:end_idx]
    
    await callback.message.edit_text(
        f"💳 Список подписок (страница {page}/{total_pages}):",
        reply_markup=AdminKeyboard.get_subscriptions_keyboard(current_subscriptions, page, total_pages)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("subs_page_"))
async def navigate_subscriptions(callback: CallbackQuery):
    """Обрабатывает навигацию по страницам подписок"""
    page = int(callback.data.split("_")[2])
    await show_subscriptions_list(callback, page)

@router.callback_query(F.data == "manage_tariffs")
async def show_tariffs(callback: CallbackQuery):
    """Показывает список тарифов"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    db = Database()
    tariffs = await db.get_all_subscriptions()
    
    await callback.message.edit_text(
        "⚙️ Управление тарифами\n\n"
        "Выберите тариф для редактирования:",
        reply_markup=AdminKeyboard.get_tariffs_keyboard(tariffs)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_tariff_"))
async def edit_tariff(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс редактирования тарифа"""
    tariff_id = int(callback.data.split("_")[2])
    await state.update_data(tariff_id=tariff_id)
    await state.set_state(TariffStates.waiting_for_name)
    
    await callback.message.edit_text(
        "Введите новое название тарифа:"
    )
    await callback.answer()

@router.message(TariffStates.waiting_for_name)
async def process_tariff_name(message: Message, state: FSMContext):
    """Обрабатывает ввод названия тарифа"""
    await state.update_data(new_name=message.text)
    await state.set_state(TariffStates.waiting_for_price)
    
    await message.answer("Введите новую стоимость тарифа (в рублях):")

@router.message(TariffStates.waiting_for_price)
async def process_tariff_price(message: Message, state: FSMContext):
    """Обрабатывает ввод стоимости тарифа"""
    try:
        price = int(message.text)
        data = await state.get_data()
        
        db = Database()
        await db.update_subscription(
            data['tariff_id'],
            data['new_name'],
            price
        )
        
        await state.clear()
        await message.answer(
            "✅ Тариф успешно обновлен!",
            reply_markup=AdminKeyboard.get_menu_keyboard()
        )
    except ValueError:
        await message.answer("Ошибка! Введите целое число:")

@router.callback_query(F.data == "admin_content")
async def show_content_menu(callback: CallbackQuery):
    """Показывает меню управления контентом"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📝 Управление контентом\n\n"
        "Выберите раздел для редактирования:",
        reply_markup=AdminKeyboard.get_content_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("show_content:"))
async def show_content_list(callback: CallbackQuery, state: FSMContext):
    # Разбираем callback данные
    parts = callback.data.split(":")
    
    # Определяем тип контента и страницу
    if len(parts) == 4 and parts[1] == "creativity":
        content_type = f"creativity_{parts[2]}"
        page = int(parts[3])
    else:
        content_type = parts[1]
        page = int(parts[2]) if len(parts) > 2 else 1
    
    db = Database()
    items = []
    
    if content_type == "daily":
        items = await db.get_all_daily_tasks()
    elif content_type == "riddles":
        items = await db.get_all_riddles()
    elif content_type == "twisters":
        items = await db.get_all_tongue_twisters()
    elif content_type == "puzzles":
        items = await db.get_all_puzzles()
    elif content_type.startswith("creativity_"):
        creativity_type = content_type.split("_")[1]
        items = await db.get_all_creativity(creativity_type)
    elif content_type == "articular":
        items = await db.get_exercise_videos("articular")
    elif content_type == "neuro":
        items = await db.get_exercise_videos("neuro")

    total_pages = math.ceil(len(items) / ITEMS_PER_PAGE)
    
    # Получаем клавиатуру для списка контента
    keyboard = AdminKeyboard.get_content_list_keyboard(items, page, total_pages, content_type)
    
    # Формируем заголовок в зависимости от типа контента
    headers = {
        "daily": "📝 Список заданий на день",
        "riddles": "🤔 Список загадок",
        "twisters": "👅 Список скороговорок",
        "puzzles": "🧩 Список ребусов",
        "creativity_drawing": "🎨 Список мастер-классов по рисованию",
        "creativity_paper": "📄 Список мастер-классов по бумаге",
        "creativity_sculpting": "🏺 Список мастер-классов по лепке",
        "articular": "🗣 Список упражнений для артикуляции",
        "neuro": "🧠 Список упражнений для нейрогимнастики"
    }
    
    header = headers.get(content_type, "📋 Список элементов")
    
    await callback.message.edit_text(
        text=f"{header}\n\nСтраница {page}/{total_pages}",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("admin_add_content:"))
async def start_content_addition(callback: CallbackQuery, state: FSMContext):
    content_type = callback.data.split(":")[1]
    
    # Сохраняем тип контента в состоянии
    await state.update_data(content_type=content_type)
    
    # Определяем следующее состояние и сообщение в зависимости от типа контента
    messages = {
        "daily": "📝 Введите текст задания на день:",
        "riddles": "🤔 Введите текст загадки и правильный ответ через | (пример: Загадка|Ответ):",
        "twisters": "👅 Введите текст скороговорки:",
        "puzzles": "🧩 Отправьте изображение ребуса:",
        "creativity_drawing": "🎨 Введите название мастер-класса по рисованию:",
        "creativity_paper": "📄 Введите название мастер-класса по бумаге:",
        "creativity_sculpting": "🏺 Введите название мастер-класса по лепке:",
        "articular": "🗣 Введите название упражнения для артикуляции:",
        "neuro": "🧠 Введите название упражнения для нейрогимнастики:"
    }
    
    message = messages.get(content_type, "Введите данные:")
    
    # Устанавливаем соответствующее состояние
    states = {
        "daily": ContentStates.waiting_for_daily_task,
        "riddles": ContentStates.waiting_for_riddle,
        "twisters": ContentStates.waiting_for_twister,
        "puzzles": ContentStates.waiting_for_puzzle_image,
        "creativity_drawing": ContentStates.waiting_for_creativity_title,
        "creativity_paper": ContentStates.waiting_for_creativity_title,
        "creativity_sculpting": ContentStates.waiting_for_creativity_title,
        "articular": ContentStates.waiting_for_exercise_title,
        "neuro": ContentStates.waiting_for_exercise_title
    }
    
    await state.set_state(states.get(content_type))
    
    # Отправляем сообщение с кнопкой отмены
    await callback.message.edit_text(
        text=message,
        reply_markup=AdminKeyboard.get_cancel_keyboard()
    )

@router.message(ContentStates.waiting_for_puzzle_image)
async def process_puzzle_image(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте изображение ребуса")
        return
        
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file.file_path)
    
    await state.update_data(puzzle_image=file_bytes.read())
    await state.set_state(ContentStates.waiting_for_puzzle_answers)
    await message.answer("Теперь отправьте три варианта ответа через запятую")

@router.message(ContentStates.waiting_for_puzzle_answers)
async def process_puzzle_answers(message: Message, state: FSMContext):
    answers = [answer.strip() for answer in message.text.split(",")]
    if len(answers) != 3:
        await message.answer("Пожалуйста, отправьте ровно три варианта ответа через запятую")
        return
        
    data = await state.get_data()
    image_bytes = data["puzzle_image"]
    
    db = Database()
    try:
        await db.add_puzzle(image_bytes, answers[0], answers[1], answers[2])
        await message.answer("✅ Ребус успешно добавлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении ребуса: {str(e)}")
    
    await state.clear()

@router.message(ContentStates.waiting_for_twister)
async def process_twister(message: Message, state: FSMContext):
    """Обрабатывает добавление скороговорки"""
    db = Database()
    await db.add_tongue_twister(message.text)
    
    await state.clear()
    await message.answer(
        "✅ Скороговорка успешно добавлена!",
        reply_markup=AdminKeyboard.get_menu_keyboard()
    )

@router.message(ContentStates.waiting_for_riddle)
async def process_riddle(message: Message, state: FSMContext):
    """Обрабатывает добавление загадки"""
    await state.update_data(riddle_text=message.text)
    await state.set_state(ContentStates.waiting_for_riddle_answer)
    await message.answer("Введите ответ на загадку:")

@router.message(ContentStates.waiting_for_riddle_answer)
async def process_riddle_answer(message: Message, state: FSMContext):
    """Обрабатывает ответ на загадку"""
    data = await state.get_data()
    
    db = Database()
    await db.add_riddle(data['riddle_text'], message.text)
    
    await state.clear()
    await message.answer(
        "✅ Загадка успешно добавлена!",
        reply_markup=AdminKeyboard.get_menu_keyboard()
    )

@router.message(ContentStates.waiting_for_daily_task)
async def process_daily_task(message: Message, state: FSMContext):
    """Обрабатывает добавление ежедневного задания"""
    db = Database()
    await db.add_daily_task(message.text)
    
    await state.clear()
    await message.answer(
        "✅ Задание успешно добавлено!",
        reply_markup=AdminKeyboard.get_menu_keyboard()
    )

@router.callback_query(F.data.in_({"back_to_admin", "back_to_content", "back_to_subscriptions"}))
async def process_back_button(callback: CallbackQuery):
    """Обрабатывает нажатие кнопок "Назад" """
    if callback.data == "back_to_admin":
        await show_admin_menu(callback)
    elif callback.data == "back_to_content":
        await show_content_menu(callback)
    elif callback.data == "back_to_subscriptions":
        await show_subscriptions_list(callback)

@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отменяет текущее действие"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено",
        reply_markup=AdminKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    """Возвращает в главное меню админ-панели и очищает состояние"""
    await state.clear()
    await callback.message.edit_text(
        "⚙️ Панель администратора\nВыберите раздел для управления:",
        reply_markup=AdminKeyboard.get_menu_keyboard()
    )

@router.callback_query(F.data == "back_to_content_menu")
async def back_to_content_menu(callback: CallbackQuery, state: FSMContext):
    """Возвращает в меню управления контентом и очищает состояние"""
    await state.clear()
    await callback.message.edit_text(
        "📝 Управление контентом\nВыберите тип контента:",
        reply_markup=AdminKeyboard.get_content_keyboard()
    )

@router.message(ContentStates.waiting_for_exercise_title)
async def process_exercise_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ContentStates.waiting_for_exercise_description)
    await message.answer("Введите описание упражнения:")

@router.message(ContentStates.waiting_for_exercise_description)
async def process_exercise_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ContentStates.waiting_for_exercise_video)
    await message.answer("Отправьте ссылку на видео упражнения:")

@router.message(ContentStates.waiting_for_exercise_video)
async def process_exercise_video(message: Message, state: FSMContext):
    data = await state.get_data()
    db = Database()
    try:
        await db.add_exercise_video(
            data['title'], 
            data['description'], 
            message.text,
            data['content_type']
        )
        await message.answer("✅ Упражнение успешно добавлено!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении упражнения: {str(e)}")
    await state.clear()

@router.message(ContentStates.waiting_for_creativity_title)
async def process_creativity_title(message: Message, state: FSMContext):
    """Обрабатывает название мастер-класса"""
    data = await state.get_data()
    await state.update_data(title=message.text)
    await state.set_state(ContentStates.waiting_for_creativity_description)
    await message.answer("Введите описание мастер-класса:")

@router.message(ContentStates.waiting_for_creativity_description)
async def process_creativity_description(message: Message, state: FSMContext):
    """Обрабатывает описание мастер-класса"""
    await state.update_data(description=message.text)
    await state.set_state(ContentStates.waiting_for_creativity_video)
    await message.answer("Отправьте ссылку на видео мастер-класса:")

@router.message(ContentStates.waiting_for_creativity_video)
async def process_creativity_video(message: Message, state: FSMContext):
    """Обрабатывает ссылку на видео мастер-класса"""
    data = await state.get_data()
    content_type = data.get('content_type')
    creativity_type = content_type.split('_')[1] if content_type else None
    
    db = Database()
    try:
        await db.add_creativity_video(
            title=data['title'],
            description=data['description'],
            video_url=message.text,
            video_type=creativity_type
        )
        await message.answer(
            "✅ Мастер-класс успешно добавлен!",
            reply_markup=AdminKeyboard.get_menu_keyboard()
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении мастер-класса: {str(e)}")
    
    await state.clear()

@router.callback_query(F.data.startswith("delete_content:"))
async def delete_content_confirmation(callback: CallbackQuery):
    """Запрашивает подтверждение удаления контента"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    # Получаем тип контента и id
    _, content_type, content_id = callback.data.split(":")
    
    await callback.message.edit_text(
        "❗ Вы уверены, что хотите удалить этот элемент?\n"
        "Это действие нельзя будет отменить.",
        reply_markup=AdminKeyboard.get_delete_confirmation_keyboard(content_type, content_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_content(callback: CallbackQuery):
    """Подтверждает удаление контента"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    # Получаем тип контента и id
    _, content_type, content_id = callback.data.split(":")
    content_id = int(content_id)
    
    db = Database()
    if await db.delete_content(content_type, content_id):
        await callback.answer("✅ Элемент успешно удален!", show_alert=True)
        
        # Получаем список контента заново
        items = []
        if content_type == "daily":
            items = await db.get_all_daily_tasks()
        elif content_type == "riddles":
            items = await db.get_all_riddles()
        elif content_type == "twisters":
            items = await db.get_all_tongue_twisters()
        elif content_type == "puzzles":
            items = await db.get_all_puzzles()
        elif content_type.startswith("creativity_"):
            creativity_type = content_type.split("_")[1]
            items = await db.get_all_creativity(creativity_type)
        elif content_type == "articular":
            items = await db.get_exercise_videos("articular")
        elif content_type == "neuro":
            items = await db.get_exercise_videos("neuro")
        
        total_pages = math.ceil(len(items) / ITEMS_PER_PAGE)
        current_page = 1  # Возвращаемся на первую страницу после удаления
        
        # Формируем заголовок в зависимости от типа контента
        headers = {
            "daily": "📝 Список заданий на день",
            "riddles": "🤔 Список загадок",
            "twisters": "👅 Список скороговорок",
            "puzzles": "🧩 Список ребусов",
            "creativity_drawing": "🎨 Список мастер-классов по рисованию",
            "creativity_paper": "📄 Список мастер-классов по бумаге",
            "creativity_sculpting": "🏺 Список мастер-классов по лепке",
            "articular": "🗣 Список упражнений для артикуляции",
            "neuro": "🧠 Список упражнений для нейрогимнастики"
        }
        
        header = headers.get(content_type, "📋 Список элементов")
        
        # Обновляем сообщение с обновленным списком
        await callback.message.edit_text(
            text=f"{header}\n\nСтраница {current_page}/{total_pages}",
            reply_markup=AdminKeyboard.get_content_list_keyboard(items, current_page, total_pages, content_type)
        )
    else:
        await callback.answer("❌ Ошибка при удалении элемента", show_alert=True)

@router.callback_query(F.data.startswith("view_content:"))
async def view_content(callback: CallbackQuery):
    """Показывает детали контента"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    # Получаем тип контента и id
    _, content_type, content_id = callback.data.split(":")
    content_id = int(content_id)
    
    db = Database()
    # Здесь можно добавить логику просмотра деталей контента
    await callback.answer("🔍 Просмотр деталей контента (функционал в разработке)", show_alert=True)

@router.callback_query(F.data == "admin_tokens")
async def show_tokens_list(callback: CallbackQuery, page: int = 1):
    """Показывает список жетонов пользователей"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    db = Database()
    tokens = await db.get_all_tokens()
    
    total_pages = math.ceil(len(tokens) / ITEMS_PER_PAGE)
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    current_tokens = tokens[start_idx:end_idx]
    
    await callback.message.edit_text(
        f"🏆 Список жетонов (страница {page}/{total_pages}):",
        reply_markup=AdminKeyboard.get_tokens_keyboard(current_tokens, page, total_pages)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("tokens_page_"))
async def navigate_tokens(callback: CallbackQuery):
    """Обрабатывает навигацию по страницам жетонов"""
    page = int(callback.data.split("_")[2])
    await show_tokens_list(callback, page)

@router.callback_query(F.data.startswith("token_"))
async def edit_token(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс редактирования токена"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    token_id = int(callback.data.split("_")[1])
    await state.update_data(token_id=token_id)
    await state.set_state(TokenStates.waiting_for_emoji)
    await callback.message.edit_text(
        "Отправьте новый эмодзи для токена:\n\n"
        "📝 Требования:\n"
        "• Отправьте только один эмодзи\n"
        "• Не используйте текст или цифры\n\n"
        "✨ Примеры:\n"
        "• 🌟 - звезда\n"
        "• 🎨 - палитра\n"
        "• 🎯 - мишень\n"
        "• 🏆 - кубок\n"
        "• 🎮 - геймпад",
        reply_markup=AdminKeyboard.get_cancel_keyboard()
    )
    await callback.answer()

@router.message(TokenStates.waiting_for_emoji)
async def process_token_emoji(message: Message, state: FSMContext):
    """Обрабатывает новый эмодзи для токена"""
    db = Database()
    if not db.is_valid_emoji(message.text):
        await message.answer(
            "❌ Пожалуйста, отправьте только один эмодзи\n\n"
            "✨ Примеры:\n"
            "• 🌟 - звезда\n"
            "• 🎨 - палитра\n"
            "• 🎯 - мишень\n"
            "• 🏆 - кубок\n"
            "• 🎮 - геймпад"
        )
        return
    
    await state.update_data(emoji=message.text)
    await state.set_state(TokenStates.waiting_for_name)
    await message.answer(
        "Теперь отправьте новое название для токена:\n\n"
        "📝 Требования:\n"
        "• Используйте только буквы и пробелы\n"
        "• Название должно быть понятным и кратким\n\n"
        "✨ Примеры:\n"
        "• Звезда творчества\n"
        "• Кубок мастера\n"
        "• Знак отличия\n"
        "• Медаль успеха"
    )

@router.message(TokenStates.waiting_for_name)
async def process_token_name(message: Message, state: FSMContext):
    """Обрабатывает новое название для токена"""
    db = Database()
    if not db.is_valid_name(message.text):
        await message.answer(
            "❌ Название должно содержать только буквы и пробелы\n\n"
            "📝 Требования:\n"
            "• Используйте только буквы и пробелы\n"
            "• Название должно быть понятным и кратким\n\n"
            "✨ Примеры:\n"
            "• Звезда творчества\n"
            "• Кубок мастера\n"
            "• Знак отличия\n"
            "• Медаль успеха"
        )
        return
    
    data = await state.get_data()
    token_id = data['token_id']
    new_emoji = data['emoji']
    new_name = message.text
    
    if await db.update_token(token_id, new_emoji, new_name):
        await message.answer("✅ Токен успешно обновлен!")
        
        # Показываем обновленный список токенов
        tokens = await db.get_all_tokens()
        total_pages = math.ceil(len(tokens) / ITEMS_PER_PAGE)
        await message.answer(
            f"🏆 Список токенов (страница 1/{total_pages}):",
            reply_markup=AdminKeyboard.get_tokens_keyboard(tokens[:ITEMS_PER_PAGE], 1, total_pages)
        )
    else:
        await message.answer("❌ Ошибка при обновлении токена")
    
    await state.clear() 