from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.daily_tasks import DailyTasksKeyboard
from keyboards.main_menu import MainMenuKeyboard
from database.database import Database
import random

router = Router()

@router.callback_query(F.data == "daily_tasks")
async def show_daily_tasks_menu(callback: CallbackQuery):
    """Показывает главное меню раздела ежедневных заданий"""
    db = Database()
    
    # Проверяем доступ к функции
    has_access = await db.check_feature_access(callback.from_user.id, 'daily_tasks')
    if not has_access:
        await callback.message.edit_text(
            "⭐ Доступ к ежедневным заданиям ограничен!\n\n"
            "Вы уже использовали бесплатную попытку.\n"
            "Для продолжения необходима подписка.\n\n"
            "Перейдите в раздел «Для мам», чтобы узнать подробности.",
            reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return
    
    tasks, completed = await db.get_user_daily_tasks(callback.from_user.id)
    
    if completed == 5:
        text = (
            "🌟 Ух ты, ты уже выполнил все задания на сегодня!\n"
            "Ты настоящий герой дня! 💖\n\n"
            "Завтра я приготовлю для тебя новые интересные задания."
        )
        markup = DailyTasksKeyboard.get_back_button()
    else:
        text = (
            "🌞 Добро пожаловать в раздел «Задания на день»!\n\n"
            "Каждый день тебя ждут 5 интересных заданий. "
            "За каждое выполненное задание ты получаешь звёздочку ⭐\n"
            "А если выполнишь все задания, получишь особую награду! 🏆\n\n"
            f"Выполнено заданий: {completed}/5"
        )
        markup = DailyTasksKeyboard.get_main_keyboard()
    
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data == "show_daily_tasks")
async def show_next_task(callback: CallbackQuery):
    """Показывает следующее невыполненное задание"""
    db = Database()
    
    # Проверяем доступ к функции
    has_access = await db.check_feature_access(callback.from_user.id, 'daily_tasks')
    if not has_access:
        await callback.message.edit_text(
            "⭐ Доступ к ежедневным заданиям ограничен!\n\n"
            "Вы уже использовали бесплатную попытку.\n"
            "Для продолжения необходима подписка.\n\n"
            "Перейдите в раздел «Для мам», чтобы узнать подробности.",
            reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return
    
    tasks, completed = await db.get_user_daily_tasks(callback.from_user.id)
    
    if completed == 5:
        text = (
            "🌟 Ух ты, ты уже выполнил все задания на сегодня!\n"
            "Ты настоящий герой дня! 💖\n\n"
            "Завтра я приготовлю для тебя новые интересные задания."
        )
        markup = DailyTasksKeyboard.get_back_button()
    else:
        # Находим первое невыполненное задание
        next_task = next((task for task in tasks if not task['completed']), None)
        if next_task:
            text = (
                f"📝 Задание {completed + 1} из 5:\n\n"
                f"{next_task['text']}\n\n"
                "Нажми «Сделал», когда выполнишь задание!"
            )
            markup = DailyTasksKeyboard.get_task_keyboard(next_task['id'])
        else:
            text = "Произошла ошибка при получении задания."
            markup = DailyTasksKeyboard.get_back_button()
    
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task(callback: CallbackQuery):
    """Обрабатывает выполнение задания"""
    db = Database()
    
    # Проверяем доступ к функции
    has_access = await db.check_feature_access(callback.from_user.id, 'daily_tasks')
    if not has_access:
        await callback.message.edit_text(
            "⭐ Доступ к ежедневным заданиям ограничен!\n\n"
            "Вы уже использовали бесплатную попытку.\n"
            "Для продолжения необходима подписка.\n\n"
            "Перейдите в раздел «Для мам», чтобы узнать подробности.",
            reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return
    
    task_id = int(callback.data.split("_")[2])
    
    # Отмечаем задание как выполненное
    success = await db.complete_daily_task(callback.from_user.id, task_id)
    if success:
        # Увеличиваем счетчик использования функции
        await db.increment_feature_attempt(callback.from_user.id, 'daily_tasks')
        
        # Проверяем количество выполненных заданий
        tasks, completed = await db.get_user_daily_tasks(callback.from_user.id)
        
        if completed == 5:
            # Получаем супер-приз (токен с id=8)
            super_token = await db.get_token_by_id(8)
            text = (
                "🎉 Поздравляем! Ты выполнил все задания на сегодня!\n"
                f"В награду ты получаешь особый приз: {super_token['emoji']} {super_token['name']}!\n"
                "Возвращайся завтра за новыми заданиями! 🌟"
            )
            markup = InlineKeyboardBuilder()
            markup.add(InlineKeyboardButton(text="↩️ В главное меню", callback_data="back_to_main"))
            markup = markup.as_markup()
        else:
            # Получаем обычный токен
            tokens = await db.get_all_tokens()
            token = next((t for t in tokens if t['id'] == 2), None)
            text = f"Здорово! За выполнение задания ты получаешь {token['emoji']} {token['name']}! Соберешь еще больше?"
            markup = DailyTasksKeyboard.get_main_keyboard()
    else:
        text = "Произошла ошибка при сохранении результата."
        markup = DailyTasksKeyboard.get_main_keyboard()
    
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.startswith("skip_task_"))
async def skip_task(callback: CallbackQuery):
    """Пропускает текущее задание и показывает другое случайное"""
    current_task_id = int(callback.data.split("_")[2])
    db = Database()
    tasks, completed = await db.get_user_daily_tasks(callback.from_user.id)
    
    if completed == 5:
        text = (
            "🌟 Ух ты, ты уже выполнил все задания на сегодня!\n"
            "Ты настоящий герой дня! 💖\n\n"
            "Завтра я приготовлю для тебя новые интересные задания."
        )
        markup = DailyTasksKeyboard.get_back_button()
    else:
        # Находим все невыполненные задания, кроме текущего
        uncompleted_tasks = [task for task in tasks if not task['completed'] and task['id'] != current_task_id]
        
        if uncompleted_tasks:
            # Выбираем случайное задание из невыполненных
            next_task = random.choice(uncompleted_tasks)
            text = (
                "Это задание можно оставить на потом. Главное — стараться! "
                "Держи следующее задание на сегодня. 🐾\n\n"
                f"📝 Задание {completed + 1} из 5:\n\n"
                f"{next_task['text']}\n\n"
                "Нажми «Сделал», когда выполнишь задание!"
            )
            markup = DailyTasksKeyboard.get_task_keyboard(next_task['id'])
        else:
            text = "Другие задания я пока дать не могу, так как новых заданий нет."
            markup = DailyTasksKeyboard.get_back_button()
    
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.in_({"back_to_daily_tasks", "back_to_main"}))
async def process_back_button(callback: CallbackQuery):
    """Обрабатывает нажатие кнопки "Назад" """
    try:
        if callback.data == "back_to_main":
            await callback.message.edit_text(
                "Главное меню:",
                reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
            )
        else:
            await callback.message.edit_text(
                "🌞 Добро пожаловать в раздел «Задания на день»!\n\n"
                "Каждый день тебя ждут 5 интересных заданий. "
                "За каждое выполненное задание ты получаешь звёздочку ⭐\n"
                "А если выполнишь все задания, получишь особую награду! 🏆",
                reply_markup=DailyTasksKeyboard.get_main_keyboard()
            )
    except Exception as e:
        # Если не удалось отредактировать сообщение, отправляем новое
        if callback.data == "back_to_main":
            await callback.message.answer(
                "Главное меню:",
                reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
            )
        else:
            await callback.message.answer(
                "🌞 Добро пожаловать в раздел «Задания на день»!\n\n"
                "Каждый день тебя ждут 5 интересных заданий. "
                "За каждое выполненное задание ты получаешь звёздочку ⭐\n"
                "А если выполнишь все задания, получишь особую награду! 🏆",
                reply_markup=DailyTasksKeyboard.get_main_keyboard()
            )
    await callback.answer() 