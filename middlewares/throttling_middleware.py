from aiogram import BaseMiddleware
from core.rate_limiter import limiter

class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = str(event.from_user.id)
        if not limiter.is_allowed(user_id):
            return
        return await handler(event, data)
