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
        
        # Добавляем кнопки в одну колонку
        kb.add(InlineKeyboardButton(text="❓ Загадки", callback_data="riddles"))
        kb.add(InlineKeyboardButton(text="🧠 Нейрогимнастика", callback_data="neuro_exercises"))
        kb.add(InlineKeyboardButton(text="🤸 Артикулярная гимнастика", callback_data="articular_exercises"))
        kb.add(InlineKeyboardButton(text="📅 Ежедневные задания", callback_data="daily_tasks"))
        kb.add(InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements"))
        
        # Добавляем кнопку админ-панели только для администраторов
        if user_id in config.ADMIN_IDS:
            kb.add(InlineKeyboardButton(
                text="⚙️ Админ панель",
                callback_data="admin_panel"
            ))
            
        # Устанавливаем одну кнопку в строке
        kb.adjust(1)
        
        return kb.as_markup() 