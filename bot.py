import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import timedelta

API_TOKEN = '7510854780:AAFLKxbZ2rQsq10DcQ9uTNg2dvU2PimWtHw'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

START, IN_PROGRESS, FINISHED, ADMIN_PANEL, EDIT_DAY = range(5)

user_data = {}
admin_id = 954053674

day_links = {}

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'day': 1, 'progress': 0}
    
    user = update.message.from_user
    welcome_message = (
        f"Привет, {user.first_name}! Спасибо, что выбрали нас. "
        "С нами вы сможете изучить базовую криптовалюту.\n\n"
        "Чтобы начать изучать, нажмите на кнопку 'День 1'."
    )
    keyboard = [[("День 1")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    return START

def get_links_for_day(day):
    if day in day_links:
        return day_links[day]
    else:
        return []

async def day_progress(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    current_day = user_data[user_id]['day']
    
    if user_data[user_id]['progress'] == 0:
        await update.message.reply_text(f"Вы начали день {current_day}. Смотрите видео для этого дня!")
        admin_links = get_links_for_day(current_day)
        
        if not admin_links:
            await update.message.reply_text(f"Ссылки для дня {current_day} еще не добавлены администратором.")
        else:
            for link in admin_links:
                await update.message.reply_text(f"Ссылка для дня {current_day}: {link}")
        
        keyboard = [[("Готово")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Нажмите 'Готово', когда завершите просмотр.", reply_markup=reply_markup)
        user_data[user_id]['progress'] = 1
        return IN_PROGRESS
    else:
        await update.message.reply_text("Вы уже прошли этот день. Ждите следующий!")
        return FINISHED

async def finish_day(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    current_day = user_data[user_id]['day']
    
    time_spent = timedelta(minutes=3)
    if time_spent < timedelta(minutes=3):
        remaining_time = timedelta(minutes=3) - time_spent
        await update.message.reply_text(f"Вы не посмотрели видео достаточно долго. Попробуйте снова через {remaining_time}.")
        return IN_PROGRESS
    
    user_data[user_id]['day'] += 1
    await update.message.reply_text(f"Поздравляем! Вы завершили день {current_day}. Переходите к следующему!")
    
    keyboard = [[(f"День {user_data[user_id]['day']}")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Нажмите, чтобы начать следующий день.", reply_markup=reply_markup)
    return FINISHED

async def admin_panel(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == admin_id:
        keyboard = [['Добавить ссылки для дня', 'Редактировать ссылки'], ['Выход']]
        reply_markup = ReplyKeyboardMarkup(keyboard)
        await update.message.reply_text("Админ панель", reply_markup=reply_markup)
        return ADMIN_PANEL
    else:
        await update.message.reply_text("Вы не являетесь администратором.")
        return START

async def add_links(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == admin_id:
        await update.message.reply_text("Введите номер дня, для которого хотите добавить ссылки.")
        return EDIT_DAY
    else:
        await update.message.reply_text("Вы не являетесь администратором.")
        return START

async def edit_day(update: Update, context: CallbackContext):
    day = int(update.message.text.strip())
    user_id = update.message.from_user.id
    if user_id == admin_id:
        await update.message.reply_text(f"Введите ссылки для дня {day} (через запятую). Например: 'link1, link2, link3'.")
        return EDIT_DAY
    else:
        await update.message.reply_text("Вы не являетесь администратором.")
        return START

async def save_links(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == admin_id:
        day = int(update.message.text.split()[0])
        links = update.message.text.split()[1].split(',')
        day_links[day] = links
        await update.message.reply_text(f"Ссылки для дня {day} успешно обновлены.")
        return ADMIN_PANEL
    else:
        await update.message.reply_text("Вы не являетесь администратором.")
        return START

async def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex('^День \d+$'), day_progress))
    application.add_handler(MessageHandler(filters.Regex('^Готово$'), finish_day))
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(MessageHandler(filters.Regex('^Добавить ссылки для дня$'), add_links))
    application.add_handler(MessageHandler(filters.Regex('^Редактировать ссылки$'), add_links))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_links))

    # Replace asyncio.run with application.run_polling
    await application.run_polling()

if __name__ == '__main__':
    main()
