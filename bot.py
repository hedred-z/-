import logging
import re
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from config import API_TOKEN, CHANNEL_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    welcome_text = f"Здравствуйте, {user.first_name}! Рады, что вы хотите изучать криптовалюту с нами. Нажмите кнопку, чтобы приступить к изучению первого дня."
    
    # Создаем клавиатуру для первой кнопки
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

    # Проходим по сообщениям канала и ищем, например, "День 1", "День 2" и т.д.
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
        # Отправляем каждую ссылку по очереди
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

def main():
    application = Application.builder().token(API_TOKEN).build()
    
    # Обработчик команд
    application.add_handler(CommandHandler("start", start))
    
    # Обработчик для кнопки "Изучить 1-й день"
    application.add_handler(MessageHandler(filters.Regex("Изучить 1-й день"), learn_day))
    
    # Обработчик для кнопки "Я посмотрел"
    application.add_handler(MessageHandler(filters.Regex("✅ Я посмотрел"), watched))
    
    application.run_polling()

if __name__ == '__main__':
    main()
