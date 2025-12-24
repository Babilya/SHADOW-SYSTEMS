from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.crud import KeyCRUD, ProjectCRUD

router = Router()

@router.message(F.text)
async def auth_key(message: Message, state: FSMContext, db):
    if message.text.startswith("SHADOW-"):
        key = KeyCRUD.get_by_code(db, message.text.upper())
        if key and not key.is_used:
            ProjectCRUD.create(db, leader_id=str(message.from_user.id), 
                             leader_username=message.from_user.username,
                             key_id=key.id, name="Проект", tariff=key.tariff,
                             bots_limit=50, managers_limit=5)
            await message.answer("✅ Авторизація успішна!")
        else:
            await message.answer("❌ Ключ невалідний")
