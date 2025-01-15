# Развивашка Бот

Telegram-бот для развивающих занятий с детьми. Бот предоставляет различные активности и упражнения для совместного времяпровождения родителей с детьми.

## Функционал

- Творческие задания
- Ежедневные задания
- Ребусы
- Загадки
- Артикулярная гимнастика
- Скороговорки
- Нейрогимнастика
- Система достижений
- Раздел для родителей
- Административная панель

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/razvivashka-bot.git
cd razvivashka-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте необходимые переменные окружения:
```
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=id1,id2,id3
```

4. Запустите бота:
```bash
python main.py
```

## Структура проекта

- `main.py` - точка входа для запуска бота
- `config.py` - конфигурация бота
- `handlers/` - обработчики команд
- `keyboards/` - клавиатуры и кнопки
- `database/` - работа с базой данных
- `services/` - вспомогательные функции

## Требования

- Python 3.7+
- aiogram 3.x
- aiosqlite
- python-dotenv 