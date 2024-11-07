import logging
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

# Импорт данных из конфигурационного файла
from config import API_TOKEN, CHANNEL_ID

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    welcome_text = f"Здравствуйте, {user.first_name}! Рады, что вы хотите изучать криптовалюту с нами. Нажмите на кнопку, чтобы приступить к изучению первого дня."
    
    # Клавиатура с кнопкой для начала изучения
    keyboard = [
        ["Изучить 1-й день"]
    ]
    
    # Преобразуем в объект ReplyKeyboardMarkup
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Отправляем сообщение с клавиатурой
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def get_course_day(day: int, context: CallbackContext) -> list:
    # Список для хранения всех ссылок на видео
    video_links = []
    
    # Получаем сообщения из канала
    async for message in context.bot.get_chat_messages(CHANNEL_ID):
        if f"День {day}:" in message.text:
            # Ищем все ссылки в сообщении
            links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
            if links:
                video_links.extend(links)
    
    return video_links

async def learn_day(update: Update, context: CallbackContext) -> None:
    day = 1  # Вы можете изменить этот номер дня, например, на 2, 3 и т.д.
    
    # Получаем ссылки на видео для указанного дня
    video_links = await get_course_day(day, context)
    
    if video_links:
        # Отправляем каждое видео по очереди
        for link in video_links:
            await update.message.reply_text(f"Ссылка на видео: {link}")
        
        # Создаем клавиатуру с кнопкой "Я посмотрел"
        keyboard = [
            ["✅ Я посмотрел"]
        ]
        
        # Преобразуем в объект ReplyKeyboardMarkup
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        # Отправляем сообщение с новой кнопкой
        await update.message.reply_text("Пожалуйста, подождите 3 минуты перед переходом к следующему видео...", reply_markup=reply_markup)
    else:
        # Если контент не найден, отправляем сообщение
        await update.message.reply_text("Мы не нашли видео для данного дня. Пожалуйста, изучите канал для получения новых материалов.")

async def watched(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Поздравляем! Вы завершили первый день обучения.")

async def main_menu(update: Update, context: CallbackContext) -> None:
    # Главное меню, которое появляется после завершения первого дня
    keyboard = [
        ["Изучить 2-й день", "Настроить уведомления"],
        ["Рейтинг", "Об авторе"]
    ]
    
    # Преобразуем в объект ReplyKeyboardMarkup
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Отправляем сообщение с клавиатурой
    await update.message.reply_text("Вы завершили первый день! Теперь вы можете начать второй день или настроить уведомления.", reply_markup=reply_markup)

async def notification_settings(update: Update, context: CallbackContext) -> None:
    # Отправляем список кнопок для настройки уведомлений
    keyboard = [
        ["Уведомление о новом дне", "Уведомление о невыполненном дне"]
    ]
    
    # Преобразуем в объект ReplyKeyboardMarkup
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Отправляем сообщение с клавиатурой
    await update.message.reply_text("Выберите, какие уведомления вы хотите получать:", reply_markup=reply_markup)

async def rating(update: Update, context: CallbackContext) -> None:
    # Рейтинг пользователей
    # Пример данных рейтинга
    ranking = [
        "1. Ник1 : 20 дней",
        "2. Ник2 : 18 дней",
        "3. Ник3 : 15 дней"
    ]
    
    # Отправляем рейтинг
    await update.message.reply_text("\n".join(ranking))

async def author_info(update: Update, context: CallbackContext) -> None:
    # Информация о курсе и авторе
    course_info = """
    Добро пожаловать на курс по криптовалютам! Этот курс разработан для того, чтобы помочь вам разобраться в мире криптовалют и блокчейн технологий.
    Весь курс состоит из 45 дней, и каждый день вы будете изучать новые аспекты криптовалют и их применения.
    """
    await update.message.reply_text(course_info)

def main():
    application = Application.builder().token(API_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("Изучить 1-й день"), learn_day))
    application.add_handler(MessageHandler(filters.Regex("✅ Я посмотрел"), watched))
    application.add_handler(MessageHandler(filters.Regex("Настроить уведомления"), notification_settings))
    application.add_handler(MessageHandler(filters.Regex("Рейтинг"), rating))
    application.add_handler(MessageHandler(filters.Regex("Об авторе"), author_info))
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
  
