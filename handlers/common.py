from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from database.database import Database
from keyboards.main_menu import MainMenuKeyboard
import config

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    # Добавляем пользователя в базу данных
    db = Database()
    await db.add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    
    await message.answer(
        "👋 Привет! Я бот-развивашка!\n\n"
        "Я помогу тебе развить:\n"
        "• Речь\n"
        "• Мышление\n"
        "• Память\n"
        "• Воображение\n"
        "• Мелкую моторику\n\n"
        "Выбери интересующий тебя раздел в меню ниже:",
        reply_markup=MainMenuKeyboard.get_keyboard(message.from_user.id)
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Обработчик команды /menu"""
    await message.answer(
        "Выберите раздел:",
        reply_markup=MainMenuKeyboard.get_keyboard(message.from_user.id)
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возвращает в главное меню"""
    await callback.message.answer(
        "Выберите раздел:",
        reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
    )
    await callback.answer()

@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery):
    """Показывает админ-панель"""
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("У вас нет доступа к админ-панели", show_alert=True)
        return
    
    await callback.message.answer(
        "⚙️ Админ-панель временно недоступна",
        reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
    )
    await callback.answer() 