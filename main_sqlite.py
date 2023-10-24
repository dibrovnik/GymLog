import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from datetime import datetime
import sqlite3

conn = sqlite3.connect('data\gym_log.db')
cursor = conn.cursor()

logging.basicConfig(level=logging.INFO) # Включаем логирование, чтобы не пропустить важные сообщения

bot = Bot(token="6778184881:AAHwWFtZ1hlDWljgmj_GwUBra0NjU82gW8c") # Объект бота
dp = Dispatcher() # Диспетчер

#-------------------------------------------Функции--------------------------------

async def add_row(message_text: str): # функция для добавления строки с данными об упражнении
    
    data = message_text.split(',')
    data_to_write = [data[0], data[1], data[2]] # Данные, которые вы хотите записать
    return data[0], data[1], data[2]

# Функция для записи данных в таблицу пользователя
def add_training_data(user_id, exercise_name, repetitions, weight, date):
    table_name = f'user_{user_id}'
    cursor.execute(f'''
        INSERT INTO {table_name} (exercise_name, repetitions, weight, date)
        VALUES (?, ?, ?, ?)
    ''', (exercise_name, repetitions, weight, date))
    conn.commit()

def check_user_exists(user_id):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='user_{user_id}')")
    result = cursor.fetchone()[0]
    return result == 1

# Функция для создания таблицы для каждого пользователя
def create_user_table(user_id):
    table_name = f'user_{user_id}'
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT,
            repetitions INTEGER,
            weight REAL,
            date DATE
        )
    ''')
    conn.commit()
#-------------------------------------------Функции--------------------------------


#---------------------------------------Обработка сообщений--------------------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Начать новую тренировку")
            # types.KeyboardButton(text="Просмотр предыдущих")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer("привет, я бот для записи твоих тренировок. начнем тренировку?", reply_markup=keyboard)

# @dp.message()
# async def cmd_finish(message: types.Message):
#     kb = [
#         [
#             types.KeyboardButton(text="Закончить тренировку")
#             # types.KeyboardButton(text="Просмотр предыдущих")
#         ],
#     ]
#     keyboard = types.ReplyKeyboardMarkup(
#         keyboard=kb,
#         resize_keyboard=True,
#     )
#     await message.answer('Когда нужно будет завершить тренировку, нажмите на кнопку ниже или напишите "Закончить тренировку"', reply_markup=keyboard)


@dp.message(F.text.lower() == "начать новую тренировку" or "новая")
async def new_training(message: types.Message):
    await message.reply("Отлично! Пришлите название упражнения, количество повторений и вес на подходе в таком формате: жим лежа, 8, 60", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.lower() == "закончить тренировку" or "стоп")
async def finish_training(message: types.Message):
    today = datetime.today().strftime('%d-%m-%Y')
#----------------тут сделать кнопку под сообщением чтобы начать новую тренировку
    await message.reply(f"Тренировка {today} завершена. Буду ждать тебя снова :)")

@dp.message()
async def handle_message(message: types.Message):

    # Вывод кнопки завершения
    kb = [
        [
            types.KeyboardButton(text="Закончить тренировку")
            # types.KeyboardButton(text="Просмотр предыдущих")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer('Когда нужно будет завершить тренировку, нажмите на кнопку ниже или напишите "Закончить тренировку"', reply_markup=keyboard)


    # Сохраняем сообщение в переменную
    message_text = message.text
    user_id = message.from_user.id
    data = message_text.split(',')
    data_to_write = [data[0], data[1], data[2]] # Данные, которые вы хотите записать
    today = datetime.today().strftime('%d-%m-%Y')

    if check_user_exists(user_id):
        print(f"Пользователь с ID {user_id} существует в базе данных.")
        add_training_data(user_id, data[0], data[1], data[2], today)
    else:
        print(f"Пользователь с ID {user_id} не найден в базе данных.")
        create_user_table(user_id)
        add_training_data(user_id, data[0], data[1], data[2], today)     

    name_ex, count, weight = await add_row(message_text)  # Вызываем функцию add_row и сохраняем возвращаемые значения в переменных

    await message.answer(f'Записал данные об упражнении. Название упражнения: {name_ex}, количество повторений: {count} , вес на подходе: {weight}. Жду следующей записи...')



# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


