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
            ("🎨 Творчество", "creativity"),
            ("🧩 Ребусы", "puzzles"),
            ("❓ Загадки", "riddles"),
            ("🎯 Ежедневные задания", "daily_tasks"),
            ("🏆 Достижения", "achievements"),
            ("🤸‍♂️ Артикулярная гимнастика", "articular_gym"),
            ("👄 Скороговорки", "tongue_twisters"),
            ("🧠 Нейрогимнастика", "neuro_gym"),
            ("👩‍👦 Для мам", "for_moms")
        ]
        
        # Добавляем основные кнопки
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
            
        # Добавляем кнопку админ-панели только для администраторов
        if user_id in config.ADMIN_IDS:
            kb.add(InlineKeyboardButton(
                text="👑 Админ панель",
                callback_data="admin_panel"
            ))
            
        kb.adjust(1)  # Устанавливаем по 1 кнопке в ряд
        
        return kb.as_markup() 