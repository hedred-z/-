from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from datetime import datetime, timedelta
import logging

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Статусы
SELECT_DAY, ADD_VIDEOS = range(2)

# Данные пользователей
user_data = {}
admin_id = 954053674  # ID администратора

# Для хранения информации о днях и видео
course_data = {day: [] for day in range(1, 46)}  # 45 дней, список видео для каждого дня

def start(update: Update, context):
    user_id = update.message.from_user.id

    # Приветственное сообщение
    welcome_message = "Здравствуйте, рады, что вы хотите изучать криптовалюту с нами. Нажмите на кнопку, чтобы приступить к изучению первого дня."

    # Кнопки
    keyboard = [['Изучить 1-й день']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(welcome_message, reply_markup=reply_markup)
    return SELECT_DAY

def select_day(update: Update, context):
    user_id = update.message.from_user.id

    if update.message.text == "Изучить 1-й день":
        # Проверка доступности дня
        current_time = datetime.now()
        start_of_day = datetime(current_time.year, current_time.month, current_time.day, 7, 0, 0)

        if current_time < start_of_day:
            remaining_time = start_of_day - current_time
            update.message.reply_text(f"День будет доступен через {remaining_time}.")
            return SELECT_DAY

        # Проверяем видео для первого дня
        if len(course_data[1]) == 0:
            update.message.reply_text("Администратор еще не добавил видео для первого дня. Пожалуйста, подождите.")
            return SELECT_DAY

        # Отправляем видео для первого дня
        video_link = course_data[1][0]  # Ссылка на первое видео
        update.message.reply_text(f"День 1: Введение в криптовалюты\nСсылка на первое видео: {video_link}")

        # Кнопка "Просмотрено"
        keyboard = [['Просмотрено ✅']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Просмотрите видео и нажмите 'Просмотрено', чтобы продолжить.", reply_markup=reply_markup)

        user_data[user_id] = {'day': 1, 'videos_watched': 0, 'time_started': current_time}
        return SELECT_DAY

def mark_as_viewed(update: Update, context):
    user_id = update.message.from_user.id

    if user_id not in user_data:
        return SELECT_DAY

    # Проверка, что видео еще не было просмотрено
    current_time = datetime.now()
    time_elapsed = current_time - user_data[user_id]['time_started']
    if time_elapsed < timedelta(minutes=3):
        update.message.reply_text(f"Для начала посмотрите видео. Оставшееся время: {timedelta(minutes=3) - time_elapsed}")
        return SELECT_DAY

    # Увеличиваем количество просмотренных видео
    user_data[user_id]['videos_watched'] += 1

    # Если видео просмотрено, отправляем следующее
    if user_data[user_id]['videos_watched'] < len(course_data[1]):
        video_link = course_data[1][user_data[user_id]['videos_watched']]
        update.message.reply_text(f"Ссылка на следующее видео: {video_link}")
        return SELECT_DAY

    # Все видео просмотрены, завершаем день
    update.message.reply_text(f"Поздравляем, вы изучили 1/45 дней! Продолжайте в том же духе.")
    keyboard = [['Главное меню']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Завершили день. Нажмите 'Главное меню' для продолжения.", reply_markup=reply_markup)

    return ConversationHandler.END

def admin_panel(update: Update, context):
    user_id = update.message.from_user.id

    if user_id != admin_id:
        update.message.reply_text("У вас нет доступа к админ панели.")
        return SELECT_DAY

    # Администраторская панель
    keyboard = [[f"День {i}" for i in range(1, 46)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Выберите день для добавления видео:", reply_markup=reply_markup)
    return ADD_VIDEOS

def add_videos(update: Update, context):
    user_id = update.message.from_user.id

    if user_id != admin_id:
        return SELECT_DAY

    day_number = int(update.message.text.split()[1])  # Получаем номер дня
    update.message.reply_text(f"Вы выбрали день {day_number}. Сколько видео вы хотите добавить?")
    return ADD_VIDEOS

def store_video_links(update: Update, context):
    user_id = update.message.from_user.id
    day_number = int(update.message.text.split()[1])  # Получаем номер дня

    video_links = []
    for i in range(int(update.message.text)):  # Запрашиваем ссылки на видео
        update.message.reply_text(f"Введите ссылку на видео {i+1}:")
        video_link = update.message.text  # Сохранить ссылку
        video_links.append(video_link)

    course_data[day_number] = video_links  # Сохраняем ссылки для дня
    update.message.reply_text(f"Видео для дня {day_number} добавлены.")
    return ConversationHandler.END

def main():
    updater = Updater("YOUR_API_KEY", use_context=True)
    dp = updater.dispatcher

    # Конверсии для администратора
    admin_conversation = ConversationHandler(
        entry_points=[CommandHandler('admin', admin_panel)],
        states={
            ADD_VIDEOS: [MessageHandler(Filters.text & ~Filters.command, store_video_links)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(admin_conversation)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, select_day))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, mark_as_viewed))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
