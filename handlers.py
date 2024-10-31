from aiogram import types, Dispatcher
from aiogram.filters.command import Command
from datetime import datetime
from database import *  # Импортируем get_training_data
from utils import add_row
import logging

async def cmd_start(message: types.Message):
    kb = [[types.KeyboardButton(text="Начать новую тренировку")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Привет, я бот для записи твоих тренировок. Начнем тренировку?", reply_markup=keyboard)
    logging.info(f"User {message.from_user.id} initiated the bot.")

async def new_training(message: types.Message):
    await message.reply("Пришлите название упражнения, количество повторений и вес в формате: жим лежа, 8, 60", reply_markup=types.ReplyKeyboardRemove())

async def finish_training(message: types.Message):
    today = datetime.today().strftime('%d-%m-%Y')
    await message.reply(f"Тренировка {today} завершена. Жду тебя снова :)")
    logging.info(f"User {message.from_user.id} finished the training session.")

async def show_logs(message: types.Message):
    user_id = message.from_user.id
    if check_user_exists(user_id):
        logs = get_training_data(user_id)
        if logs:
            # Форматируем вывод для сгруппированных упражнений и дат
            logs_text = ""
            for exercise, dates in logs.items():
                logs_text += f"\n\n<b>{exercise.capitalize()}:</b>\n"  # Название упражнения с заглавной буквы
                for date, entries in dates.items():
                    logs_text += f"\n<b>{date}:</b>\n"  # Дата
                    for entry in entries:
                        logs_text += f"• {entry['repetitions']} повторений, {entry['weight']} кг\n"
            
            await message.answer(f"Ваши тренировки:\n{logs_text}", parse_mode="HTML")
        else:
            await message.answer("У вас еще нет записей тренировок.")
    else:
        await message.answer("Вы еще не начинали тренировку. Начните, отправив команду /start.")
        
async def show_logs_by_date(message: types.Message):
    user_id = message.from_user.id
    if check_user_exists(user_id):
        logs = get_training_data_by_date(user_id)
        if logs:
            # Форматируем вывод для данных, сгруппированных по дате и упражнениям
            logs_text = ""
            for date, exercises in logs.items():
                logs_text += f"\n<b>{date}:</b>\n"  # Дата тренировки
                for exercise, entries in exercises.items():
                    logs_text += f"\n{exercise.capitalize()}:\n"  # Название упражнения
                    for entry in entries:
                        logs_text += f"• {entry['repetitions']} повторений, {entry['weight']} кг\n"
            
            await message.answer(f"Ваши тренировки по датам:\n{logs_text}", parse_mode="HTML")
        else:
            await message.answer("У вас еще нет записей тренировок.")
    else:
        await message.answer("Вы еще не начинали тренировку. Начните, отправив команду /start.")


async def handle_message(message: types.Message):
    kb = [[types.KeyboardButton(text="Закончить тренировку")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Для завершения тренировки нажмите кнопку ниже или напишите 'Закончить тренировку'", reply_markup=keyboard)

    message_text = message.text
    user_id = message.from_user.id
    data = message_text.split(',')
    today = datetime.today().strftime('%d-%m-%Y')

    if check_user_exists(user_id):
        logging.info(f"User {user_id} exists. Adding training data.")
        add_training_data(user_id, data[0], data[1], data[2], today)
    else:
        logging.info(f"User {user_id} not found in database. Creating user table and adding data.")
        create_user_table(user_id)
        add_training_data(user_id, data[0], data[1], data[2], today)

    name_ex, count, weight = await add_row(message_text)
    await message.answer(f"Записал данные: Упражнение - {name_ex}, Повторения - {count}, Вес - {weight}. Жду следующей записи...")

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(new_training, lambda message: "начать новую тренировку" in message.text.lower())
    dp.message.register(finish_training, lambda message: "закончить тренировку" in message.text.lower())
    dp.message.register(show_logs, Command("show_logs"))
    dp.message.register(show_logs_by_date, Command("show_logs_by_date"))  # Регистрируем новую команду
    dp.message.register(handle_message)

