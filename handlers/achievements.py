from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.achievements import AchievementsKeyboard
from database.database import Database

router = Router()

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

@router.callback_query(F.data == "achievements_list")
async def show_achievements_list(callback: CallbackQuery):
    """Показывает список достижений пользователя"""
    db = Database()
    user_achievements = await db.get_user_achievements(callback.from_user.id)
    tokens = await db.get_all_tokens()
    
    message = (
        "🌟 Твои достижения:\n\n"
    )
    
    for token in tokens:
        count = user_achievements.get(token['id'], 0)
        message += f"{token['emoji']} {token['name']}: {count} шт.\n"
        message += f"└ {token['description']}\n\n"
    
    await callback.message.edit_text(
        message,
        reply_markup=AchievementsKeyboard.get_back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_achievements")
async def back_to_achievements(callback: CallbackQuery):
    """Возвращает в главное меню достижений"""
    await show_achievements_menu(callback) 