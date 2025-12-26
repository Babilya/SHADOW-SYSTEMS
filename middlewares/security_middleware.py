from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

logger = logging.getLogger(__name__)

blocked_users: Dict[int, dict] = {}
kicked_users: Dict[int, dict] = {}

def is_user_blocked(user_id: int) -> bool:
    return user_id in blocked_users and blocked_users[user_id].get("is_blocked", False)

def is_user_kicked(user_id: int) -> bool:
    return user_id in kicked_users and kicked_users[user_id].get("requires_new_key", False)

def block_user(user_id: int, admin_id: int, reason: str, legal_basis: str = None):
    blocked_users[user_id] = {
        "is_blocked": True,
        "blocked_by": admin_id,
        "reason": reason,
        "legal_basis": legal_basis
    }

def kick_user(user_id: int, admin_id: int, reason: str):
    kicked_users[user_id] = {
        "requires_new_key": True,
        "kicked_by": admin_id,
        "reason": reason
    }

def unblock_user(user_id: int):
    if user_id in blocked_users:
        blocked_users[user_id]["is_blocked"] = False

def clear_kick(user_id: int):
    if user_id in kicked_users:
        kicked_users[user_id]["requires_new_key"] = False

class SecurityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        
        if user_id:
            if is_user_blocked(user_id):
                block_info = blocked_users.get(user_id, {})
                reason = block_info.get("reason", "Не вказано")
                
                if isinstance(event, Message):
                    await event.answer(
                        f"🚫 <b>ДОСТУП ЗАБЛОКОВАНО</b>\n\n"
                        f"Причина: {reason}\n\n"
                        f"Зверніться до адміністратора.",
                        parse_mode="HTML"
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Ви заблоковані", show_alert=True)
                
                logger.warning(f"Blocked user {user_id} tried to access bot")
                return
            
            if is_user_kicked(user_id):
                state: FSMContext = data.get("state")
                if state:
                    await state.clear()
                    logger.info(f"FSM cleared for kicked user {user_id}")
                
                if isinstance(event, Message):
                    if event.text and event.text.startswith("/activate"):
                        clear_kick(user_id)
                        return await handler(event, data)
                    
                    await event.answer(
                        "👢 <b>СЕСІЮ ЗАВЕРШЕНО</b>\n\n"
                        "Для продовження роботи введіть новий ліцензійний ключ:\n"
                        "<code>/activate SHADOW-XXXX-XXXX</code>",
                        parse_mode="HTML"
                    )
                    return
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "Введіть новий ліцензійний ключ: /activate",
                        show_alert=True
                    )
                    return
        
        return await handler(event, data)
