from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import Database
from keyboards.main_menu import MainMenuKeyboard
from keyboards.riddles import RiddlesKeyboard

router = Router()

class RiddleStates(StatesGroup):
    waiting_for_answer = State()

@router.callback_query(F.data == "riddles")
async def show_riddles_menu(callback: CallbackQuery):
    """Показывает меню загадок"""
    await callback.message.edit_text(
        "🎯 Добро пожаловать в раздел Загадки!\n\n"
        "Здесь тебя ждут интересные загадки, которые помогут развить "
        "логическое мышление и сообразительность.\n\n"
        "За каждую правильно разгаданную загадку ты получишь ❓ Мудрец!\n"
        "А если разгадаешь все 5 загадок, получишь особую награду - 🏆 Чемпион дня!\n\n"
        "Чтобы посмотреть ответ на загадку, нужен 🔑 Ключ доступа.\n"
        "Нажми кнопку 'Загадки', чтобы начать!",
        reply_markup=RiddlesKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "start_riddles")
async def start_riddles(callback: CallbackQuery, state: FSMContext):
    """Начинает сессию загадок"""
    db = Database()
    riddles, completed_count = await db.get_user_riddles(callback.from_user.id)
    
    if completed_count == 5:
        await callback.message.edit_text(
            "🎉 Поздравляем! Ты уже разгадал все загадки на сегодня.\n"
            "Приходи завтра за новыми загадками!",
            reply_markup=RiddlesKeyboard.get_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Сохраняем загадки в состояние
    await state.update_data(riddles=riddles, current_index=0)
    
    # Показываем первую загадку
    riddle = riddles[0]
    await callback.message.edit_text(
        f"Загадка {1}/5:\n\n"
        f"{riddle['question']}\n\n"
        f"{'✅ Разгадана!' if riddle['completed'] else '❌ Не разгадана'}",
        reply_markup=RiddlesKeyboard.get_navigation_keyboard(0, len(riddles))
    )
    await callback.answer()

@router.callback_query(F.data.startswith(("next_riddle_", "prev_riddle_")))
async def navigate_riddles(callback: CallbackQuery, state: FSMContext):
    """Обработка навигации по загадкам"""
    data = await state.get_data()
    riddles = data['riddles']
    current_index = int(callback.data.split('_')[2])
    
    if callback.data.startswith("next_"):
        new_index = current_index + 1
    else:
        new_index = current_index - 1
    
    # Очищаем состояние ответа, если оно было
    await state.set_data({**data, 'current_index': new_index})
    
    riddle = riddles[new_index]
    await callback.message.edit_text(
        f"Загадка {new_index + 1}/5:\n\n"
        f"{riddle['question']}\n\n"
        f"{'✅ Разгадана!' if riddle['completed'] else '❌ Не разгадана'}",
        reply_markup=RiddlesKeyboard.get_navigation_keyboard(new_index, len(riddles))
    )
    await callback.answer()

@router.callback_query(F.data.startswith("answer_riddle_"))
async def start_answer_riddle(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс ответа на загадку"""
    current_index = int(callback.data.split('_')[2])
    data = await state.get_data()
    riddle = data['riddles'][current_index]
    
    if riddle['completed']:
        await callback.message.edit_text(
            "Эта загадка уже разгадана! Переходи к следующей.",
            reply_markup=RiddlesKeyboard.get_navigation_keyboard(current_index, len(data['riddles']))
        )
        await callback.answer()
        return
    
    await state.set_state(RiddleStates.waiting_for_answer)
    await callback.message.edit_text(
        f"Загадка:\n{riddle['question']}\n\n"
        "Введи свой ответ одним словом.\n"
        "Для отмены нажми кнопку 'Назад'.",
        reply_markup=RiddlesKeyboard.get_cancel_keyboard(current_index)
    )
    await callback.answer()

@router.message(RiddleStates.waiting_for_answer)
async def process_riddle_answer(message: Message, state: FSMContext):
    """Обработка ответа на загадку"""
    data = await state.get_data()
    current_index = data['current_index']
    riddle = data['riddles'][current_index]
    
    db = Database()
    is_correct = await db.check_riddle_answer(
        message.from_user.id,
        riddle['id'],
        message.text
    )
    
    if is_correct:
        # Получаем обновленные данные о загадках
        updated_riddles, completed_count = await db.get_user_riddles(message.from_user.id)
        await state.update_data(riddles=updated_riddles)
        
        if completed_count == 5:
            # Получаем информацию о токенах
            super_token = await db.get_token_by_id(8)
            riddle_token = await db.get_token_by_id(7)
            
            await message.answer(
                f"🎉 Поздравляем! Ты разгадал все загадки!\n"
                f"Ты получаешь {riddle_token['emoji']} {riddle_token['name']} за эту загадку\n"
                f"И особую награду {super_token['emoji']} {super_token['name']}!\n"
                "Приходи завтра за новыми загадками!",
                reply_markup=RiddlesKeyboard.get_menu_keyboard()
            )
        else:
            # Получаем информацию о токене
            riddle_token = await db.get_token_by_id(7)
            await message.answer(
                f"✨ Правильно! Ты получаешь {riddle_token['emoji']} {riddle_token['name']}!\n"
                f"Загадка {current_index + 1}/5 разгадана!",
                reply_markup=RiddlesKeyboard.get_navigation_keyboard(current_index, len(updated_riddles))
            )
    else:
        await message.answer(
            "🤔 Хм, подумай ещё!\n"
            "Попробуй дать другой ответ или нажми 'Назад' для отмены.",
            reply_markup=RiddlesKeyboard.get_cancel_keyboard(current_index)
        )

@router.callback_query(F.data.startswith("show_answer_"))
async def show_riddle_answer(callback: CallbackQuery, state: FSMContext):
    """Показывает ответ на загадку"""
    db = Database()
    # Пытаемся потратить ключ доступа
    if not await db.spend_token(callback.from_user.id, 1):
        await callback.message.edit_text(
            "У тебя нет 🔑 Ключа доступа!\n"
            "Попроси помощи у родителей или попробуй отгадать самостоятельно.",
            reply_markup=RiddlesKeyboard.get_navigation_keyboard(
                int(callback.data.split('_')[2]),
                5
            )
        )
        await callback.answer()
        return
    
    data = await state.get_data()
    current_index = int(callback.data.split('_')[2])
    riddle = data['riddles'][current_index]
    
    await callback.message.edit_text(
        f"Загадка {current_index + 1}/5:\n\n"
        f"{riddle['question']}\n\n"
        f"Ответ: {riddle['answer']}\n\n"
        "За просмотр ответа потрачен 1 🔑 Ключ доступа",
        reply_markup=RiddlesKeyboard.get_navigation_keyboard(current_index, len(data['riddles']))
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cancel_answer_"))
async def cancel_riddle_answer(callback: CallbackQuery, state: FSMContext):
    """Отменяет ввод ответа на загадку"""
    current_index = int(callback.data.split('_')[2])
    data = await state.get_data()
    riddle = data['riddles'][current_index]
    
    await state.set_data(data)  # Сбрасываем состояние ответа
    
    await callback.message.edit_text(
        f"Загадка {current_index + 1}/5:\n\n"
        f"{riddle['question']}\n\n"
        f"{'✅ Разгадана!' if riddle['completed'] else '❌ Не разгадана'}",
        reply_markup=RiddlesKeyboard.get_navigation_keyboard(current_index, len(data['riddles']))
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_riddles_menu")
async def back_to_riddles_menu(callback: CallbackQuery, state: FSMContext):
    """Возвращает в меню загадок"""
    await state.clear()
    await show_riddles_menu(callback) 