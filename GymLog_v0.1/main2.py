import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from datetime import datetime
import sqlite3

db_path = 'data/gym_log_0_2.db'

# Подключаемся к базе данных. SQLite создаст файл базы данных, если он не существует
conn = sqlite3.connect(db_path)


cursor = conn.cursor()
today = datetime.today().strftime('%d-%m-%Y')
user_id = 1234567891
name_ex, count, weight = None, None, None

bot = Bot(token="6778184881:AAHwWFtZ1hlDWljgmj_GwUBra0NjU82gW8c") # Объект бота
dp = Dispatcher() # Диспетчер

logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения



def add_row(message_text: str):
    data = message_text.split(',')
    return data[0], data[1], data[2]  # Данные, которые вы хотите записать

def add_training_data(user_id, exercise_name, repetitions, weight, date):
    table_name = f'user_{user_id}'
    cursor.execute(f'''
        INSERT INTO {table_name} (type_of_training, exercise_name, repetitions, weight, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (exercise_name, repetitions, weight, date))
    conn.commit()

def check_user_exists(user_id):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='user_{user_id}')")
    result = cursor.fetchone()[0]
    return result == 1

def create_user_table(user_id):
    table_name = f'user_{user_id}'
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_of_training TEXT,
            exercise_name TEXT,
            repetitions INTEGER,
            weight REAL,
            date DATE
        )
    ''')

    table_name_types = f'user_{user_id}_types_of_trainings'
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name_types} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_of_training TEXT
        )
    ''')

    conn.commit()

def login_user(user_id):
    print(f"Пользователь с ID {user_id} существует в базе данных.")
    view_types_of_trainings(user_id, 'all')
    return('Вы уже зарегестрировали план тренировок. Ваш план тренировок:') 

async def reg_user(user_id, type_of_traing):
    print(f"Пользователь с ID {user_id} не найден в базе данных.")
    create_user_table(user_id)  
    type_of_traing_split = [exercise.strip() for exercise in type_of_traing.split(',')]

    table_name_types = f'user_{user_id}_types_of_trainings'
    values_to_insert = [(exercise,) for exercise in type_of_traing_split]

    cursor.executemany(f'INSERT INTO {table_name_types} (type_of_training) VALUES (?)', values_to_insert)
    conn.commit()


def view_types_of_trainings(user_id, number_of_plan):

    # Выполните SQL-запрос для извлечения данных из второй строки
    table_name_types = f'user_{user_id}_types_of_trainings'

    if number_of_plan == 'all':
        cursor.execute(f'SELECT type_of_training FROM {table_name_types}')

        # Извлечение значений из строк
        row = cursor.fetchone()

        # Печать значений
        v = 1
        qwe = ''
        while row is not None:
            # Извлечение значений из кортежа
            training_type = row[0]
            qwe = (f'Тип тренировки {v}: {training_type}')
            printing_types = printing_types + qwe
            # Получение следующей строки
            row = cursor.fetchone()
            v = v + 1
        return(printing_types)

    elif number_of_plan in ('1', '2', '3', '4', '5'):   
        c = int(number_of_plan) - 1
        zapros = f'SELECT type_of_training FROM {table_name_types} LIMIT 1 OFFSET {c}'
        cursor.execute(zapros)

        # Извлеките значение из второй строки
        row = cursor.fetchone()
        # Проверьте, что результат не пустой, и затем извлеките значение
        if row:
            value = row[0]  # Извлеките значение из первого столбца второй строки
            return(f'Тренировка {number_of_plan}:', value)
        else:
            return('Нет данных')
    else:
        return('error')
            

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # проверка пользователя и регистрация 
    user_id = message.from_user.id
    if check_user_exists(user_id):
        await message.answer(login_user(user_id))

    # регистрация пользователя и ввод программы тренировок
    else:
        await message.answer('Напишите ваш план тренировок. Например: ноги и плечи, спина и бицепс, грудь и трицепс.')
        type_of_traing = message.text         
        reg_user(user_id, type_of_traing)
        await message.answer('Регистрация успешна. Ваш план тренировок:')   
        view_types_of_trainings(user_id, 'all')
           



def main():
    while True:

        message_text = input()

        if message_text == 'stop':
            break

        elif message_text == 'start': 
            # TODO: воткнуть это все в функции  

            # проверка пользователя и регистрация 
            if check_user_exists(user_id):
                login_user(user_id)

            # регистрация пользователя и ввод программы тренировок
            else:
                reg_user(user_id)

        
        elif message_text == 'view_plan':
            view_types_of_trainings(user_id, input()) 

        elif message_text == 'new_workout':

            
            if check_user_exists(user_id):
                print(f"Пользователь с ID {user_id} существует в базе данных.")
                print(f"Какую тренировку начнем? Отправьте цифру")
                view_types_of_trainings(user_id, 'all')
                type_of_workout = input()
                print(f"Отлично! Сегодня тренировка: ")
                view_types_of_trainings(user_id, type_of_workout)

                #тут код записи тренировки

            else:
                print(f"Пользователь с ID {user_id} не найден в базе данных. Зарегестрируйтесь командой start")

        else:
            print('Не понимаю...')

# if __name__ == "__main__":
#     main()
# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

