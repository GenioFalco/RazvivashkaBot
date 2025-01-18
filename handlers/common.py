from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.main_menu import MainMenuKeyboard
from keyboards.achievements import AchievementsKeyboard
from database.database import Database
from config import config
import re

router = Router()

class TokenEditStates(StatesGroup):
    waiting_for_emoji = State()
    waiting_for_name = State()

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру админ-панели"""
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users"))
    kb.add(InlineKeyboardButton(text="🏆 Управление жетонами", callback_data="manage_tokens"))
    kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main"))
    kb.adjust(1)
    return kb.as_markup()

async def get_tokens_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру со списком жетонов для редактирования"""
    kb = InlineKeyboardBuilder()
    db = Database()
    tokens = await db.get_all_tokens()
    
    for token in tokens:
        kb.add(InlineKeyboardButton(
            text=f"{token['emoji']} {token['name']}", 
            callback_data=f"edit_token_{token['id']}"
        ))
    
    kb.add(InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin"))
    kb.adjust(1)
    return kb.as_markup()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    db = Database()
    await db.create_tables()
    
    await db.add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    
    await message.answer(
        "Привет! Я бот-развивашка! 🌟\n"
        "Я помогу тебе развиваться и получать награды за достижения!\n\n"
        "Выбери интересующий тебя раздел в меню:",
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

@router.callback_query(F.data == "manage_tokens")
async def manage_tokens_callback(callback: CallbackQuery):
    """Обработчик кнопки управления жетонами"""
    if callback.from_user.id in config.ADMIN_IDS:
        db = Database()
        tokens = await db.get_all_tokens()
        response = "Список жетонов:\n\n"
        for token in tokens:
            response += f"{token['emoji']} {token['name']}\n"
        
        response += "\nНажмите на жетон, который хотите отредактировать:"
        
        await callback.message.edit_text(
            response,
            reply_markup=await get_tokens_keyboard()
        )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_token_"))
async def start_token_edit(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования жетона"""
    token_id = int(callback.data.split('_')[2])
    db = Database()
    token = await db.get_token_by_id(token_id)
    await state.update_data(token_id=token_id, old_emoji=token['emoji'], old_name=token['name'])
    await state.set_state(TokenEditStates.waiting_for_emoji)
    
    await callback.message.edit_text(
        f"Текущий жетон: {token['emoji']} {token['name']}\n\n"
        "Отправьте новый эмодзи для жетона.\n"
        "Примеры: ⭐ 🌟 🎯 🎨 🎭\n\n"
        "Для отмены нажмите кнопку ниже.",
        reply_markup=InlineKeyboardBuilder().add(
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")
        ).as_markup()
    )
    await callback.answer()

@router.message(TokenEditStates.waiting_for_emoji)
async def process_token_emoji(message: Message, state: FSMContext):
    """Обработка нового эмодзи для жетона"""
    if not re.match(r'^[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]$', message.text):
        await message.answer(
            "Это не эмодзи! Пожалуйста, отправьте один эмодзи.\n"
            "Примеры: ⭐ 🌟 🎯 🎨 🎭\n\n"
            "Для отмены нажмите кнопку ниже.",
            reply_markup=InlineKeyboardBuilder().add(
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")
            ).as_markup()
        )
        return

    data = await state.get_data()
    await state.update_data(new_emoji=message.text)
    await state.set_state(TokenEditStates.waiting_for_name)
    
    await message.answer(
        f"Текущий жетон: {data['old_emoji']} {data['old_name']}\n"
        f"Новый эмодзи: {message.text}\n\n"
        "Теперь отправьте новое название для жетона.\n"
        "Примеры: Звездочка, Солнышко, Радуга\n"
        "Используйте только русские и английские буквы.\n\n"
        "Для отмены нажмите кнопку ниже.",
        reply_markup=InlineKeyboardBuilder().add(
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")
        ).as_markup()
    )

@router.message(TokenEditStates.waiting_for_name)
async def process_token_name(message: Message, state: FSMContext):
    """Обработка нового названия для жетона"""
    if not re.match(r'^[а-яА-Яa-zA-Z\s]+$', message.text):
        data = await state.get_data()
        await message.answer(
            f"Неверный формат названия!\n\n"
            f"Текущий жетон: {data['old_emoji']} {data['old_name']}\n"
            f"Новый эмодзи: {data['new_emoji']}\n\n"
            "Отправьте название, используя только русские и английские буквы.\n"
            "Примеры: Звездочка, Солнышко, Радуга\n\n"
            "Для отмены нажмите кнопку ниже.",
            reply_markup=InlineKeyboardBuilder().add(
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")
            ).as_markup()
        )
        return

    data = await state.get_data()
    db = Database()
    
    success = await db.update_token(
        token_id=data['token_id'],
        new_emoji=data['new_emoji'],
        new_name=message.text
    )
    
    if success:
        await message.answer(
            "✅ Жетон успешно обновлен!\n\n"
            f"Было: {data['old_emoji']} {data['old_name']}\n"
            f"Стало: {data['new_emoji']} {message.text}",
            reply_markup=await get_tokens_keyboard()
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при обновлении жетона.",
            reply_markup=await get_tokens_keyboard()
        )
    
    await state.clear()

@router.callback_query(F.data == "cancel_edit")
async def cancel_token_edit(callback: CallbackQuery, state: FSMContext):
    """Отмена редактирования жетона"""
    await state.clear()
    await callback.message.edit_text(
        "Редактирование отменено.",
        reply_markup=await get_tokens_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_admin")
async def back_to_admin_panel(callback: CallbackQuery, state: FSMContext):
    """Возвращает в админ-панель"""
    await state.clear()
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.in_({
    "creativity",
    "articular_gym", "neuro_gym",
    "for_moms"
}))
async def process_callback(callback: CallbackQuery):
    """Обработчик остальных кнопок меню"""
    responses = {
        "creativity": "🎨 Раздел Творчество в разработке",
        "articular_gym": "🤸‍♂️ Раздел Артикулярная гимнастика в разработке",
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
    """Обработчик возврата в главное меню"""
    await callback.message.edit_text(
        "Выбери интересующий тебя раздел:",
        reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
    )
    await callback.answer() 