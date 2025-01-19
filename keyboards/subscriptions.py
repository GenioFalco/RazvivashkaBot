from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class SubscriptionsKeyboard:
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру меню подписок"""
        kb = InlineKeyboardBuilder()
        
        buttons = [
            ("💎 Подписки", "show_subscriptions"),
            ("❓ Как это работает", "subscription_info"),
            ("↩️ Главное меню", "back_to_main")
        ]
        
        for text, callback_data in buttons:
            kb.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        kb.adjust(1)
        
        return kb.as_markup()

    @staticmethod
    def get_subscription_list_keyboard(subscriptions: list) -> InlineKeyboardMarkup:
        """Создает клавиатуру со списком доступных подписок"""
        kb = InlineKeyboardBuilder()
        
        for sub in subscriptions:
            kb.add(InlineKeyboardButton(
                text=f"{sub['name']} - {sub['price']}₽",
                callback_data=f"buy_subscription_{sub['id']}"
            ))
        
        kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_subscriptions"))
        kb.adjust(1)
        
        return kb.as_markup()

    @staticmethod
    def get_payment_keyboard(payment_url: str, subscription_id: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру для оплаты"""
        kb = InlineKeyboardBuilder()
        
        kb.add(InlineKeyboardButton(text="💳 Оплатить", url=payment_url))
        kb.add(InlineKeyboardButton(
            text="✅ Я оплатил(а)",
            callback_data=f"check_payment_{subscription_id}"
        ))
        kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data="show_subscriptions"))
        
        kb.adjust(1)
        return kb.as_markup() 