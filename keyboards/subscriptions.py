from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class SubscriptionsKeyboard:
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру меню подписок"""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="💳 Подписка", callback_data="subscription")
        builder.button(text="🤝 Реферальная ссылка", callback_data="referral_link")
        builder.button(text="⬅️ Назад", callback_data="back_to_main")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def get_subscription_keyboard(has_subscription: bool) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для раздела подписки"""
        builder = InlineKeyboardBuilder()
        
        if has_subscription:
            builder.button(text="🔄 Продлить подписку", callback_data="extend_subscription")
        else:
            builder.button(text="💳 Купить подписку", callback_data="buy_subscription")
            
        builder.button(text="⬅️ Назад", callback_data="back_to_parents")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def get_referral_keyboard(link: str) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для раздела рефералов"""
        builder = InlineKeyboardBuilder()
        
        builder.button(text=link, callback_data="copy_referral")
        builder.button(text="⬅️ Назад", callback_data="back_to_parents")
        
        builder.adjust(1)
        return builder.as_markup()

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