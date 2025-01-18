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
        kb = InlineKeyboardBuilder()
        
        buttons = [
            ("📝 Задания на день", "daily_tasks"),
            ("❓ Загадки", "riddles"),
            ("🧩 Ребусы", "puzzles"),
            ("👄 Скороговорки", "tongue_twisters"),
            ("🧠 Нейрогимнастика", "neuro_exercises"),
            ("🤸 Артикулярная гимнастика", "articular_exercises"),
            ("🏆 Достижения", "achievements")
        ]
        
        # Добавляем кнопку админ-панели для администраторов
        if user_id in config.ADMIN_IDS:
            buttons.append(("⚙️ Админ панель", "admin_panel"))
        
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        
        kb.adjust(1)  # Размещаем кнопки в один столбец
        return kb.as_markup() 