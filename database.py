import sqlite3
import logging
from collections import defaultdict

conn = sqlite3.connect('data/gym_log.db')
cursor = conn.cursor()

def add_training_data(user_id, exercise_name, repetitions, weight, date):
    table_name = f'user_{user_id}'
    cursor.execute(f'''
        INSERT INTO {table_name} (exercise_name, repetitions, weight, date)
        VALUES (?, ?, ?, ?)
    ''', (exercise_name, repetitions, weight, date))
    conn.commit()
    logging.info(f"Data added for user {user_id} - Exercise: {exercise_name}, Repetitions: {repetitions}, Weight: {weight}, Date: {date}.")

def check_user_exists(user_id):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='user_{user_id}')")
    result = cursor.fetchone()[0]
    return result == 1

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
    logging.info(f"Table created for user {user_id}.")

def get_training_data(user_id):
    table_name = f'user_{user_id}'
    cursor.execute(f'''
        SELECT LOWER(exercise_name), repetitions, weight, date FROM {table_name} ORDER BY date DESC
    ''')
    records = cursor.fetchall()

    # Группируем данные по названию упражнения и дате
    grouped_logs = defaultdict(lambda: defaultdict(list))
    for row in records:
        exercise_name, repetitions, weight, date = row
        grouped_logs[exercise_name][date].append({
            "repetitions": repetitions,
            "weight": weight
        })
    
    logging.info(f"Retrieved and grouped training data for user {user_id}.")
    return grouped_logs

def get_training_data_by_date(user_id):
    table_name = f'user_{user_id}'
    cursor.execute(f'''
        SELECT date, LOWER(exercise_name), repetitions, weight FROM {table_name} ORDER BY date DESC
    ''')
    records = cursor.fetchall()

    # Группируем данные по дате и названию упражнения
    grouped_logs = defaultdict(lambda: defaultdict(list))
    for row in records:
        date, exercise_name, repetitions, weight = row
        grouped_logs[date][exercise_name].append({
            "repetitions": repetitions,
            "weight": weight
        })
    
    logging.info(f"Retrieved and grouped training data by date for user {user_id}.")
    return grouped_logs