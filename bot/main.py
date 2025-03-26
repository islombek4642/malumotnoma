import sys
import os

# Loyihaning ildiz papkasini qidiruv yo'liga qo'shish
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Loyihaning ildiz papkasi
if project_root not in sys.path:
    sys.path.append(project_root)

from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import router
from bot.database import create_database
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

async def main():
    create_database()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())  # FSM uchun MemoryStorage
    dp.include_router(router)
    await dp.start_polling(bot)

asyncio.run(main())
