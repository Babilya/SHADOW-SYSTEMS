import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, User, Application
from database.crud import UserCRUD
from config.settings import BOT_TOKEN, DATABASE_URL
from config.templates import MESSAGES
from keyboards.guest_kb import guest_main_kb, tariffs_kb
from keyboards.user_kb import user_main_kb

# Database setup
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_session():
    return SessionLocal()

# Bot setup
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

@router.message()
async def start_handler(message: Message):
    db = await get_session()
    user = UserCRUD.get_or_create(db, str(message.from_user.id), message.from_user.username, message.from_user.first_name)
    
    if message.text == "/start":
        await message.answer(MESSAGES["guest_welcome"], reply_markup=guest_main_kb())
    elif "Тарифи" in message.text:
        await message.answer(MESSAGES["tariffs_list"], reply_markup=tariffs_kb())
    
    db.close()

dp.include_router(router)

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
