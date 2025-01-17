from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class RiddlesKeyboard:
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру для меню загадок"""
        kb = InlineKeyboardBuilder()
        kb.button(text="🎯 Загадки", callback_data="start_riddles")
        kb.button(text="↩️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_navigation_keyboard(current_index: int, total_riddles: int, is_completed: bool = False) -> InlineKeyboardMarkup:
        """Создает клавиатуру навигации по загадкам"""
        kb = InlineKeyboardBuilder()
        
        # Кнопки навигации
        if current_index > 0:
            kb.button(text="⬅️ Предыдущая", callback_data=f"prev_riddle_{current_index}")
        if current_index < total_riddles - 1:
            kb.button(text="Следующая ➡️", callback_data=f"next_riddle_{current_index}")
        kb.adjust(2)
        
        # Кнопки действий
        if not is_completed:
            kb.button(text="✍️ Ответить", callback_data=f"answer_riddle_{current_index}")
        kb.button(text="👀 Смотреть ответ", callback_data=f"show_answer_{current_index}")
        kb.button(text="↩️ Назад", callback_data="back_to_riddles_menu")
        kb.adjust(1)
        
        return kb.as_markup()

    @staticmethod
    def get_cancel_keyboard(current_index: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру с кнопкой отмены"""
        kb = InlineKeyboardBuilder()
        kb.button(text="↩️ Назад", callback_data=f"cancel_answer_{current_index}")
        return kb.as_markup() 