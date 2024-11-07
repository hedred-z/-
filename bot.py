import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from config import API_TOKEN, CHANNEL_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    welcome_text = f"Здравствуйте, {user.first_name}! Рады, что вы хотите изучать криптовалюту с нами. Нажмите кнопку, чтобы приступить к изучению первого дня."
    
    keyboard = [
        ["Изучить 1-й день"]
    ]
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def get_course_day(day: int) -> str:
    return f"День {day}: Ссылка на видео: https://www.youtube.com/watch?v=example_video_id"

async def learn_day(update: Update, context: CallbackContext) -> None:
    day = 1
    course_content = await get_course_day(day)
    
    await update.message.reply_text(course_content)
    await update.message.reply_text("Пожалуйста, подождите 3 минуты перед переходом к следующему видео...")

def main():
    application = Application.builder().token(API_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("Изучить 1-й день"), learn_day))
    
    application.run_polling()

if __name__ == '__main__':
    main()
