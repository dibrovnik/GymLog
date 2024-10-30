import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from logging_config import configure_logging
from dotenv import load_dotenv
import os

# Загрузка переменных из .env
load_dotenv()

# Настройка логирования
configure_logging()

# Получение токена из .env
bot_token = os.getenv("BOT_TOKEN")

bot = Bot(token=bot_token)
dp = Dispatcher()

# Регистрируем обработчики
register_handlers(dp)

async def main():
    logging.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
