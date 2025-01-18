from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class CreativityKeyboard:
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру главного меню раздела творчества"""
        builder = InlineKeyboardBuilder()
        
        # Добавляем кнопки разделов
        builder.row(InlineKeyboardButton(text="🎨 Рисовать", callback_data="creativity_drawing"))
        builder.row(InlineKeyboardButton(text="📄 Бумага", callback_data="creativity_paper"))
        builder.row(InlineKeyboardButton(text="🏺 Лепка", callback_data="creativity_sculpting"))
        builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_menu"))
        
        return builder.as_markup()

    @staticmethod
    def get_section_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для конкретного раздела"""
        builder = InlineKeyboardBuilder()
        
        builder.row(InlineKeyboardButton(text="▶️ Начать", callback_data="start_masterclass"))
        builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_creativity"))
        
        return builder.as_markup()

    @staticmethod
    def get_masterclass_keyboard(video_id: int, is_completed: bool = False) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для мастер-класса"""
        builder = InlineKeyboardBuilder()
        
        if not is_completed:
            # Кнопки для невыполненного мастер-класса
            builder.row(
                InlineKeyboardButton(text="✅ Выполнил", callback_data=f"complete_masterclass_{video_id}"),
                InlineKeyboardButton(text="⏳ Выполнить позже", callback_data=f"postpone_masterclass_{video_id}")
            )
        
        # Кнопка для отправки фото
        builder.row(InlineKeyboardButton(text="📸 Отправить фото", callback_data=f"send_photo_{video_id}"))
        
        if is_completed:
            # Кнопки навигации для выполненного мастер-класса
            builder.row(
                InlineKeyboardButton(text="⬅️ Предыдущий", callback_data=f"prev_masterclass_{video_id}"),
                InlineKeyboardButton(text="➡️ Следующий", callback_data=f"next_masterclass_{video_id}")
            )
        
        # Кнопка "Назад"
        builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_creativity"))
        
        return builder.as_markup()

    @staticmethod
    def get_photo_cancel_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для отмены отправки фото"""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_photo"))
        return builder.as_markup() 