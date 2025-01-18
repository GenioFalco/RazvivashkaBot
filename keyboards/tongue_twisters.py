from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class TongueTwistersKeyboard:
    """Класс для создания клавиатур раздела скороговорок"""
    
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Создает основную клавиатуру раздела"""
        kb = InlineKeyboardBuilder()
        
        buttons = [
            ("🎯 Начать", "start_tongue_twisters"),
            ("↩️ В главное меню", "back_to_main")
        ]
        
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        kb.adjust(1)
        
        return kb.as_markup()
    
    @staticmethod
    def get_navigation_keyboard(current_index: int, total_twisters: int, twister_id: int, is_completed: bool = False) -> InlineKeyboardMarkup:
        """Создает клавиатуру навигации по скороговоркам"""
        kb = InlineKeyboardBuilder()
        
        # Кнопки для отметки выполнения добавляем только если скороговорка не выполнена
        if not is_completed:
            kb.add(InlineKeyboardButton(
                text="✅ Выполнил",
                callback_data=f"complete_twister_{twister_id}"
            ))
            kb.add(InlineKeyboardButton(
                text="❌ Не выполнил",
                callback_data=f"skip_twister_{twister_id}"
            ))
        
        # Кнопки навигации
        buttons = []
        if current_index > 0:
            buttons.append(("⬅️ Предыдущая", f"prev_{current_index}"))
        if current_index < total_twisters - 1:
            buttons.append(("Следующая ➡️", f"next_{current_index}"))
            
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        
        # Кнопка "Назад"
        kb.add(InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="back_to_tongue_twisters"
        ))
        
        # Размещаем кнопки: сначала кнопки выполнения в один ряд (если есть),
        # затем кнопки навигации в один ряд, и кнопку "Назад" отдельно
        if not is_completed:
            kb.adjust(2, len(buttons), 1)
        else:
            kb.adjust(len(buttons), 1)
        
        return kb.as_markup()
    
    @staticmethod
    def get_back_button() -> InlineKeyboardMarkup:
        """Создает клавиатуру только с кнопкой "Назад" """
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="back_to_tongue_twisters"
        ))
        return kb.as_markup() 