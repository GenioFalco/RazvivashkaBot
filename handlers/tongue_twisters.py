from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.database import Database
from keyboards.tongue_twisters import TongueTwistersKeyboard
from keyboards.main_menu import MainMenuKeyboard
import logging

router = Router()

MOTIVATIONAL_MESSAGES = [
    "Не переживай! У тебя обязательно получится в следующий раз! 🌟",
    "Тренировка делает мастера! Продолжай стараться! 💪",
    "Даже маленький прогресс - это уже успех! Молодец! 🌈",
    "Главное - не сдаваться! Ты справишься! ⭐",
    "С каждой попыткой ты становишься лучше! 🎯"
]

@router.callback_query(F.data == "tongue_twisters")
async def show_tongue_twisters_menu(callback: CallbackQuery):
    """Показывает меню скороговорок"""
    db = Database()
    
    # Проверяем доступ к функции
    has_access = await db.check_feature_access(callback.from_user.id, 'tongue_twisters')
    if not has_access:
        await callback.message.edit_text(
            "⭐ Доступ к скороговоркам ограничен!\n\n"
            "Для доступа к этому разделу необходима подписка.\n"
            "Перейдите в раздел «Для мам», чтобы узнать подробности.",
            reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "👄 Добро пожаловать в раздел Скороговорки!\n\n"
        "Здесь тебя ждут интересные скороговорки, которые помогут:\n"
        "• Улучшить дикцию\n"
        "• Развить речь\n"
        "• Научиться говорить чётко и красиво\n\n"
        "За каждую выполненную скороговорку ты получишь 👄 Говорун!\n"
        "А если выполнишь все 3 скороговорки за день, получишь особую награду - 🏆 Чемпион дня!\n\n"
        "Нажми кнопку 'Начать', чтобы приступить к тренировке!",
        reply_markup=TongueTwistersKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "start_tongue_twisters")
async def start_tongue_twisters(callback: CallbackQuery, state: FSMContext):
    """Начинает сессию скороговорок"""
    db = Database()
    twisters, completed_count = await db.get_user_tongue_twisters(callback.from_user.id)
    
    # Сохраняем скороговорки в состояние
    await state.update_data(twisters=twisters, current_index=0)
    
    # Показываем первую скороговорку
    twister = twisters[0]
    await callback.message.edit_text(
        f"Скороговорка {1}/3:\n\n"
        f"{twister['text']}\n\n"
        f"{'✅ Выполнена!' if twister['completed'] else '❌ Не выполнена'}",
        reply_markup=TongueTwistersKeyboard.get_navigation_keyboard(0, len(twisters), twister['id'], twister['completed'])
    )
    await callback.answer()

@router.callback_query(F.data.startswith(("prev_twister_", "next_twister_")))
async def navigate_twisters(callback: CallbackQuery, state: FSMContext):
    """Навигация между скороговорками"""
    try:
        # Получаем направление и текущий индекс
        direction = "prev" if callback.data.startswith("prev") else "next"
        current_index = int(callback.data.split("_")[2])
        
        # Получаем данные из состояния
        data = await state.get_data()
        twisters = data.get('twisters', [])
        
        if not twisters:
            await callback.message.answer("Ошибка: скороговорки не найдены")
            return
        
        # Вычисляем новый индекс
        new_index = current_index - 1 if direction == "prev" else current_index + 1
        
        # Проверяем границы
        if new_index < 0 or new_index >= len(twisters):
            await callback.answer("Больше скороговорок нет!")
            return
        
        # Обновляем индекс в состоянии
        await state.update_data(current_index=new_index)
        
        # Получаем статус выполнения из списка скороговорок
        current_twister = twisters[new_index]
        is_completed = current_twister['completed']
        
        # Формируем сообщение
        message = (
            f"Скороговорка {new_index + 1}/3:\n\n"
            f"{current_twister['text']}\n\n"
            f"{'✅ Выполнена!' if is_completed else '❌ Не выполнена'}"
        )
        
        # Получаем клавиатуру
        markup = TongueTwistersKeyboard.get_navigation_keyboard(
            new_index,
            len(twisters),
            current_twister['id'],
            is_completed
        )
        
        await callback.message.edit_text(message, reply_markup=markup)
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error in navigate_twisters: {e}")
        await callback.message.answer(
            "Произошла ошибка при навигации между скороговорками. Попробуйте еще раз."
        )
        await callback.answer()

@router.callback_query(F.data.startswith("complete_twister_"))
async def complete_twister(callback: CallbackQuery, state: FSMContext):
    """Отмечает скороговорку как выполненную"""
    twister_id = int(callback.data.split("_")[2])
    db = Database()
    
    # Отмечаем скороговорку как выполненную
    success = await db.complete_tongue_twister(callback.from_user.id, twister_id)
    if success:
        # Проверяем количество выполненных скороговорок
        twisters, completed_count = await db.get_user_tongue_twisters(callback.from_user.id)
        
        # Обновляем данные в состоянии
        data = await state.get_data()
        current_index = data.get('current_index', 0)
        await state.update_data(twisters=twisters)
        
        if completed_count == 3:
            # Получаем супер-приз (токен с id=8)
            super_token = await db.get_token_by_id(8)
            text = (
                "🎉 Поздравляем! Ты выполнил все скороговорки на сегодня!\n"
                f"В награду ты получаешь особый приз: {super_token['emoji']} {super_token['name']}!\n"
                "Возвращайся завтра за новыми упражнениями! 🌟\n\n"
                f"Скороговорка {current_index + 1}/3:\n"
                f"{twisters[current_index]['text']}"
            )
        else:
            # Получаем обычный токен
            token = await db.get_token_by_id(4)  # id=4 для токена "Говорун"
            text = (
                "🎯 Отлично! Ты справился со скороговоркой!\n"
                f"Получаешь награду: {token['emoji']} {token['name']}!\n"
                "Продолжай тренироваться!\n\n"
                f"Скороговорка {current_index + 1}/3:\n"
                f"{twisters[current_index]['text']}"
            )
        
        # Всегда показываем навигационную клавиатуру с пометкой is_completed=True
        markup = TongueTwistersKeyboard.get_navigation_keyboard(
            current_index,
            len(twisters),
            twisters[current_index]['id'],
            True  # Скороговорка теперь выполнена
        )
    else:
        text = "Произошла ошибка при сохранении результата."
        markup = TongueTwistersKeyboard.get_back_button()
    
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.startswith("skip_twister_"))
async def skip_twister(callback: CallbackQuery, state: FSMContext):
    """Пропускает текущую скороговорку"""
    import random
    
    # Получаем мотивирующее сообщение
    message = random.choice(MOTIVATIONAL_MESSAGES)
    
    # Получаем данные из состояния
    data = await state.get_data()
    twisters = data.get('twisters', [])
    current_index = data.get('current_index', 0)
    current_twister = twisters[current_index]
    
    await callback.message.edit_text(
        f"{message}\n\n"
        f"Скороговорка {current_index + 1}/3:\n"
        f"{current_twister['text']}",
        reply_markup=TongueTwistersKeyboard.get_navigation_keyboard(
            current_index,
            len(twisters),
            current_twister['id'],
            current_twister['completed']
        )
    )
    await callback.answer()

@router.callback_query(F.data.in_({"back_to_tongue_twisters", "back_to_main"}))
async def process_back_button(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие кнопки "Назад" """
    await state.clear()
    
    if callback.data == "back_to_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=MainMenuKeyboard.get_keyboard(user_id=callback.from_user.id)
        )
    else:
        await callback.message.edit_text(
            "👄 Добро пожаловать в раздел Скороговорки!\n\n"
            "Здесь тебя ждут интересные скороговорки, которые помогут:\n"
            "• Улучшить дикцию\n"
            "• Развить речь\n"
            "• Научиться говорить чётко и красиво\n\n"
            "За каждую выполненную скороговорку ты получишь 👄 Говорун!\n"
            "А если выполнишь все 3 скороговорки за день, получишь особую награду - 🏆 Чемпион дня!\n\n"
            "Нажми кнопку 'Начать', чтобы приступить к тренировке!",
            reply_markup=TongueTwistersKeyboard.get_menu_keyboard()
        )
    await callback.answer() 