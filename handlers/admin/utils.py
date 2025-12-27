from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import logging

logger = logging.getLogger(__name__)

async def safe_edit_message(query: CallbackQuery, text: str, reply_markup=None, parse_mode="HTML"):
    try:
        if query.message:
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e) and "query is too old" not in str(e):
            logger.warning(f"TelegramBadRequest in safe_edit_message: {e}")
            raise
