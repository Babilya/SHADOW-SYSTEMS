from enum import Enum
from typing import List, Optional
from functools import wraps
from aiogram.types import Message, CallbackQuery

class UserRole(str, Enum):
    GUEST = "guest"
    LEADER = "leader"
    MANAGER = "manager"
    ADMIN = "admin"

ROLE_HIERARCHY = {
    UserRole.GUEST: 0,
    UserRole.MANAGER: 1,
    UserRole.LEADER: 2,
    UserRole.ADMIN: 3
}

ROLE_NAMES = {
    UserRole.GUEST: "Гість",
    UserRole.LEADER: "Лідер",
    UserRole.MANAGER: "Менеджер",
    UserRole.ADMIN: "Адміністратор"
}

ROLE_PERMISSIONS = {
    UserRole.GUEST: [
        "view_tariffs",
        "submit_application",
        "view_help"
    ],
    UserRole.MANAGER: [
        "view_tariffs",
        "view_help",
        "view_campaigns",
        "create_campaign",
        "view_bots",
        "send_messages",
        "view_analytics"
    ],
    UserRole.LEADER: [
        "view_tariffs",
        "view_help",
        "view_campaigns",
        "create_campaign",
        "view_bots",
        "add_bots",
        "manage_bots",
        "send_messages",
        "view_analytics",
        "view_team",
        "add_manager",
        "remove_manager",
        "view_osint",
        "use_osint",
        "manage_project",
        "view_payments",
        "manage_subscriptions"
    ],
    UserRole.ADMIN: [
        "all"
    ]
}

def has_permission(role: str, permission: str) -> bool:
    if role == UserRole.ADMIN:
        return True
    role_perms = ROLE_PERMISSIONS.get(role, [])
    return permission in role_perms or "all" in role_perms

def get_role_level(role: str) -> int:
    return ROLE_HIERARCHY.get(role, 0)

def check_role_access(required_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            event = args[0] if args else None
            if isinstance(event, (Message, CallbackQuery)):
                user_role = kwargs.get('user_role', UserRole.GUEST)
                if user_role in required_roles or UserRole.ADMIN in [user_role]:
                    return await func(*args, **kwargs)
                else:
                    if isinstance(event, Message):
                        await event.answer("❌ У вас немає доступу до цієї функції")
                    else:
                        await event.answer("❌ Немає доступу", show_alert=True)
                    return None
            return await func(*args, **kwargs)
        return wrapper
    return decorator
