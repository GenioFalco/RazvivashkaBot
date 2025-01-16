from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class AchievementsKeyboard:
    """Класс для создания клавиатур раздела достижений"""
    
    @staticmethod
    def get_main_keyboard() -> InlineKeyboardMarkup:
        """Создает основную клавиатуру раздела достижений"""
        kb = InlineKeyboardBuilder()
        
        buttons = [
            ("📸 Фотоальбом", "photo_album"),
            ("🏆 Достижения", "achievements_list"),
            ("↩️ Назад", "back_to_main")
        ]
        
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        kb.adjust(1)
        return kb.as_markup()
    
    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """Создает клавиатуру с кнопкой возврата"""
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="back_to_achievements"
        ))
        return kb.as_markup() 