import asyncio
import nest_asyncio  # Для совместимости с активным циклом событий
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import logging
import pytz

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

# Московский часовой пояс
moscow_tz = pytz.timezone('Europe/Moscow')

# Стартовое сообщение
async def start(update: Update, context):
    user_id = update.message.from_user.id

    # Приветственное сообщение
    welcome_message = "Здравствуйте, рады, что вы хотите изучать криптовалюту с нами."

    # День 1 доступен сразу
    await update.message.reply_text(f"День 1: Введение в криптовалюты\nСсылка на видео: {course_data[1][0]}")

    # Кнопка "Просмотрено"
    keyboard = [['Просмотрено ✅']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Просмотрите видео и нажмите 'Просмотрено', чтобы продолжить.", reply_markup=reply_markup)

    user_data[user_id] = {'day': 1, 'videos_watched': 0}
    return SELECT_DAY

# Отметить видео как просмотренное
async def mark_as_viewed(update: Update, context):
    user_id = update.message.from_user.id

    if user_id not in user_data:
        return SELECT_DAY

    # Проверка, что видео еще не было просмотрено
    user_data[user_id]['videos_watched'] += 1

    # Если видео просмотрено, отправляем следующее
    if user_data[user_id]['videos_watched'] < len(course_data[1]):
        video_link = course_data[1][user_data[user_id]['videos_watched']]
        await update.message.reply_text(f"Ссылка на следующее видео: {video_link}")
        return SELECT_DAY

    # Все видео просмотрены, завершаем день
    await update.message.reply_text(f"Поздравляем, вы изучили 1/45 дней! Продолжайте в том же духе.")
    keyboard = [['Главное меню']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Завершили день. Нажмите 'Главное меню' для продолжения.", reply_markup=reply_markup)

    return ConversationHandler.END

# Админ панель
async def admin_panel(update: Update, context):
    user_id = update.message.from_user.id

    if user_id != admin_id:
        await update.message.reply_text("У вас нет доступа к админ панели.")
        return SELECT_DAY

    # Администраторская панель
    keyboard = [[f"День {i}" for i in range(1, 46)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите день для добавления видео:", reply_markup=reply_markup)
    return ADD_VIDEOS

# Добавить видео
async def add_videos(update: Update, context):
    user_id = update.message.from_user.id

    if user_id != admin_id:
        return SELECT_DAY

    day_number = int(update.message.text.split()[1])  # Получаем номер дня
    await update.message.reply_text(f"Вы выбрали день {day_number}. Сколько видео вы хотите добавить?")
    return ADD_VIDEOS

# Хранение ссылок на видео
async def store_video_links(update: Update, context):
    user_id = update.message.from_user.id
    day_number = int(update.message.text.split()[1])  # Получаем номер дня

    # Спрашиваем у администратора ссылки на видео
    await update.message.reply_text("Введите ссылку на видео:")

    # Ожидаем следующего сообщения с ссылкой
    video_link = update.message.text
    course_data[day_number].append(video_link)

    await update.message.reply_text(f"Видео для дня {day_number} добавлено.")
    return ConversationHandler.END

async def main():
    application = Application.builder().token("YOUR_API_KEY").build()

    # Конверсии для администратора
    admin_conversation = ConversationHandler(
        entry_points=[CommandHandler('admin', admin_panel)],
        states={
            ADD_VIDEOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_video_links)],
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(admin_conversation)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mark_as_viewed))

    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    # Используем nest_asyncio для исправления проблемы с циклом событий
    nest_asyncio.apply()  # Это позволяет повторно использовать текущий цикл событий
    asyncio.get_event_loop().run_until_complete(main())  # Запускаем основной код бота
