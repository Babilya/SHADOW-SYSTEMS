import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.repositories.payment_repository import PaymentRepository
from database.repositories.user_repository import UserRepository
from database.db import get_session

logger = logging.getLogger(__name__)
payments_router = Router()


@payments_router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Show user balance"""
    try:
        async with get_session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(message.from_user.id)
            
            if not user:
                await message.answer("❌ Користувача не знайдено")
                return
            
            balance = user.statistics.get('balance', 0) if user.statistics else 0
            text = f"💰 <b>Ваш баланс:</b> {balance} UAH"
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        await message.answer(f"❌ Помилка: {e}")


@payments_router.message(Command("payments"))
async def cmd_payments(message: Message):
    """Show payment history"""
    try:
        async with get_session() as session:
            repo = PaymentRepository(session)
            payments = await repo.get_user_payments(message.from_user.id, limit=10)
            
            if not payments:
                await message.answer("❌ Платежів не знайдено")
                return
            
            text = "💳 <b>Історія платежів:</b>\n\n"
            for pay in payments:
                text += (
                    f"Сума: {pay.amount} {pay.currency}\n"
                    f"Статус: {pay.status}\n"
                    f"Дата: {pay.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                    f"─────────────\n"
                )
            
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        await message.answer(f"❌ Помилка: {e}")


@payments_router.message(Command("top_up"))
async def cmd_top_up(message: Message):
    """Top up balance with Telegram Stars"""
    text = (
        "⭐ <b>Поповнення за допомогою Telegram Stars</b>\n\n"
        "Телеграм зірки - безпечний спосіб платежу\n\n"
        "💳 <b>Ціни:</b>\n"
        "⭐ 1 = 0.01 USD\n"
        "⭐ 100 = 1 USD\n"
        "⭐ 1000 = 10 USD\n\n"
        "Введіть кількість зірок:"
    )
    await message.answer(text, parse_mode="HTML")
