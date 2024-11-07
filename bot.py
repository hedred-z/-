import logging
from datetime import datetime, timedelta, time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from config import API_TOKEN

# Идентификатор администратора
ADMIN_ID = 954053674

# Хранилище для ссылок (можно заменить на базу данных)
video_links_by_day = {}

# Состояние пользователя: последний пройденный день и время доступа к следующему дню
user_progress = {}

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для отображения клавиатуры с учетом роли пользователя
def get_keyboard(user_id):
    if user_id == ADMIN_ID:
        # Клавиатура с кнопкой "Админ-панель" только для администратора
        return ReplyKeyboardMarkup(
            [["Начать день"], ["Админ-панель"]], 
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup([["День 1"]], resize_keyboard=True)

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку 'Начать день', чтобы приступить к изучению.",
        reply_markup=get_keyboard(user_id)
    )

async def admin_panel(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == ADMIN_ID:
        # Панель администратора с выбором дня
        days_keyboard = [[str(day)] for day in range(1, 46)]
        reply_markup = ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Выберите день для добавления видео:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("У вас нет доступа к этой функции.")

async def ask_video_count(update: Update, context: CallbackContext) -> None:
    day = int(update.message.text)
    if update.message.from_user.id == ADMIN_ID:
        # Спросим количество видео для выбранного дня
        context.user_data['day'] = day
        await update.message.reply_text(f"Сколько видео вы хотите добавить для дня {day}?")
    else:
        await update.message.reply_text("У вас нет доступа к этой функции.")

async def save_video_link(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    if user_message.startswith('http'):
        day = context.user_data.get('day')
        if day is not None:
            if day not in video_links_by_day:
                video_links_by_day[day] = []
            video_links_by_day[day].append(user_message)
            await update.message.reply_text(f"Ссылка на видео добавлена для дня {day}.")
        else:
            await update.message.reply_text("Ошибка: день не выбран.")
    else:
        await update.message.reply_text("Пожалуйста, отправьте ссылку на видео.")

async def start_day(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_time = datetime.now()
    
    # Проверка прогресса пользователя и времени доступа
    if user_id in user_progress:
        last_day, next_available_time = user_progress[user_id]
        if current_time < next_available_time:
            remaining_time = next_available_time - current_time
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            await update.message.reply_text(f"Следующий день будет доступен через {hours} часов и {minutes} минут.")
            return

    # Проверка, что день доступен не раньше 7 утра
    if current_time.time() < time(7, 0):
        time_until_access = datetime.combine(current_time.date(), time(7, 0)) - current_time
        await update.message.reply_text(f"День будет доступен через {time_until_access.seconds // 3600} часов и {time_until_access.seconds % 3600 // 60} минут.")
        return
    
    # Отправляем видео для текущего дня
    day = user_progress.get(user_id, (0, None))[0] + 1
    if day in video_links_by_day:
        await update.message.reply_text(f"День {day} - Начинаем просмотр видео!")
        for index, link in enumerate(video_links_by_day[day], start=1):
            await update.message.reply_text(f"Видео {index}: {link}")
        
        await update.message.reply_text("После просмотра всех видео нажмите '✅ Я посмотрел', чтобы завершить этот день.")
    else:
        await update.message.reply_text("Видео для этого дня пока не добавлено.")
    
    # Обновляем прогресс пользователя
    next_available_time = current_time + timedelta(days=1)
    user_progress[user_id] = (day, next_available_time)

async def watched(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    last_day, _ = user_progress.get(user_id, (0, datetime.now()))
    await update.message.reply_text(f"Поздравляем! Вы завершили день {last_day}. Завтра будет доступен следующий день.")
    await start_day(update, context)

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("Админ-панель"), admin_panel))
    application.add_handler(MessageHandler(filters.Regex(r"^\d+$"), ask_video_count))
    application.add_handler(MessageHandler(filters.Regex(r'http'), save_video_link))  # Проверка на ссылку
    application.add_handler(MessageHandler(filters.Regex("День 1"), start_day))
    application.add_handler(MessageHandler(filters.Regex("✅ Я посмотрел"), watched))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
    
