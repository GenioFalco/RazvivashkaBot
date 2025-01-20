from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

ITEMS_PER_PAGE = 5

class AdminKeyboard:
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру главного меню админ-панели"""
        builder = InlineKeyboardBuilder()
        
        buttons = [
            ("👥 Управление пользователями", "admin_users"),
            ("🏆 Управление жетонами", "admin_tokens"),
            ("💳 Управление подписками", "admin_subscriptions"),
            ("📝 Управление контентом", "admin_content"),
            ("↩️ Назад", "back_to_main")
        ]
        
        for text, callback_data in buttons:
            builder.button(text=text, callback_data=callback_data)
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def get_users_keyboard(users: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру со списком пользователей"""
        builder = InlineKeyboardBuilder()
        
        # Добавляем кнопки пользователей
        for user in users:
            builder.button(
                text=f"{user['full_name']} (@{user['username']})",
                callback_data=f"user_{user['id']}"
            )
        
        # Добавляем кнопки навигации
        nav_buttons = []
        if page > 1:
            nav_buttons.append(("⬅️", f"users_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(("➡️", f"users_page_{page+1}"))
        
        for text, callback_data in nav_buttons:
            builder.button(text=text, callback_data=callback_data)
            
        builder.button(text="↩️ Назад", callback_data="back_to_admin")
        
        # Настраиваем расположение кнопок
        if len(users) > 0:
            if len(nav_buttons) > 0:
                builder.adjust(1, len(nav_buttons), 1)
            else:
                builder.adjust(1)
        else:
            builder.adjust(1)
            
        return builder.as_markup()
    
    @staticmethod
    def get_subscriptions_keyboard(subscriptions: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру со списком подписок"""
        builder = InlineKeyboardBuilder()
        
        # Добавляем кнопку настройки тарифов
        builder.button(text="⚙️ Настройка тарифов", callback_data="manage_tariffs")
        
        # Добавляем кнопки подписок
        for sub in subscriptions:
            builder.button(
                text=f"{sub['user_name']} - {sub['tariff_name']} до {sub['end_date']}",
                callback_data=f"subscription_{sub['id']}"
            )
        
        # Добавляем кнопки навигации
        nav_buttons = []
        if page > 1:
            nav_buttons.append(("⬅️", f"subs_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(("➡️", f"subs_page_{page+1}"))
        
        for text, callback_data in nav_buttons:
            builder.button(text=text, callback_data=callback_data)
            
        builder.button(text="↩️ Назад", callback_data="back_to_admin")
        
        builder.adjust(1, 1, len(nav_buttons), 1)
        return builder.as_markup()
    
    @staticmethod
    def get_tariffs_keyboard(tariffs: list) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру со списком тарифов"""
        builder = InlineKeyboardBuilder()
        
        for tariff in tariffs:
            builder.button(
                text=f"{tariff['name']} - {tariff['price']}₽",
                callback_data=f"edit_tariff_{tariff['id']}"
            )
        
        builder.button(text="↩️ Назад", callback_data="back_to_subscriptions")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def get_content_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для выбора типа контента"""
        builder = InlineKeyboardBuilder()
        
        buttons = [
            ("📝 Задания на день", "show_content:daily:1"),
            ("🤔 Загадки", "show_content:riddles:1"),
            ("👄 Скороговорки", "show_content:twisters:1"),
            ("🧩 Ребусы", "show_content:puzzles:1"),
            ("🎨 Рисование", "show_content:creativity:drawing:1"),
            ("📄 Бумага", "show_content:creativity:paper:1"),
            ("🏺 Лепка", "show_content:creativity:sculpting:1"),
            ("🗣 Артикуляционная гимнастика", "show_content:articular:1"),
            ("🧠 Нейро гимнастика", "show_content:neuro:1")
        ]
        
        for text, callback_data in buttons:
            builder.button(text=text, callback_data=callback_data)
        
        builder.button(text="🔙 Назад", callback_data="back_to_admin_menu")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def get_content_list_keyboard(items: list, page: int, total_pages: int, content_type: str) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру со списком контента"""
        builder = InlineKeyboardBuilder()
        
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        current_items = items[start_idx:end_idx]
        
        for item in current_items:
            if content_type == "daily":
                text = item.get("task_text", "") or item.get("text", "")
            elif content_type == "riddles":
                text = item.get("text", "") or item.get("question", "")
            elif content_type == "twisters":
                text = item.get("text", "")
            elif content_type == "puzzles":
                text = f"Ребус #{item.get('id', 0)}"
            elif content_type.startswith("creativity_"):
                text = item.get("title", "")
            elif content_type in ["articular", "neuro"]:
                text = item.get("title", "")
            else:
                text = str(item)

            if len(text) > 30:
                text = text[:27] + "..."
            
            item_id = item.get('id', 0)
            builder.button(
                text=text,
                callback_data=f"edit_content:{content_type}:{item_id}"
            )
        
        builder.adjust(1)

        # Добавляем навигационные кнопки
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️",
                callback_data=f"show_content:{content_type}:{page-1}"
            ))
        
        nav_buttons.append(InlineKeyboardButton(
            text=f"📄 {page}/{total_pages}",
            callback_data="ignore"
        ))
        
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(
                text="➡️",
                callback_data=f"show_content:{content_type}:{page+1}"
            ))
        
        builder.row(*nav_buttons)
        
        # Добавляем кнопку добавления нового контента
        builder.row(InlineKeyboardButton(
            text="➕ Добавить",
            callback_data=f"admin_add_content:{content_type}"
        ))
        
        # Добавляем кнопку "Назад"
        builder.row(InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_content_menu"
        ))

        return builder.as_markup()

    @staticmethod
    def get_cancel_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру с кнопкой отмены"""
        builder = InlineKeyboardBuilder()
        builder.button(text="❌ Отмена", callback_data="cancel_action")
        return builder.as_markup() 