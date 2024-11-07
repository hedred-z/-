import logging
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

async def get_course_day(day: int, context: CallbackContext) -> str:
    # Проходим по сообщениям канала и ищем, например, "День 1", "День 2" и т.д.
    async for message in context.bot.get_chat_messages(CHANNEL_ID):
        if f"День {day}:" in message.text:
            # Находим ссылку в тексте, которая будет после "День X:"
            start_index = message.text.find("http")
            end_index = message.text.find(" ", start_index)
            video_url = message.text[start_index:end_index] if end_index != -1 else message.text[start_index:]
            return f"День {day}: Ссылка на видео: {video_url}"
    
    return f"Контент для дня {day} не найден."

async def learn_day(update: Update, context: CallbackContext) -> None:
    # Получаем номер дня из текста сообщения (например, если 1-й день, то день=1)
    day = 1
    course_content = await get_course_day(day, context)
    
    # Отправляем видео и сообщение
    await update.message.reply_text(course_content)
    
    # Создаём новую клавиатуру с кнопкой "Я посмотрел" с зелёной галочкой
    keyboard = [
        ["✅ Я посмотрел"]
    ]
    
    # Преобразуем в объект ReplyKeyboardMarkup
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    # Отправляем сообщение с новой кнопкой
    await update.message.reply_text("Пожалуйста, подождите 3 минуты перед переходом к следующему видео...", reply_markup=reply_markup)

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
  
