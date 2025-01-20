from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import Database
from keyboards.main_menu import MainMenuKeyboard
from keyboards.puzzles import PuzzlesKeyboard

router = Router()

class PuzzleStates(StatesGroup):
    waiting_for_answer = State()

@router.callback_query(F.data == "puzzles")
async def show_puzzles_menu(callback: CallbackQuery):
    """Показывает меню ребусов"""
    db = Database()
    
    # Проверяем доступ к функции
    has_access = await db.check_feature_access(callback.from_user.id, 'puzzles')
    if not has_access:
        await callback.message.edit_text(
            "⭐ Доступ к ребусам ограничен!\n\n"
            "Для доступа к этому разделу необходима подписка.\n"
            "Перейдите в раздел «Для мам», чтобы узнать подробности.",
            reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🧩 Добро пожаловать в раздел Ребусы!\n\n"
        "Здесь тебя ждут интересные ребусы, которые помогут развить "
        "логическое мышление и сообразительность.\n\n"
        "За каждые 3 разгаданных ребуса ты получишь 🧩 Мастер ребусов!\n"
        "А если разгадаешь все ребусы за день, получишь особую награду - 🏆 Чемпион дня!\n\n"
        "Чтобы посмотреть ответы на ребусы, нужен 🔑 Ключ доступа.\n"
        "Нажми кнопку 'Решать', чтобы начать!",
        reply_markup=PuzzlesKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "start_puzzles")
async def start_puzzles(callback: CallbackQuery, state: FSMContext):
    """Начинает сессию ребусов"""
    db = Database()
    puzzles, completed_count = await db.get_user_puzzles(callback.from_user.id)
    
    if completed_count == 9:  # 3 ребуса * 3 картинки
        await callback.message.edit_text(
            "🎉 Поздравляем! Ты уже разгадал все ребусы на сегодня.\n"
            "Приходи завтра за новыми ребусами!",
            reply_markup=PuzzlesKeyboard.get_menu_keyboard()
        )
        await callback.answer()
        await db.cleanup_temp_files()
        return
    
    # Показываем первый ребус
    puzzle = puzzles[0]
    image = FSInputFile(puzzle['image_path'])
    
    # Отправляем изображение с ребусами
    await callback.message.answer_photo(
        photo=image,
        caption=(
            f"Ребус {1}/3\n\n"
            "На картинке изображены 3 ребуса.\n"
            "Выбери, на какой ребус хочешь ответить!"
        ),
        reply_markup=PuzzlesKeyboard.get_puzzle_keyboard(puzzle['id'], puzzle['solved'])
    )
    
    # Сохраняем текущий ребус в состояние
    await state.update_data(current_puzzle=puzzle)
    await callback.answer()

@router.callback_query(F.data.startswith("answer_puzzle_"))
async def start_answer_puzzle(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс ответа на ребус"""
    puzzle_id = int(callback.data.split('_')[2])
    rebus_number = int(callback.data.split('_')[3])
    
    data = await state.get_data()
    puzzle = data.get('current_puzzle')
    
    if puzzle['solved'][rebus_number - 1]:
        # Отправляем новое сообщение вместо редактирования
        await callback.message.answer(
            "Этот ребус уже разгадан! Выбери другой ребус.",
            reply_markup=PuzzlesKeyboard.get_puzzle_keyboard(puzzle_id, puzzle['solved'])
        )
        await callback.answer()
        return
    
    await state.set_state(PuzzleStates.waiting_for_answer)
    # Сохраняем все необходимые данные в состояние
    puzzle['index'] = data.get('current_index', 0) + 1
    await state.update_data(
        puzzle_id=puzzle_id,
        rebus_number=rebus_number,
        current_puzzle=puzzle
    )
    
    # Отправляем новое сообщение вместо редактирования
    await callback.message.answer(
        f"Введи ответ на {rebus_number}-й ребус.\n"
        "Для отмены нажми кнопку 'Назад'.",
        reply_markup=PuzzlesKeyboard.get_cancel_keyboard(puzzle_id, rebus_number)
    )
    await callback.answer()

@router.message(PuzzleStates.waiting_for_answer)
async def process_puzzle_answer(message: Message, state: FSMContext):
    """Обработка ответа на ребус"""
    data = await state.get_data()
    puzzle_id = data['puzzle_id']
    rebus_number = data['rebus_number']
    
    db = Database()
    is_correct = await db.check_puzzle_answer(
        message.from_user.id,
        puzzle_id,
        rebus_number,
        message.text
    )
    
    if is_correct:
        # Получаем обновленные данные о ребусах
        puzzles, completed_count = await db.get_user_puzzles(message.from_user.id)
        current_puzzle = next(p for p in puzzles if p['id'] == puzzle_id)
        
        # Считаем количество нерешенных ребусов на текущей картинке
        remaining = sum(1 for solved in current_puzzle['solved'] if not solved)
        
        if remaining > 0:
            await message.answer(
                f"Ты на верном пути! Один ребус разгадан, осталось еще {remaining} "
                f"ребусов на этой картинке. Давай разгадаем их все!",
                reply_markup=PuzzlesKeyboard.get_puzzle_keyboard(puzzle_id, current_puzzle['solved'])
            )
        else:
            # Если все ребусы на картинке разгаданы
            token = await db.get_token_by_id(3)  # Мастер ребусов
            
            if completed_count == 9:  # Все ребусы на день разгаданы
                super_token = await db.get_token_by_id(8)  # Чемпион дня
                await message.answer(
                    f"🎉 Поздравляем! Ты разгадал все ребусы!\n"
                    f"Ты получаешь {token['emoji']} {token['name']} за эту картинку\n"
                    f"И особую награду {super_token['emoji']} {super_token['name']}!\n"
                    "Приходи завтра за новыми ребусами!",
                    reply_markup=PuzzlesKeyboard.get_menu_keyboard()
                )
                await db.cleanup_temp_files()
            else:
                await message.answer(
                    f"✨ Отлично! Ты разгадал все ребусы на этой картинке!\n"
                    f"Ты получаешь {token['emoji']} {token['name']}!\n"
                    "Хочешь разгадать следующие ребусы?",
                    reply_markup=PuzzlesKeyboard.get_next_puzzle_keyboard()
                )
    else:
        await message.answer(
            "🤔 Хм, подумай еще!\n"
            "Попробуй дать другой ответ или нажми 'Назад' для отмены.",
            reply_markup=PuzzlesKeyboard.get_cancel_keyboard(puzzle_id, rebus_number)
        )

@router.callback_query(F.data.startswith("show_answers_"))
async def show_puzzle_answers(callback: CallbackQuery, state: FSMContext):
    """Показывает ответы на ребусы"""
    puzzle_id = int(callback.data.split('_')[2])
    
    db = Database()
    # Пытаемся потратить ключ доступа
    if not await db.spend_token(callback.from_user.id, 1):
        data = await state.get_data()
        puzzle = data.get('current_puzzle')
        # Отправляем новое сообщение вместо редактирования
        await callback.message.answer(
            "У тебя нет 🔑 Ключа доступа!\n"
            "Попроси помощи у родителей или попробуй отгадать самостоятельно.",
            reply_markup=PuzzlesKeyboard.get_puzzle_keyboard(puzzle_id, puzzle['solved'])
        )
        await callback.answer()
        return
    
    data = await state.get_data()
    puzzle = data.get('current_puzzle')
    
    # Отправляем новое сообщение вместо редактирования
    await callback.message.answer(
        "Ответы на ребусы:\n\n"
        f"1. {puzzle['answers'][0]}\n"
        f"2. {puzzle['answers'][1]}\n"
        f"3. {puzzle['answers'][2]}\n\n"
        "За просмотр ответов потрачен 1 🔑 Ключ доступа",
        reply_markup=PuzzlesKeyboard.get_puzzle_keyboard(puzzle_id, puzzle['solved'])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cancel_puzzle_answer_"))
async def cancel_puzzle_answer(callback: CallbackQuery, state: FSMContext):
    """Отменяет ввод ответа на ребус"""
    puzzle_id = int(callback.data.split('_')[3])
    rebus_number = int(callback.data.split('_')[4])
    
    # Получаем актуальные данные из БД
    db = Database()
    puzzles, completed_count = await db.get_user_puzzles(callback.from_user.id)
    current_puzzle = next(p for p in puzzles if p['id'] == puzzle_id)
    
    # Очищаем состояние ожидания ответа
    await state.clear()
    
    # Восстанавливаем состояние текущего ребуса с актуальными данными
    current_puzzle['index'] = next(i for i, p in enumerate(puzzles) if p['id'] == puzzle_id) + 1
    await state.update_data(current_puzzle=current_puzzle)
    
    # Отправляем изображение с актуальным состоянием кнопок
    image = FSInputFile(current_puzzle['image_path'])
    await callback.message.answer_photo(
        photo=image,
        caption=(
            f"Ребус {current_puzzle['index']}/3\n\n"
            "На картинке изображены 3 ребуса.\n"
            "Выбери, на какой ребус хочешь ответить!"
        ),
        reply_markup=PuzzlesKeyboard.get_puzzle_keyboard(puzzle_id, current_puzzle['solved'])
    )
    await callback.answer()

@router.callback_query(F.data == "next_puzzle")
async def show_next_puzzle(callback: CallbackQuery, state: FSMContext):
    """Показывает следующий ребус"""
    db = Database()
    puzzles, completed_count = await db.get_user_puzzles(callback.from_user.id)
    
    # Находим текущий и следующий ребус
    data = await state.get_data()
    current_puzzle = data.get('current_puzzle')
    current_index = next(i for i, p in enumerate(puzzles) if p['id'] == current_puzzle['id'])
    next_index = current_index + 1
    
    if next_index >= len(puzzles):
        await callback.message.answer(
            "Это была последняя картинка с ребусами на сегодня.\n"
            "Приходи завтра за новыми ребусами!",
            reply_markup=PuzzlesKeyboard.get_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Показываем следующий ребус
    puzzle = puzzles[next_index]
    puzzle['index'] = next_index + 1  # Сохраняем индекс
    image = FSInputFile(puzzle['image_path'])
    
    await callback.message.answer_photo(
        photo=image,
        caption=(
            f"Ребус {next_index + 1}/3\n\n"
            "На картинке изображены 3 ребуса.\n"
            "Выбери, на какой ребус хочешь ответить!"
        ),
        reply_markup=PuzzlesKeyboard.get_puzzle_keyboard(puzzle['id'], puzzle['solved'])
    )
    
    # Обновляем текущий ребус в состоянии
    await state.update_data(current_puzzle=puzzle, current_index=next_index)
    await callback.answer()

@router.callback_query(F.data == "back_to_puzzles_menu")
async def back_to_puzzles_menu(callback: CallbackQuery, state: FSMContext):
    """Возвращает в меню ребусов"""
    db = Database()
    await state.clear()
    await db.cleanup_temp_files()
    # Отправляем новое сообщение вместо редактирования
    await callback.message.answer(
        "🧩 Добро пожаловать в раздел Ребусы!\n\n"
        "Здесь тебя ждут интересные ребусы, которые помогут развить "
        "логическое мышление и сообразительность.\n\n"
        "За каждые 3 разгаданных ребуса ты получишь 🧩 Мастер ребусов!\n"
        "А если разгадаешь все ребусы за день, получишь особую награду - 🏆 Чемпион дня!\n\n"
        "Чтобы посмотреть ответы на ребусы, нужен 🔑 Ключ доступа.\n"
        "Нажми кнопку 'Решать', чтобы начать!",
        reply_markup=PuzzlesKeyboard.get_menu_keyboard()
    )
    await callback.answer() 