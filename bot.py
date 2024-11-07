import logging
from datetime import datetime, timedelta, time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from config import API_TOKEN

ADMIN_ID = 954053674
video_links_by_day = {}
user_progress = {}
video_link_input = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_keyboard(user_id):
    if user_id == ADMIN_ID:
        days_keyboard = []
        for day in range(1, 46):
            button_text = f"День {day}"
            if day in video_links_by_day:
                button_text += " ✅"
            days_keyboard.append([KeyboardButton(button_text)])
        days_keyboard.append([KeyboardButton("Админ-панель")])
        reply_markup = ReplyKeyboardMarkup(days_keyboard, resize_keyboard=True)
    else:
        day_buttons = [[KeyboardButton(f"День {i}") for i in range(1, len(user_progress) + 2)]]
        reply_markup = ReplyKeyboardMarkup(day_buttons, resize_keyboard=True)
    return reply_markup

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку 'День 1', чтобы приступить к изучению.",
        reply_markup=get_keyboard(user_id)
    )

async def admin_panel(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == ADMIN_ID:
        days_keyboard = [[KeyboardButton(f"День {day}") for day in range(1, 46)]]
        days_keyboard.append([KeyboardButton("Админ-панель")])
        reply_markup = ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Выберите день для добавления видео:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("У вас нет доступа к этой функции.")

async def ask_video_count(update: Update, context: CallbackContext) -> None:
    day = int(update.message.text.split()[1])
    context.user_data['day'] = day
    await update.message.reply_text(f"Сколько видео вы хотите добавить для дня {day}?")

async def save_video_link(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_id = update.message.from_user.id

    if user_message.isdigit() and int(user_message) > 0:
        video_count = int(user_message)
        day = context.user_data.get('day')
        context.user_data['video_count'] = video_count
        video_link_input[day] = 0
        await update.message.reply_text(f"Вы выбрали {video_count} видео для дня {day}. Пожалуйста, отправьте ссылки.")
    elif user_message.startswith('http'):
        day = context.user_data.get('day')
        if day is not None:
            video_count = context.user_data.get('video_count', 0)
            if day not in video_links_by_day:
                video_links_by_day[day] = []
            
            video_links_by_day[day].append(user_message)
            video_link_input[day] += 1

            if video_link_input[day] < video_count:
                await update.message.reply_text(f"Добавьте ссылку на {video_link_input[day] + 1} видео.")
            else:
                await update.message.reply_text(f"Все {video_count} видео добавлены для дня {day}.")
                context.user_data['day'] = None
                video_link_input[day] = 0
                context.user_data['video_count'] = None
        else:
            await update.message.reply_text("Ошибка: день не выбран.")
    else:
        await update.message.reply_text("Пожалуйста, отправьте ссылку на видео.")

async def start_day(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_time = datetime.now()
    
    if user_id in user_progress:
        last_day, next_available_time = user_progress[user_id]
        if current_time < next_available_time:
            remaining_time = next_available_time - current_time
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes = remainder // 60
            time_string = f"{hours} часов" if hours > 0 else ""
            time_string += f" {minutes} минут" if minutes > 0 else ""
            await update.message.reply_text(f"Следующий день будет доступен через {time_string}.")
            return

    if current_time.time() < time(7, 0):
        time_until_access = datetime.combine(current_time.date(), time(7, 0)) - current_time
        time_string = f"{time_until_access.seconds // 3600} часов {time_until_access.seconds % 3600 // 60} минут"
        await update.message.reply_text(f"День будет доступен через {time_string}.")
        return
    
    day = user_progress.get(user_id, (0, None))[0] + 1
    if day in video_links_by_day:
        await update.message.reply_text(f"День {day} - Начинаем просмотр видео!")
        for index, link in enumerate(video_links_by_day[day], start=1):
            await update.message.reply_text(f"Видео {index}: {link}")
        
        await update.message.reply_text("После просмотра всех видео нажмите '✅ Я посмотрел', чтобы завершить этот день.")
    else:
        await update.message.reply_text("Видео для этого дня пока не добавлено.")
    
    next_available_time = current_time + timedelta(days=1)
    user_progress[user_id] = (day, next_available_time)

async def watched(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    last_day, _ = user_progress.get(user_id, (0, datetime.now()))
    await update.message.reply_text(f"Поздравляем! Вы завершили день {last_day}. Завтра будет доступен следующий день.")
    await start_day(update, context)

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("Админ-панель"), admin_panel))
    application.add_handler(MessageHandler(filters.Regex(r"День \d+"), ask_video_count))
    application.add_handler(MessageHandler(filters.Regex(r'http'), save_video_link))
    application.add_handler(MessageHandler(filters.Regex("День 1"), start_day))
    application.add_handler(MessageHandler(filters.Regex("✅ Я посмотрел"), watched))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    
