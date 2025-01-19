from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ParentsKeyboard:
    @staticmethod
    def get_menu_keyboard() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру главного меню раздела для мам"""
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