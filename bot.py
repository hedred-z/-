from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, Application
from telegram.ext import CallbackContext, Updater
import logging
import time
from datetime import datetime
import asyncio
import pytz

# Токен вашего бота
API_TOKEN = '7510854780:AAFLKxbZ2rQsq10DcQ9uTNg2dvU2PimWtHw'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Структуры данных для пользователей
users = {}
admin_id = 954053674  # ID администратора
days_content = {i: {"videos": []} for i in range(1, 46)}  # Структура дней и видео

# Функция для начала работы с ботом
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    users[user_id] = {"current_day": 1, "completed_days": 0, "notifications_enabled": True}
    await update.message.reply_text(
        "Привет, спасибо что выбрал нас! С нами ты сможешь изучить всю базовую криптовалюту.",
        reply_markup=await get_start_keyboard()
    )

# Функция для получения клавиатуры старта
async def get_start_keyboard():
    keyboard = [['День 1']]
    return {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': True}

# Функция для обработки кнопки "День 1"
async def handle_day_1(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    users[user_id]["current_day"] = 1
    await update.message.reply_text(
        "Ты выбрал День 1. Смотри видео и жми 'Готово' после просмотра!",
        reply_markup=await get_day_1_keyboard()
    )

# Функция для получения клавиатуры для дня 1
async def get_day_1_keyboard():
    keyboard = [['Готово']]
    return {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': True}

# Таймер для кнопки "Готово"
async def handle_done(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_day = users[user_id]["current_day"]

    # Проверка таймера, если меньше чем 3 минуты
    if time.time() - users[user_id].get("last_video_time", 0) < 180:
        await update.message.reply_text("Вы не посмотрели видео! Повторите попытку через 2 минуты 45 секунд.")
    else:
        users[user_id]["completed_days"] += 1
        if users[user_id]["completed_days"] == 45:
            await update.message.reply_text("Поздравляем, вы завершили курс!")
        else:
            await update.message.reply_text(f"Вы завершили День {current_day}. Теперь можете перейти к следующему дню!")

# Рейтинг лучших пользователей
async def get_rating(update: Update, context: CallbackContext) -> None:
    sorted_users = sorted(users.items(), key=lambda x: x[1]["completed_days"], reverse=True)
    leaderboard = "Рейтинг лучших пользователей:\n"
    for i, (user_id, data) in enumerate(sorted_users[:5]):
        leaderboard += f"{i+1}. {data['completed_days']} дней - {user_id}\n"
    await update.message.reply_text(leaderboard)

# Панель администрирования
async def admin_panel(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == admin_id:
        keyboard = [['Редактировать дни', 'Выход']]
        await update.message.reply_text("Добро пожаловать в панель администратора", reply_markup=keyboard)

# Редактирование дня
async def edit_day(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == admin_id:
        day = int(update.message.text.split()[1])
        await update.message.reply_text(f"Вы редактируете День {day}. Введите количество видео:")

# Обработка ввода количества видео
async def set_video_count(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == admin_id:
        day = int(update.message.text.split()[1])
        video_count = int(update.message.text.split()[2])
        days_content[day]["videos"] = video_count
        await update.message.reply_text(f"Вы добавили {video_count} видео для Дня {day}.")

# Главная функция для запуска бота
async def main():
    application = Application.builder().token(API_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('rating', get_rating))
    application.add_handler(CommandHandler('admin_panel', admin_panel))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_day_1, pattern="День 1"))
    application.add_handler(CallbackQueryHandler(handle_done, pattern="Готово"))
    application.add_handler(CallbackQueryHandler(edit_day, pattern="Редактировать"))

    await application.run_polling()

# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())
