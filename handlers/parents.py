from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.database import Database
from keyboards.parents import ParentsKeyboard
from keyboards.main_menu import MainMenuKeyboard
from datetime import datetime

router = Router()

@router.callback_query(F.data == "for_parents")
async def show_parents_menu(callback: CallbackQuery):
    """Показывает главное меню раздела для мам"""
    await callback.message.edit_text(
        "👋 Добро пожаловать в раздел для родителей!\n\n"
        "Здесь вы можете:\n"
        "• Управлять подпиской\n"
        "• Получить реферальную ссылку\n"
        "• Приглашать друзей и получать бонусы\n\n"
        "Выберите интересующий вас раздел:",
        reply_markup=ParentsKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "referral_link")
async def show_referral_info(callback: CallbackQuery):
    """Показывает информацию о реферальной программе"""
    db = Database()
    stats = await db.get_referral_stats(callback.from_user.id)
    link = await db.get_referral_link(callback.from_user.id)
    
    text = (
        "🤝 Реферальная программа\n\n"
        "Приглашайте друзей и получайте бонусные дни подписки!\n"
        "За каждого друга, который активирует подписку, вы получите +5 дней.\n\n"
        f"👥 Ваши приглашенные друзья: {stats['total']}\n"
        f"✅ Активировали подписку: {stats['active']}\n\n"
        "Ваша реферальная ссылка:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=ParentsKeyboard.get_referral_keyboard(link)
    )
    await callback.answer()

@router.callback_query(F.data == "copy_referral")
async def copy_referral_link(callback: CallbackQuery):
    """Копирует реферальную ссылку"""
    db = Database()
    link = await db.get_referral_link(callback.from_user.id)
    await callback.answer("Ссылка скопирована!", show_alert=True)

@router.callback_query(F.data == "back_to_parents")
async def back_to_parents(callback: CallbackQuery):
    """Возвращает в главное меню раздела для мам"""
    await show_parents_menu(callback)

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Возвращает в главное меню"""
    await callback.message.edit_text(
        "Выберите раздел:",
        reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
    )
    await callback.answer() 