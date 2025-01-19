from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import Database
from keyboards.creativity import CreativityKeyboard
from keyboards.main_menu import MainMenuKeyboard
from handlers.exercises import send_video, get_direct_download_link
from config import config
import random
import logging

router = Router()

class CreativityStates(StatesGroup):
    waiting_for_photo = State()

SECTION_DESCRIPTIONS = {
    "drawing": {
        "title": "🎨 Рисование",
        "description": (
            "Добро пожаловать в раздел Рисования!\n\n"
            "Здесь ты найдешь увлекательные мастер-классы, которые помогут:\n"
            "• Развить творческие способности\n"
            "• Освоить разные техники рисования\n"
            "• Создать красивые картины\n\n"
            "За каждый выполненный мастер-класс ты получишь 💎 Алмаз!"
        )
    },
    "paper": {
        "title": "📄 Бумажное творчество",
        "description": (
            "Добро пожаловать в раздел Бумажного творчества!\n\n"
            "Здесь ты научишься создавать:\n"
            "• Оригами\n"
            "• Аппликации\n"
            "• Объемные фигуры\n\n"
            "За каждый выполненный мастер-класс ты получишь 💎 Алмаз!"
        )
    },
    "sculpting": {
        "title": "🏺 Лепка",
        "description": (
            "Добро пожаловать в раздел Лепки!\n\n"
            "Здесь ты научишься:\n"
            "• Работать с пластилином\n"
            "• Создавать объемные фигуры\n"
            "• Развивать мелкую моторику\n\n"
            "За каждый выполненный мастер-класс ты получишь 💎 Алмаз!"
        )
    }
}

MOTIVATION_MESSAGES = [
    "🌟 Великолепная работа! Ты настоящий творец!",
    "✨ Потрясающе! Твои творческие способности растут с каждым днем!",
    "🎨 Прекрасное творение! Продолжай в том же духе!",
    "🎯 Отличный результат! Ты становишься все лучше и лучше!",
    "🌈 Замечательно! Твое творчество вдохновляет!"
]

@router.callback_query(F.data == "creativity")
async def show_creativity_menu(callback: CallbackQuery):
    """Показывает меню раздела творчества"""
    await callback.message.edit_text(
        "🎨 Добро пожаловать в раздел Творчества!\n\n"
        "Здесь тебя ждут увлекательные мастер-классы по:\n"
        "• Рисованию 🎨\n"
        "• Бумажному творчеству 📄\n"
        "• Лепке 🏺\n\n"
        "Выбери направление, которое тебе интересно!",
        reply_markup=CreativityKeyboard.get_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("creativity_"))
async def show_section_menu(callback: CallbackQuery, state: FSMContext):
    """Показывает меню конкретного раздела"""
    section = callback.data.split("_")[1]
    info = SECTION_DESCRIPTIONS.get(section, {})
    
    db = Database()
    # Проверяем доступ к функции для всех разделов, кроме рисования
    if section in ["paper", "sculpting"]:
        # Для бумаги и лепки всегда требуется подписка
        subscription = await db.get_user_subscription(callback.from_user.id)
        if not subscription:
            await callback.message.edit_text(
                "⭐ Доступ к этому разделу ограничен!\n\n"
                "Для доступа к разделу необходима подписка.\n"
                "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
            )
            await callback.answer()
            return
    elif section == "drawing":
        # Для рисования проверяем бесплатную попытку
        has_access = await db.check_feature_access(callback.from_user.id, 'drawing')
        if not has_access:
            await callback.message.edit_text(
                "⭐ Доступ к мастер-классам ограничен!\n\n"
                "Вы уже использовали бесплатную попытку.\n"
                "Для продолжения необходима подписка.\n\n"
                "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
            )
            await callback.answer()
            return
    
    await state.update_data(current_section=section)
    
    await callback.message.edit_text(
        info.get("description", "Описание раздела"),
        reply_markup=CreativityKeyboard.get_section_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "start_masterclass")
async def start_masterclass(callback: CallbackQuery, state: FSMContext):
    """Начинает сессию мастер-класса"""
    data = await state.get_data()
    section = data.get("current_section")
    
    db = Database()
    # Проверяем доступ к функции для всех разделов
    if section in ["paper", "sculpting"]:
        # Для бумаги и лепки всегда требуется подписка
        subscription = await db.get_user_subscription(callback.from_user.id)
        if not subscription:
            await callback.message.edit_text(
                "⭐ Доступ к этому разделу ограничен!\n\n"
                "Для доступа к разделу необходима подписка.\n"
                "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
            )
            await callback.answer()
            return
    elif section == "drawing":
        # Для рисования проверяем бесплатную попытку
        has_access = await db.check_feature_access(callback.from_user.id, 'drawing')
        if not has_access:
            await callback.message.edit_text(
                "⭐ Доступ к мастер-классам ограничен!\n\n"
                "Вы уже использовали бесплатную попытку.\n"
                "Для продолжения необходима подписка.\n\n"
                "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
            )
            await callback.answer()
            return
    
    video = await db.get_next_creativity_video(callback.from_user.id, section)
    
    if video:
        # Увеличиваем счетчик использования для рисования
        if section == "drawing":
            await db.increment_feature_attempt(callback.from_user.id, 'drawing')
        
        # Проверяем, было ли видео уже выполнено
        is_completed = await db.is_creativity_masterclass_completed(callback.from_user.id, video['id'])
        
        await state.update_data(current_video=video)
        await send_masterclass_video(callback.message, video, is_completed)
    else:
        await callback.message.edit_text(
            "К сожалению, сейчас нет доступных мастер-классов.",
            reply_markup=CreativityKeyboard.get_section_keyboard()
        )
    await callback.answer()

async def send_masterclass_video(message, video, is_completed):
    """Отправляет видео мастер-класса"""
    try:
        # Получаем прямую ссылку на видео
        direct_link = await get_direct_download_link(video['video_url'])
        
        # Формируем текст описания
        text = f"🎨 {video['title']}\n\n{video['description']}\n\n"
        
        if is_completed:
            text += "✅ Вы уже выполнили этот мастер-класс!"
        else:
            text += "Посмотри видео и попробуй повторить!"
        
        # Отправляем видео
        success = await send_video(
            bot=message.bot,
            chat_id=message.chat.id,
            video_url=direct_link,
            caption=text,
            reply_markup=CreativityKeyboard.get_masterclass_keyboard(
                video['id'],
                show_completion=not is_completed
            )
        )
        
        if not success:
            await message.answer(
                "Произошла ошибка при загрузке видео. Попробуйте позже.",
                reply_markup=CreativityKeyboard.get_section_keyboard()
            )
            
    except Exception as e:
        logging.error(f"Error sending masterclass video: {e}")
        await message.answer(
            "Произошла ошибка при загрузке видео. Попробуйте позже.",
            reply_markup=CreativityKeyboard.get_section_keyboard()
        )

@router.callback_query(F.data.startswith("complete_masterclass_"))
async def complete_masterclass(callback: CallbackQuery, state: FSMContext):
    """Отмечает мастер-класс как выполненный"""
    try:
        data = await state.get_data()
        section = data.get("current_section")
        
        db = Database()
        # Проверяем доступ к функции для всех разделов
        if section in ["paper", "sculpting"]:
            # Для бумаги и лепки всегда требуется подписка
            subscription = await db.get_user_subscription(callback.from_user.id)
            if not subscription:
                await callback.message.edit_text(
                    "⭐ Доступ к этому разделу ограничен!\n\n"
                    "Для доступа к разделу необходима подписка.\n"
                    "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                    reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
                )
                await callback.answer()
                return
        elif section == "drawing":
            # Для рисования проверяем бесплатную попытку
            has_access = await db.check_feature_access(callback.from_user.id, 'drawing')
            if not has_access:
                await callback.message.edit_text(
                    "⭐ Доступ к мастер-классам ограничен!\n\n"
                    "Вы уже использовали бесплатную попытку.\n"
                    "Для продолжения необходима подписка.\n\n"
                    "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                    reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
                )
                await callback.answer()
                return
        
        video_id = int(callback.data.split('_')[2])
        
        # Получаем текущее видео
        current_video = await db.get_creativity_video_by_id(video_id)
        if not current_video:
            await callback.message.edit_caption(
                caption="Ошибка: видео не найдено",
                reply_markup=CreativityKeyboard.get_back_button()
            )
            return

        # Отмечаем мастер-класс как выполненный
        success = await db.complete_creativity_masterclass(callback.from_user.id, video_id)
        
        if success:
            # Увеличиваем счетчик использования функции для раздела рисования
            if section == "drawing":
                await db.increment_feature_attempt(callback.from_user.id, 'drawing')
            
            # Получаем токен "Алмаз"
            token = await db.get_token_by_id(9)
            if token:
                text = (
                    "🎉 Поздравляем! Ты успешно выполнил мастер-класс!\n"
                    f"Получаешь награду: {token['emoji']} {token['name']}!\n\n"
                    f"Текущий мастер-класс: {current_video['title']}"
                )
            else:
                text = (
                    "🎉 Поздравляем! Ты успешно выполнил мастер-класс!\n\n"
                    f"Текущий мастер-класс: {current_video['title']}"
                )
            
            # Создаем клавиатуру с кнопками навигации, скрываем кнопки выполнения
            markup = CreativityKeyboard.get_masterclass_keyboard(
                current_video['id'],
                show_completion=False  # скрываем кнопки после выполнения
            )
        else:
            text = "Произошла ошибка при сохранении результата. Попробуйте еще раз."
            markup = CreativityKeyboard.get_masterclass_keyboard(video_id, show_completion=True)
        
        await callback.message.edit_caption(
            caption=text,
            reply_markup=markup
        )
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error in complete_masterclass: {e}")
        await callback.message.edit_caption(
            caption="Произошла ошибка при выполнении мастер-класса. Попробуйте еще раз.",
            reply_markup=CreativityKeyboard.get_masterclass_keyboard(video_id, show_completion=True)
        )
        await callback.answer()

@router.callback_query(F.data.startswith("postpone_masterclass_"))
async def postpone_masterclass(callback: CallbackQuery, state: FSMContext):
    """Откладывает текущий мастер-класс и показывает следующий"""
    data = await state.get_data()
    section = data.get("current_section")
    
    db = Database()
    # Проверяем доступ к функции для всех разделов
    if section in ["paper", "sculpting"]:
        # Для бумаги и лепки всегда требуется подписка
        subscription = await db.get_user_subscription(callback.from_user.id)
        if not subscription:
            await callback.message.edit_text(
                "⭐ Доступ к этому разделу ограничен!\n\n"
                "Для доступа к разделу необходима подписка.\n"
                "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
            )
            await callback.answer()
            return
    elif section == "drawing":
        # Для рисования проверяем бесплатную попытку
        has_access = await db.check_feature_access(callback.from_user.id, 'drawing')
        if not has_access:
            await callback.message.edit_text(
                "⭐ Доступ к мастер-классам ограничен!\n\n"
                "Вы уже использовали бесплатную попытку.\n"
                "Для продолжения необходима подписка.\n\n"
                "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
            )
            await callback.answer()
            return
    
    next_video = await db.get_next_creativity_video(callback.from_user.id, section)
    
    if next_video:
        await state.update_data(current_video=next_video)
        await send_masterclass_video(callback.message, next_video, False)
    else:
        await callback.message.edit_text(
            "Больше нет доступных мастер-классов.",
            reply_markup=CreativityKeyboard.get_section_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("send_photo_"))
async def request_photo(callback: CallbackQuery, state: FSMContext):
    """Запрашивает фото выполненной работы"""
    await callback.answer()
    await state.set_state(CreativityStates.waiting_for_photo)
    await callback.message.answer(
        "Пожалуйста, отправьте фото вашей работы. "
        "Для отмены нажмите кнопку 'Отмена'.",
        reply_markup=CreativityKeyboard.get_photo_cancel_keyboard()
    )

@router.message(F.photo, CreativityStates.waiting_for_photo)
async def process_photo(message: Message, state: FSMContext):
    """Обрабатывает полученное фото"""
    data = await state.get_data()
    current_video = data.get("current_video")
    
    # Отправляем фото в канал
    await message.bot.send_photo(
        chat_id=config.PHOTO_CHANNEL_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"🎨 Новая работа от @{message.from_user.username}!\n"
            f"Мастер-класс: {current_video['title']}"
        )
    )
    
    # Проверяем статус выполнения
    db = Database()
    is_completed = await db.is_creativity_masterclass_completed(message.from_user.id, current_video['id'])
    
    await message.answer(
        "🌟 Спасибо за фото! Оно уже опубликовано в нашем канале творчества!",
        reply_markup=CreativityKeyboard.get_masterclass_keyboard(current_video['id'], show_completion=not is_completed)
    )
    await state.clear()

@router.callback_query(F.data == "cancel_photo")
async def cancel_photo(callback: CallbackQuery, state: FSMContext):
    """Отменяет отправку фото"""
    data = await state.get_data()
    current_video = data.get("current_video")
    
    # Проверяем статус выполнения
    db = Database()
    is_completed = await db.is_creativity_masterclass_completed(callback.from_user.id, current_video['id'])
    
    await state.clear()
    await send_masterclass_video(callback.message, current_video, is_completed)
    await callback.answer()

@router.callback_query(F.data.startswith(("next_masterclass_", "prev_masterclass_")))
async def navigate_masterclasses(callback: CallbackQuery, state: FSMContext):
    """Навигация между мастер-классами"""
    try:
        direction = "next" if callback.data.startswith("next") else "prev"
        video_id = int(callback.data.split("_")[2])
        
        data = await state.get_data()
        section = data.get("current_section")
        
        db = Database()
        # Проверяем доступ к функции для всех разделов
        if section in ["paper", "sculpting"]:
            # Для бумаги и лепки всегда требуется подписка
            subscription = await db.get_user_subscription(callback.from_user.id)
            if not subscription:
                await callback.message.edit_caption(
                    caption="⭐ Доступ к этому разделу ограничен!\n\n"
                    "Для доступа к разделу необходима подписка.\n"
                    "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                    reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
                )
                await callback.answer()
                return
        elif section == "drawing":
            # Для рисования проверяем бесплатную попытку
            has_access = await db.check_feature_access(callback.from_user.id, 'drawing')
            if not has_access:
                await callback.message.edit_caption(
                    caption="⭐ Доступ к мастер-классам ограничен!\n\n"
                    "Вы уже использовали бесплатную попытку.\n"
                    "Для продолжения необходима подписка.\n\n"
                    "Перейдите в раздел «Для мам», чтобы узнать подробности.",
                    reply_markup=MainMenuKeyboard.get_keyboard(callback.from_user.id)
                )
                await callback.answer()
                return
        
        next_video = await db.get_next_creativity_video(
            callback.from_user.id,
            section,
            current_id=video_id,
            direction=direction
        )
        
        if next_video:
            # Проверяем, было ли видео уже выполнено
            is_completed = await db.is_creativity_masterclass_completed(callback.from_user.id, next_video['id'])
            
            await state.update_data(current_video=next_video)
            await send_masterclass_video(callback.message, next_video, is_completed)
        else:
            direction_text = "следующих" if direction == "next" else "предыдущих"
            await callback.message.edit_caption(
                caption=f"В этом направлении больше нет {direction_text} мастер-классов.",
                reply_markup=CreativityKeyboard.get_masterclass_keyboard(video_id, show_completion=False)
            )
        
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in navigate_masterclasses: {e}")
        await callback.message.edit_caption(
            caption="Произошла ошибка при навигации между мастер-классами.",
            reply_markup=CreativityKeyboard.get_back_button()
        )
        await callback.answer()

@router.callback_query(F.data == "back_to_creativity")
async def back_to_creativity(callback: CallbackQuery, state: FSMContext):
    """Возвращает в главное меню творчества"""
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "Выберите направление творчества:",
        reply_markup=CreativityKeyboard.get_menu_keyboard()
    ) 