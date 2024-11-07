from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
import time
from datetime import datetime
import asyncio

API_TOKEN = '7510854780:AAFLKxbZ2rQsq10DcQ9uTNg2dvU2PimWtHw'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

users = {}
admin_id = 954053674
days_content = {i: {"videos": 1, "completed": False} for i in range(1, 46)}

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    users[user_id] = {"current_day": 1, "completed_days": 0, "notifications_enabled": True, "last_video_time": 0}
    await update.message.reply_text(
        "Привет, добро пожаловать! Смотри видео и нажимай 'Готово' после каждого видео.",
        reply_markup=await get_start_keyboard()
    )

async def get_start_keyboard():
    keyboard = [['День 1']]
    return {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': True}

async def handle_day(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_day = users[user_id]["current_day"]

    if current_day > 45:
        await update.message.reply_text("Вы завершили курс!")
        return

    if current_day == 1:
        await update.message.reply_text(
            "Ты выбрал День 1. Смотри видео и жми 'Готово' после просмотра!",
            reply_markup=await get_day_keyboard(current_day)
        )
    else:
        if users[user_id]["completed_days"] >= current_day:
            await update.message.reply_text(
                f"Ты уже завершил {current_day} день. Продолжай на следующий день!",
                reply_markup=await get_day_keyboard(current_day)
            )
        else:
            await update.message.reply_text(f"Ты должен завершить предыдущий день перед тем, как перейти к Дню {current_day}.")

async def get_day_keyboard(day):
    return {'keyboard': [['Готово']], 'resize_keyboard': True, 'one_time_keyboard': True}

async def handle_done(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_day = users[user_id]["current_day"]

    if time.time() - users[user_id].get("last_video_time", 0) < 180:
        await update.message.reply_text("Вы не посмотрели видео! Повторите попытку через 2 минуты 45 секунд.")
    else:
        users[user_id]["completed_days"] += 1
        users[user_id]["last_video_time"] = time.time()

        if users[user_id]["completed_days"] == 45:
            await update.message.reply_text("Поздравляем, вы завершили курс! 🎉")
        else:
            users[user_id]["current_day"] += 1
            await update.message.reply_text(f"Вы завершили День {current_day}. Переходите к следующему дню!")

async def handle_complete_day(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_day = users[user_id]["current_day"]
    
    if current_day == 45:
        await update.message.reply_text("Вы завершили весь курс! Поздравляем! 🎉")
    else:
        await update.message.reply_text("День завершён. Продолжайте в следующий раз!")

async def admin_panel(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == admin_id:
        keyboard = [['Редактировать дни', 'Выход']]
        await update.message.reply_text("Добро пожаловать в панель администратора.", reply_markup={'keyboard': keyboard, 'resize_keyboard': True})

async def edit_day(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == admin_id:
        day = int(update.message.text.split()[1])
        await update.message.reply_text(f"Вы редактируете День {day}. Введите количество видео:")

async def set_video_count(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == admin_id:
        day = int(update.message.text.split()[1])
        video_count = int(update.message.text.split()[2])
        days_content[day]["videos"] = video_count
        await update.message.reply_text(f"Для Дня {day} установлено {video_count} видео.")

async def get_rating(update: Update, context: CallbackContext) -> None:
    sorted_users = sorted(users.items(), key=lambda x: x[1]["completed_days"], reverse=True)
    leaderboard = "Рейтинг лучших пользователей:\n"
    for i, (user_id, data) in enumerate(sorted_users[:5]):
        leaderboard += f"{i+1}. {data['completed_days']} дней - {user_id}\n"
    await update.message.reply_text(leaderboard)

async def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('rating', get_rating))
    application.add_handler(CommandHandler('admin_panel', admin_panel))

    application.add_handler(CallbackQueryHandler(handle_day, pattern="День"))
    application.add_handler(CallbackQueryHandler(handle_done, pattern="Готово"))
    application.add_handler(CallbackQueryHandler(handle_complete_day, pattern="Завершить день"))
    application.add_handler(CallbackQueryHandler(edit_day, pattern="Редактировать"))
    application.add_handler(MessageHandler(filters.TEXT, set_video_count))

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
