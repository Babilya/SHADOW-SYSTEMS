import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.repositories.osint_data_repository import OSINTDataRepository
from database.db import get_session

logger = logging.getLogger(__name__)
osint_router = Router()


@osint_router.message(Command("osint_data"))
async def cmd_osint_data(message: Message):
    """List OSINT data"""
    try:
        async with get_session() as session:
            repo = OSINTDataRepository(session)
            data = await repo.get_user_osint_data(message.from_user.id, limit=20)
            
            if not data:
                await message.answer("❌ OSINT даних не знайдено")
                return
            
            text = f"🔍 <b>Ваші OSINT дані ({len(data)}):</b>\n\n"
            for item in data:
                text += (
                    f"📋 {item.data_type}\n"
                    f"Файл: {item.filename or 'N/A'}\n"
                    f"Дата: {item.created_at.strftime('%d.%m.%Y')}\n"
                    f"─────────────\n"
                )
            
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error getting OSINT data: {e}")
        await message.answer(f"❌ Помилка: {e}")


@osint_router.message(Command("scan_chat"))
async def cmd_scan_chat(message: Message):
    """Scan telegram chat"""
    text = (
        "🔍 <b>Сканування чату</b>\n\n"
        "Надішліть посилання на чат або ID:"
    )
    await message.answer(text, parse_mode="HTML")


@osint_router.message(Command("geo_scan"))
async def cmd_geo_scan(message: Message):
    """Geo scan chats"""
    text = (
        "🗺️ <b>Гео-сканування</b>\n\n"
        "Надішліть координати (lat,lon):\n\n"
        "Приклад: 50.45,30.52"
    )
    await message.answer(text, parse_mode="HTML")
