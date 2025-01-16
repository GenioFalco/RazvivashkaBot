from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class DailyTasksKeyboard:
    """Класс для создания клавиатур раздела ежедневных заданий"""
    
    @staticmethod
    def get_main_keyboard() -> InlineKeyboardMarkup:
        """Создает основную клавиатуру раздела"""
        kb = InlineKeyboardBuilder()
        
        buttons = [
            ("📝 Задания", "show_daily_tasks"),
            ("↩️ Назад", "back_to_main")
        ]
        
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        kb.adjust(1)
        
        return kb.as_markup()
    
    @staticmethod
    def get_task_keyboard(task_id: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру для конкретного задания"""
        kb = InlineKeyboardBuilder()
        
        buttons = [
            ("✅ Сделал", f"complete_task_{task_id}"),
            ("❌ Не сделал", f"skip_task_{task_id}"),
            ("↩️ Назад", "back_to_daily_tasks")
        ]
        
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        kb.adjust(1)
        
        return kb.as_markup()
    
    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """Создает клавиатуру только с кнопкой "Назад" """
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_daily_tasks"))
        return kb.as_markup() 