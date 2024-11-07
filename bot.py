from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import logging

# Вставьте ваш токен
TOKEN = '7510854780:AAHHsrY_dg09A569k94C1rYWsrgdBEBeApY'

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
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
SELECT_DAY, EDIT_VIDEOS = range(2)

# ID администратора
admin_id = 954053674  # Замените на ваш ID

# Начало курса
async def start(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id] = {'day': 1, 'videos_watched': 0}
    await update.message.reply_text('Добро пожаловать в курс! Нажмите "Просмотрено ✅", чтобы начать.')
    await send_video(update, user_id)

# Отправка видео
async def send_video(update, user_id):
    day = user_data[user_id]['day']
    videos = course_data.get(day, [])
    if videos:
        video_link = videos[user_data[user_id]['videos_watched']]
        keyboard = [[InlineKeyboardButton("Просмотрено ✅", callback_data='watched')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"День {day}: Посмотрите видео по следующей ссылке: {video_link}", reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"Вы завершили обучение на {day} день!")
        await main_menu(update)

# Кнопка "Просмотрено"
async def button(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if query.data == 'watched':
        user_data[user_id]['videos_watched'] += 1
        day = user_data[user_id]['day']
        videos = course_data.get(day, [])
        if user_data[user_id]['videos_watched'] < len(videos):
            await send_video(update, user_id)
        else:
            user_data[user_id]['videos_watched'] = 0
            user_data[user_id]['day'] += 1
            await query.edit_message_text(f"День {day} завершен! Перейдите в главное меню.")
            await main_menu(update)

# Главное меню
async def main_menu(update):
    keyboard = [[InlineKeyboardButton("Главное меню", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вы завершили день! Перейдите в главное меню.", reply_markup=reply_markup)

# Админ-панель
async def admin_panel(update: Update, context):
    if update.message.from_user.id == admin_id:
        keyboard = [
            [InlineKeyboardButton("Добавить видео", callback_data='add_video')],
            [InlineKeyboardButton("Изменить видео", callback_data='edit_video')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Добро пожаловать в админ-панель!", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Вы не администратор!")

# Редактирование видео
async def edit_video(update: Update, context):
    if update.message.from_user.id == admin_id:
        keyboard = []
        for day in range(1, 46):
            keyboard.append([InlineKeyboardButton(f"День {day}", callback_data=f"edit_{day}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите день для редактирования:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Вы не администратор!")

# Изменение видео для дня
async def edit_day_video(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id == admin_id:
        day = int(query.data.split('_')[1])
        videos = course_data.get(day, [])
        await query.edit_message_text(f"Текущие видео для дня {day}: {', '.join(videos)}. Введите новые ссылки через пробел.")
        context.user_data['day_to_edit'] = day  # Сохранение дня для редактирования
        return EDIT_VIDEOS
    else:
        await query.answer("Вы не администратор!")
        return ConversationHandler.END

# Обработка новых ссылок для видео
async def handle_new_video_links(update: Update, context):
    if update.message.from_user.id == admin_id:
        day = context.user_data['day_to_edit']
        new_links = update.message.text.split()
        course_data[day] = new_links
        await update.message.reply_text(f"Видео для дня {day} были изменены.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Вы не администратор!")
        return ConversationHandler.END

# Основные команды
async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))

    # Диалог для изменения видео
    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_day_video, pattern='^edit_')],
        states={
            EDIT_VIDEOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_video_links)],
        },
        fallbacks=[],
    )
    application.add_handler(conversation_handler)

    # Запуск бота
    await application.start_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
