from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config

class MainMenuKeyboard:
    """Класс для создания клавиатуры главного меню"""
    
    @staticmethod
    def get_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
        """
        Создает и возвращает inline-клавиатуру главного меню
        
        Args:
            user_id (int): ID пользователя для проверки прав администратора
        """
        builder = InlineKeyboardBuilder()
        
        # Основные разделы
        builder.button(text="📝 Задания на день", callback_data="daily_tasks")
        builder.button(text="🎨 Творчество", callback_data="creativity")
        builder.button(text="🧩 Ребусы", callback_data="puzzles")
        builder.button(text="❓ Загадки", callback_data="riddles")
        builder.button(text="👄 Скороговорки", callback_data="tongue_twisters")
        
        # Упражнения
        builder.button(text="🧠 Нейрогимнастика", callback_data="neuro_exercises")
        builder.button(text="👅 Артикуляция", callback_data="articular_exercises")
        
        # Дополнительные разделы
        builder.button(text="🏆 Достижения", callback_data="achievements")
        builder.button(text="🖼 Доска для всех", callback_data="photo_board")
        builder.button(text="👩‍👦 Для мам", callback_data="for_parents")
        
        # Админ-панель (если пользователь админ)
        if user_id in config.ADMIN_IDS:
            builder.button(text="⚙️ Админ-панель", callback_data="admin_panel")
        
        # Устанавливаем по одной кнопке в ряд, кроме упражнений
        builder.adjust(1, 2, 1, 1, 1)
        return builder.as_markup() 