import logging
from telegram import Update, ReplyKeyboardMarkup
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

async def get_course_day(day: int) -> str:
    return f"День {day}: Ссылка на видео: https://www.youtube.com/watch?v=example_video_id"

async def learn_day(update: Update, context: CallbackContext) -> None:
    day = 1
    course_content = await get_course_day(day)
    
    # Отправляем видео и сообщение
    await update.message.reply_text(course_content)
    await update.message.reply_text("Пожалуйста, подождите 3 минуты перед переходом к следующему видео...")

def main():
    application = Application.builder().token(API_TOKEN).build()
    
    # Обработчик команд
    application.add_handler(CommandHandler("start", start))
    
    # Обработчик для кнопки "Изучить 1-й день"
    application.add_handler(MessageHandler(filters.Regex("Изучить 1-й день"), learn_day))
    
    application.run_polling()

if __name__ == '__main__':
    main()
