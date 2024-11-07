import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from config import API_TOKEN, CHANNEL_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    welcome_text = f"Здравствуйте, {user.first_name}! Рады, что вы хотите изучать криптовалюту с нами. Нажмите кнопку, чтобы приступить к изучению первого дня."
    
    keyboard = [
        ["Изучить 1-й день"]
    ]
    update.message.reply_text(welcome_text, reply_markup=keyboard)

def get_course_day(day: int) -> str:
    return f"День {day}: Ссылка на видео: https://www.youtube.com/watch?v=example_video_id"

def learn_day(update: Update, context: CallbackContext) -> None:
    day = 1
    course_content = get_course_day(day)
    
    update.message.reply_text(course_content)
    update.message.reply_text("Пожалуйста, подождите 3 минуты перед переходом к следующему видео...")

def main():
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.regex("Изучить 1-й день"), learn_day))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
