from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ExercisesKeyboard:
    """Класс для создания клавиатур разделов упражнений"""
    
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру меню упражнений"""
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📺 Смотреть", callback_data="watch_exercise"))
        builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_exercise_menu"))
        return builder.as_markup()
    
    @staticmethod
    def get_exercise_keyboard(video_id: int, show_completion: bool = True) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для видео упражнения"""
        builder = InlineKeyboardBuilder()
        
        # Кнопки навигации
        builder.row(
            InlineKeyboardButton(text="⬅️ Предыдущее", callback_data=f"prev_video_{video_id}"),
            InlineKeyboardButton(text="➡️ Следующее", callback_data=f"next_video_{video_id}")
        )
        
        if show_completion:
            # Кнопки отметки выполнения
            builder.row(
                InlineKeyboardButton(text="✅ Сделал все получилось", callback_data=f"exercise_full_{video_id}")
            )
            builder.row(
                InlineKeyboardButton(text="👍 Сделал не все получилось", callback_data=f"exercise_partial_{video_id}")
            )
            builder.row(
                InlineKeyboardButton(text="❌ Не сделал", callback_data=f"exercise_not_done_{video_id}")
            )
        
        builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_exercise_menu"))
        return builder.as_markup() 