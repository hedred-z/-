from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
import logging

# Вставьте ваш токен
TOKEN = '7510854780:AAHHsrY_dg09A569k94C1rYWsrgdBEBeApY'

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Данные для курса
course_data = {
    1: ["https://example.com/video1"],
    2: ["https://example.com/video2", "https://example.com/video3"],
    # Дополнительные видео для каждого дня
}

# Данные пользователей
user_data = {}

# Состояния
SELECT_DAY, ADD_VIDEOS = range(2)

# ID администратора
admin_id = 954053674  # Заменено на ваш ID

# Начало курса
def start(update, context):
    user_id = update.message.from_user.id
    user_data[user_id] = {'day': 1, 'videos_watched': 0}
    update.message.reply_text('Добро пожаловать в курс! Нажмите "Просмотрено ✅", чтобы начать.')
    send_video(update, user_id)

# Отправка видео
def send_video(update, user_id):
    day = user_data[user_id]['day']
    videos = course_data.get(day, [])
    if videos:
        video_link = videos[user_data[user_id]['videos_watched']]
        keyboard = [[InlineKeyboardButton("Просмотрено ✅", callback_data='watched')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"День {day}: Посмотрите видео по следующей ссылке: {video_link}", reply_markup=reply_markup)
    else:
        update.message.reply_text(f"Вы завершили обучение на {day} день!")
        main_menu(update)

# Кнопка "Просмотрено"
def button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    if query.data == 'watched':
        user_data[user_id]['videos_watched'] += 1
        day = user_data[user_id]['day']
        videos = course_data.get(day, [])
        if user_data[user_id]['videos_watched'] < len(videos):
            send_video(update, user_id)
        else:
            user_data[user_id]['videos_watched'] = 0
            user_data[user_id]['day'] += 1
            update.callback_query.edit_message_text(f"День {day} завершен! Перейдите в главное меню.")
            main_menu(update)

# Главное меню
def main_menu(update):
    keyboard = [[InlineKeyboardButton("Главное меню", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Вы завершили день! Перейдите в главное меню.", reply_markup=reply_markup)

# Админ-панель
def admin_panel(update, context):
    if update.message.from_user.id == admin_id:
        keyboard = [[InlineKeyboardButton("Добавить видео", callback_data='add_video')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Добро пожаловать в админ-панель!", reply_markup=reply_markup)
    else:
        update.message.reply_text("Вы не администратор!")

# Добавление видео
def add_video(update, context):
    if update.message.from_user.id == admin_id:
        day = int(context.args[0])
        video_count = int(context.args[1])
        for i in range(video_count):
            video_link = context.args[i + 2]
            if day not in course_data:
                course_data[day] = []
            course_data[day].append(video_link)
        update.message.reply_text(f"Добавлены видео для дня {day}.")
    else:
        update.message.reply_text("Вы не администратор!")

# Основные команды
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_panel))
    dp.add_handler(MessageHandler(Filters.text, add_video))

    # Конверсация для выбора дня и добавления видео
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_DAY: [CallbackQueryHandler(main_menu)],
            ADD_VIDEOS: [MessageHandler(Filters.text, add_video)],
        },
        fallbacks=[],
    )
    dp.add_handler(conversation_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
