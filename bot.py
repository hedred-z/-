from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import logging
import asyncio

TOKEN = '7510854780:AAHHsrY_dg09A569k94C1rYWsrgdBEBeApY'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

course_data = {
    1: ["https://example.com/video1"],
    2: ["https://example.com/video2", "https://example.com/video3"],
}

user_data = {}
SELECT_DAY, ADD_VIDEOS, EDIT_VIDEOS = range(3)
admin_id = 954053674

async def start(update, context):
    user_id = update.message.from_user.id
    user_data[user_id] = {'day': 1, 'videos_watched': 0}
    await update.message.reply_text('Welcome to the course! Press "Watched ✅" to start.')
    await send_video(update, user_id)

async def send_video(update, user_id):
    day = user_data[user_id]['day']
    videos = course_data.get(day, [])
    if videos:
        video_link = videos[user_data[user_id]['videos_watched']]
        keyboard = [[InlineKeyboardButton("Watched ✅", callback_data='watched')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Day {day}: Watch the video here: {video_link}", reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"You've completed the course for day {day}!")
        await main_menu(update)

async def button(update, context):
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
            await query.edit_message_text(f"Day {day} completed! Go to the main menu.")
            await main_menu(update)

async def main_menu(update):
    keyboard = [[InlineKeyboardButton("Main menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Day completed! Go to the main menu.", reply_markup=reply_markup)

async def admin_panel(update, context):
    if update.message.from_user.id == admin_id:
        keyboard = [
            [InlineKeyboardButton("Add video", callback_data='add_video')],
            [InlineKeyboardButton("Edit video", callback_data='edit_video')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Welcome to the admin panel!", reply_markup=reply_markup)
    else:
        await update.message.reply_text("You are not an admin!")

async def add_video(update, context):
    if update.message.from_user.id == admin_id:
        day = int(context.args[0])
        video_count = int(context.args[1])
        for i in range(video_count):
            video_link = context.args[i + 2]
            if day not in course_data:
                course_data[day] = []
            course_data[day].append(video_link)
        await update.message.reply_text(f"Videos added for day {day}.")
    else:
        await update.message.reply_text("You are not an admin!")

async def edit_video(update, context):
    if update.message.from_user.id == admin_id:
        keyboard = []
        for day in range(1, 46):
            keyboard.append([InlineKeyboardButton(f"Day {day}", callback_data=f"edit_{day}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose a day to edit:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("You are not an admin!")

async def edit_day_video(update, context):
    if update.message.from_user.id == admin_id:
        day = int(update.callback_query.data.split('_')[1])
        videos = course_data.get(day, [])
        await update.callback_query.edit_message_text(f"Current videos for day {day}: {', '.join(videos)}. Enter new links separated by spaces.")
        return EDIT_VIDEOS
    else:
        await update.message.reply_text("You are not an admin!")

async def handle_new_video_links(update, context):
    if update.message.from_user.id == admin_id:
        day = int(update.callback_query.data.split('_')[1])
        new_links = update.message.text.split()
        course_data[day] = new_links
        await update.message.reply_text(f"Videos for day {day} have been updated.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("You are not an admin!")

async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(MessageHandler(filters.TEXT, add_video))
    application.add_handler(CallbackQueryHandler(button, pattern='^watched$'))
    application.add_handler(CallbackQueryHandler(edit_day_video, pattern='^edit_'))

    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_day_video, pattern='^edit_')],
        states={
            EDIT_VIDEOS: [MessageHandler(filters.TEXT, handle_new_video_links)],
        },
        fallbacks=[],
    )
    application.add_handler(conversation_handler)

    await application.run_polling()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(main())
    else:
        loop.run_until_complete(main())
