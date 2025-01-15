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
            ("📊 Рейтинг", "achievements_rating"),
            ("↩️ Назад", "back_to_main")
        ]
        
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        kb.adjust(1)
        
        return kb.as_markup()

    @staticmethod
    def get_admin_tokens_keyboard(tokens: list) -> InlineKeyboardMarkup:
        """Создает клавиатуру управления токенами для админа"""
        kb = InlineKeyboardBuilder()
        
        # Добавляем кнопки для каждого токена
        for token in tokens:
            kb.add(InlineKeyboardButton(
                text=f"{token['emoji']} {token['name']}", 
                callback_data=f"edit_token_{token['id']}"
            ))
        
        # Добавляем кнопку "Назад"
        kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_admin"))
        
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """Создает клавиатуру только с кнопкой "Назад" """
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_achievements"))
        return kb.as_markup() 