from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.database import Database
from keyboards.subscriptions import SubscriptionsKeyboard
from keyboards.main_menu import MainMenuKeyboard
from datetime import datetime

router = Router()

@router.callback_query(F.data == "for_parents")
async def show_subscriptions_menu(callback: CallbackQuery):
    """Показывает меню раздела для родителей"""
    await callback.message.edit_text(
        "👋 Добро пожаловать в раздел для родителей!\n\n"
        "Здесь вы можете:\n"
        "• Оформить подписку на полный доступ\n"
        "• Узнать о преимуществах подписки\n"
        "• Получить ответы на вопросы\n\n"
        "Выберите интересующий вас раздел:",
        reply_markup=SubscriptionsKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "subscription_info")
async def show_subscription_info(callback: CallbackQuery):
    """Показывает информацию о работе подписок"""
    await callback.message.edit_text(
        "ℹ️ Как работает подписка:\n\n"
        "🔸 Без подписки доступно:\n"
        "• Задания на день (только первый день)\n"
        "• Один мастер-класс в разделе Рисование\n\n"
        "🔸 С подпиской доступно:\n"
        "• Все ежедневные задания\n"
        "• Все мастер-классы\n"
        "• Все разделы без ограничений\n"
        "• Новые материалы каждый день\n"
        "• Бонусные материалы\n\n"
        "Выберите удобный тариф и развивайтесь вместе с нами! 🌟",
        reply_markup=SubscriptionsKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "show_subscriptions")
async def show_subscription_list(callback: CallbackQuery):
    """Показывает список доступных подписок"""
    db = Database()
    subscriptions = await db.get_all_subscriptions()
    
    # Проверяем текущую подписку
    current_sub = await db.get_user_subscription(callback.from_user.id)
    
    text = "💎 Доступные подписки:\n\n"
    if current_sub:
        text += (
            "✨ У вас активна подписка:\n"
            f"'{current_sub['name']}' до {current_sub['end_date']}\n\n"
        )
    
    text += "Выберите подходящий тариф:"
    
    await callback.message.edit_text(
        text,
        reply_markup=SubscriptionsKeyboard.get_subscription_list_keyboard(subscriptions)
    )
    await callback.answer()

@router.callback_query(F.data == "buy_subscription")
async def show_subscription_plans(callback: CallbackQuery):
    """Показывает список доступных подписок"""
    db = Database()
    subscriptions = await db.get_all_subscriptions()
    
    text = (
        "📋 Выберите подходящий тариф:\n\n"
    )
    
    builder = InlineKeyboardBuilder()
    
    for sub in subscriptions:
        text += (
            f"🔸 {sub['name']}\n"
            f"{sub['description']}\n"
            f"Стоимость: {sub['price']}₽\n\n"
        )
        builder.button(
            text=f"{sub['name']} - {sub['price']}₽",
            callback_data=f"activate_subscription_{sub['id']}"
        )
    
    builder.button(text="⬅️ Назад", callback_data="subscription")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("activate_subscription_"))
async def activate_subscription(callback: CallbackQuery):
    """Активирует подписку на выбранный тариф"""
    subscription_id = int(callback.data.split("_")[2])
    db = Database()
    
    # В реальном боте здесь должна быть интеграция с платежной системой
    # Сейчас просто активируем подписку
    if await db.add_subscription(callback.from_user.id, subscription_id):
        subscription = await db.get_user_subscription(callback.from_user.id)
        text = (
            "🎉 Поздравляем! Подписка успешно активирована!\n\n"
            f"Тариф: {subscription['name']}\n"
            f"Действует до: {subscription['end_date']}\n\n"
            "Теперь вам доступны:\n"
            "• Все ежедневные задания\n"
            "• Все мастер-классы\n"
            "• Дополнительные материалы\n\n"
            "Желаем приятного пользования! 🌟"
        )
    else:
        text = (
            "❌ Произошла ошибка при активации подписки.\n"
            "Пожалуйста, попробуйте позже или обратитесь в поддержку."
        )
    
    await callback.message.edit_text(
        text,
        reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment(callback: CallbackQuery):
    """Проверяет статус оплаты"""
    subscription_id = int(callback.data.split("_")[2])
    
    # Здесь должна быть проверка статуса оплаты
    # Пока просто показываем заглушку
    payment_successful = True  # В реальности здесь будет проверка статуса
    
    if payment_successful:
        db = Database()
        if await db.add_subscription(callback.from_user.id, subscription_id):
            await callback.message.edit_text(
                "🎉 Поздравляем! Подписка успешно активирована!\n\n"
                "Теперь вам доступны все функции бота.\n"
                "Желаем приятного пользования! 🌟",
                reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
            )
        else:
            await callback.message.edit_text(
                "Произошла ошибка при активации подписки.\n"
                "Пожалуйста, обратитесь в поддержку.",
                reply_markup=SubscriptionsKeyboard.get_menu_keyboard()
            )
    else:
        await callback.answer(
            "Оплата не найдена. Попробуйте еще раз или обратитесь в поддержку.",
            show_alert=True
        )

@router.callback_query(F.data == "back_to_subscriptions")
async def back_to_subscriptions(callback: CallbackQuery):
    """Возвращает в меню подписок"""
    await show_subscriptions_menu(callback)

@router.callback_query(F.data == "subscription")
async def show_subscription_info(callback: CallbackQuery):
    """Показывает информацию о подписке"""
    db = Database()
    subscription = await db.get_user_subscription(callback.from_user.id)
    
    if subscription:
        end_date = datetime.strptime(subscription['end_date'], '%Y-%m-%d')
        days_left = (end_date - datetime.now()).days
        
        text = (
            "💫 Ваша подписка активна!\n\n"
            f"Тариф: {subscription['name']}\n"
            f"Действует до: {end_date.strftime('%d.%m.%Y')}\n"
            f"Осталось дней: {days_left}\n\n"
            "Хотите продлить подписку?"
        )
    else:
        text = (
            "У вас пока нет активной подписки.\n\n"
            "С подпиской вам будут доступны:\n"
            "• Все ежедневные задания\n"
            "• Все мастер-классы\n"
            "• Дополнительные материалы\n\n"
            "Хотите приобрести подписку?"
        )
    
    await callback.message.edit_text(
        text,
        reply_markup=SubscriptionsKeyboard.get_subscription_keyboard(bool(subscription))
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Возвращает в главное меню"""
    await callback.message.edit_text(
        "Выберите раздел:",
        reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
    )
    await callback.answer() 