import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from telegram.constants import ParseMode

from config import API_TOKEN

# Идентификатор администратора
ADMIN_ID = 954053674

# Хранилище для ссылок (можно заменить на базу данных)
video_links_by_day = {}

# Состояния для ConversationHandler
CHOOSING_DAY, ADDING_VIDEOS, ENTERING_LINKS = range(3)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        # Приветственное сообщение для администратора с доступом к панели управления
        await update.message.reply_text("Привет, Админ! Вы можете открыть панель управления, чтобы добавить видео для дней.")
        await admin_panel(update, context)
    else:
        # Приветственное сообщение для пользователя
        await update.message.reply_text("Добро пожаловать! Чтобы начать обучение, выберите первый день.")
        await learn_day(update, context, day=1)

async def admin_panel(update: Update, context: CallbackContext) -> int:
    # Показ панели администратора с выбором дня
    days_keyboard = [[str(day)] for day in range(1, 46)]
    reply_markup = ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите день, для которого хотите добавить видео:", reply_markup=reply_markup)
    return CHOOSING_DAY

async def choose_day(update: Update, context: CallbackContext) -> int:
    # Получаем выбранный день и сохраняем его
    context.user_data['chosen_day'] = int(update.message.text)
    await update.message.reply_text("Сколько видео вы хотите добавить для этого дня?")
    return ADDING_VIDEOS

async def add_videos(update: Update, context: CallbackContext) -> int:
    # Получаем количество видео и начинаем добавление ссылок
    num_videos = int(update.message.text)
    context.user_data['num_videos'] = num_videos
    context.user_data['video_links'] = []
    await update.message.reply_text("Введите ссылку на первое видео:")
    return ENTERING_LINKS

async def enter_links(update: Update, context: CallbackContext) -> int:
    # Получаем ссылку на видео и сохраняем её
    video_link = update.message.text
    context.user_data['video_links'].append(video_link)

    # Проверяем, добавлены ли все видео
    if len(context.user_data['video_links']) < context.user_data['num_videos']:
        # Запрос следующей ссылки, если не все добавлены
        await update.message.reply_text(f"Введите ссылку на видео {len(context.user_data['video_links']) + 1}:")
        return ENTERING_LINKS
    else:
        # Сохранение видео для выбранного дня
        day = context.user_data['chosen_day']
        video_links_by_day[day] = context.user_data['video_links']
        await update.message.reply_text(f"Все ссылки для дня {day} успешно сохранены!")
        return admin_panel(update, context)

async def learn_day(update: Update, context: CallbackContext, day: int) -> None:
    # Проверка наличия видео на выбранный день
    if day in video_links_by_day:
        await update.message.reply_text(f"День {day} - Начинаем просмотр видео!")
        
        # Отправляем каждое видео пользователю по очереди
        for index, link in enumerate(video_links_by_day[day], start=1):
            await update.message.reply_text(f"Видео {index}: {link}")
        
        await update.message.reply_text("После просмотра всех видео нажмите '✅ Я посмотрел', чтобы завершить этот день.")
    else:
        await update.message.reply_text("Видео для этого дня пока не добавлено.")

async def watched(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Поздравляем! Вы завершили день. Вы можете перейти к следующему дню.")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Определяем ConversationHandler для панели администратора
    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            CHOOSING_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_day)],
            ADDING_VIDEOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_videos)],
            ENTERING_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_links)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(admin_conv_handler)
    application.add_handler(MessageHandler(filters.Regex("✅ Я посмотрел"), watched))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
