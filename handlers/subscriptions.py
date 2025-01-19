from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.database import Database
from keyboards.subscriptions import SubscriptionsKeyboard
from keyboards.main_menu import MainMenuKeyboard

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

@router.callback_query(F.data.startswith("buy_subscription_"))
async def process_subscription_purchase(callback: CallbackQuery):
    """Обрабатывает покупку подписки"""
    subscription_id = int(callback.data.split("_")[2])
    
    db = Database()
    subscriptions = await db.get_all_subscriptions()
    subscription = next((s for s in subscriptions if s['id'] == subscription_id), None)
    
    if not subscription:
        await callback.answer("Подписка не найдена", show_alert=True)
        return
    
    # Здесь должна быть интеграция с платежной системой
    # Пока просто показываем заглушку
    payment_url = "https://example.com/payment"  # Здесь должна быть реальная ссылка на оплату
    
    await callback.message.edit_text(
        f"💫 Оформление подписки '{subscription['name']}'\n\n"
        f"Стоимость: {subscription['price']}₽\n"
        f"Длительность: {subscription['duration_days']} дней\n\n"
        "Нажмите кнопку «Оплатить» для перехода к оплате.\n"
        "После оплаты нажмите «Я оплатил(а)» для проверки платежа.",
        reply_markup=SubscriptionsKeyboard.get_payment_keyboard(payment_url, subscription_id)
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