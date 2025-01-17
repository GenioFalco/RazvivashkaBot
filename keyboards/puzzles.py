from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class PuzzlesKeyboard:
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру для меню ребусов"""
        kb = InlineKeyboardBuilder()
        kb.button(text="🎯 Решать", callback_data="start_puzzles")
        kb.button(text="↩️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_puzzle_keyboard(puzzle_id: int, solved_status: list[bool]) -> InlineKeyboardMarkup:
        """Создает клавиатуру для конкретного ребуса"""
        kb = InlineKeyboardBuilder()
        
        # Кнопки для ответов на ребусы
        for i, solved in enumerate(solved_status, 1):
            if not solved:
                kb.button(
                    text=f"✍️ Ответить на {i} ребус",
                    callback_data=f"answer_puzzle_{puzzle_id}_{i}"
                )
        
        # Кнопка просмотра ответов
        kb.button(text="👀 Смотреть ответы", callback_data=f"show_answers_{puzzle_id}")
        
        # Кнопка "Назад"
        kb.button(text="↩️ Назад", callback_data="back_to_puzzles_menu")
        
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_next_puzzle_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру для перехода к следующему ребусу"""
        kb = InlineKeyboardBuilder()
        kb.button(text="➡️ Продолжить", callback_data="next_puzzle")
        kb.button(text="↩️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_cancel_keyboard(puzzle_id: int, rebus_number: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру с кнопкой отмены"""
        kb = InlineKeyboardBuilder()
        kb.button(
            text="↩️ Назад",
            callback_data=f"cancel_puzzle_answer_{puzzle_id}_{rebus_number}"
        )
        return kb.as_markup() 