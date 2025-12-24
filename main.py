import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

from database.models import Base, User, Application, Key, Project
from database.crud import UserCRUD, KeyCRUD, ProjectCRUD, ApplicationCRUD
from config.settings import BOT_TOKEN, DATABASE_URL, ADMIN_ID, TARIFFS
from config.templates import MESSAGES, FSM_MESSAGES
from keyboards.guest_kb import guest_main_kb, tariffs_kb
from keyboards.user_kb import user_main_kb
from core.key_generator import generate_key
from core.validation import validate_key
from utils.logger import logger

# DB
engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

def get_db():
    return SessionLocal()

@router.message(Command("start"))
async def start(msg: Message):
    db = get_db()
    try:
        user = UserCRUD.get_or_create(db, str(msg.from_user.id), msg.from_user.username, msg.from_user.first_name)
        project = ProjectCRUD.get_by_leader(db, str(msg.from_user.id))
        if project and project.is_active:
            text = f"🖥 РОБОЧИЙ СТІЛ\n👤 {user.first_name}\n💎 {project.tariff}\n🤖 {project.bots_used}/{project.bots_limit}\n👥 {project.managers_used}/{project.managers_limit}"
            await msg.answer(text, reply_markup=user_main_kb())
        else:
            await msg.answer(MESSAGES["guest_welcome"], reply_markup=guest_main_kb())
    finally:
        db.close()

@router.message(F.text.contains("Тарифи"))
async def show_tariffs(msg: Message):
    await msg.answer(MESSAGES["tariffs_list"], reply_markup=tariffs_kb())

@router.callback_query(F.data.startswith("tariff_"))
async def tariff_detail(query: CallbackQuery):
    tariff = query.data.split("_")[1]
    details = {
        "baseus": "🔹 BASEUS\n✅ 5 ботів\n✅ 1 менеджер\n💰 30д: 8400₴",
        "standard": "🔶 STANDARD\n✅ 50 ботів\n✅ 5 менеджерів\n✅ OSINT\n💰 30д: 8400₴",
        "premium": "👑 PREMIUM\n✅ 100 ботів\n✅ ∞ менеджерів\n✅ OSINT\n💰 30д: 16800₴",
        "person": "💎 PERSON\n✅ ∞ ботів\n✅ ∞ менеджерів\n✅ Все\n💰 Узгоджується"
    }
    if tariff in details:
        await query.message.edit_text(details[tariff] + f"\n\n[Оформити заявку]")
    await query.answer()

@router.message(F.text.contains("Авторизація"))
async def auth_menu(msg: Message):
    await msg.answer("🔐 Введіть ваш ключ доступу (SHADOW-XXXX-XXXX):")

@router.message(F.text.startswith("SHADOW-"))
async def check_key(msg: Message):
    db = get_db()
    try:
        key_code = msg.text.upper()
        key = KeyCRUD.get_by_code(db, key_code)
        
        if not key:
            await msg.answer("❌ Ключ не знайден")
        elif key.is_used:
            await msg.answer("❌ Ключ вже використаний")
        elif key.expires_at < datetime.now():
            await msg.answer("❌ Ключ закінчився")
        else:
            project = ProjectCRUD.create(db,
                leader_id=str(msg.from_user.id),
                leader_username=msg.from_user.username,
                key_id=key.id,
                name=f"Проект {msg.from_user.first_name}",
                tariff=key.tariff,
                bots_limit=TARIFFS.get(key.tariff, {}).get("bots_limit", 50),
                managers_limit=TARIFFS.get(key.tariff, {}).get("managers_limit", 5)
            )
            await msg.answer("✅ Авторизація успішна! Ласкаво просимо! 🎉")
    finally:
        db.close()

@router.message()
async def default(msg: Message):
    await msg.answer("👋 Ласкаво просимо в SHADOW SYSTEM v2.0\n\nОберіть опцію:", reply_markup=guest_main_kb())

dp.include_router(router)

async def main():
    logger.info("🚀 Бот запущено...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
