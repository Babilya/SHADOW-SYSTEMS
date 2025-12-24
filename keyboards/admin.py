from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu() -> InlineKeyboardMarkup:
    """Адміністративне меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="🤖 Боти", callback_data="admin_bots"),
            InlineKeyboardButton(text="💳 Платежі", callback_data="admin_payments")
        ],
        [
            InlineKeyboardButton(text="📝 Кампанії", callback_data="admin_campaigns"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="📈 Аналітика", callback_data="admin_analytics"),
            InlineKeyboardButton(text="🔐 Безпека", callback_data="admin_security")
        ],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_menu")]
    ])

def broadcast_menu() -> InlineKeyboardMarkup:
    """Меню розсилки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка всім", callback_data="broadcast_all")],
        [InlineKeyboardButton(text="👑 Лише преміум", callback_data="broadcast_premium")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ])

def confirm_keyboard() -> InlineKeyboardMarkup:
    """Підтвердження для адміна"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="admin_confirm"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel"),
        ]
    ])
