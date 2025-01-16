from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.main_menu import MainMenuKeyboard
from keyboards.achievements import AchievementsKeyboard
from database.database import Database
from config import config

router = Router()

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру админ-панели"""
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users"))
    kb.add(InlineKeyboardButton(text="🏆 Управление жетонами", callback_data="manage_tokens"))
    kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main"))
    kb.adjust(1)
    return kb.as_markup()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    db = Database()
    await db.create_tables()
    
    # Добавляем пользователя в базу данных
    await db.add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    
    # Отправляем приветственное сообщение с клавиатурой, учитывая права пользователя
    await message.answer(
        "Вас приветствует бот Развивашка!\n"
        "Здесь вы можете найти множество техник для совместного времяпровождения с ребенком.",
        reply_markup=MainMenuKeyboard.get_keyboard(user_id=message.from_user.id)
    )

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    """Обработчик кнопки админ панели"""
    if callback.from_user.id in config.ADMIN_IDS:
        await callback.message.edit_text(
            "Выберите действие:",
            reply_markup=get_admin_keyboard()
        )
    else:
        await callback.message.answer("У вас нет доступа к админ панели.")
    await callback.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users_callback(callback: CallbackQuery):
    """Обработчик кнопки списка пользователей"""
    if callback.from_user.id in config.ADMIN_IDS:
        db = Database()
        users = await db.get_all_users()
        response = "Список пользователей:\n\n"
        for user in users:
            response += f"ID: {user['telegram_id']}\n"
            response += f"Имя: {user['full_name']}\n"
            response += f"Username: {user['username']}\n"
            response += f"Дата регистрации: {user['registration_date']}\n"
            response += "-" * 20 + "\n"
        await callback.message.edit_text(
            response,
            reply_markup=get_admin_keyboard()
        )
    await callback.answer()

@router.callback_query(F.data.in_({
    "creativity", "puzzles", "riddles",
    "articular_gym", "tongue_twisters", "neuro_gym",
    "for_moms"
}))
async def process_callback(callback: CallbackQuery):
    """Обработчик остальных кнопок меню"""
    responses = {
        "creativity": "🎨 Раздел Творчество в разработке",
        "puzzles": "🧩 Раздел Ребусы в разработке",
        "riddles": "❓ Раздел Загадки в разработке",
        "articular_gym": "🤸‍♂️ Раздел Артикулярная гимнастика в разработке",
        "tongue_twisters": "👄 Раздел Скороговорки в разработке",
        "neuro_gym": "🧠 Раздел Нейрогимнастика в разработке",
        "for_moms": "👩‍👦 Раздел Для мам в разработке"
    }
    await callback.message.edit_text(
        responses[callback.data],
        reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Обработчик кнопки возврата в главное меню"""
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
    )
    await callback.answer() 