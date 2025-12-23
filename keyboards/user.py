from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """Головне меню з 2-3 кнопками в ряді"""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Рядок 1: 2 кнопки
        [
            InlineKeyboardButton(text="🤖 Botnet", callback_data="botnet_main"),
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main")
        ],
        # Рядок 2: 2 кнопки
        [
            InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main"),
            InlineKeyboardButton(text="👥 Команда", callback_data="team_main")
        ],
        # Рядок 3: 2 кнопки
        [
            InlineKeyboardButton(text="📦 Підписки", callback_data="subscription_main"),
            InlineKeyboardButton(text="💳 Платежі", callback_data="payments_main")
        ],
        # Рядок 4: 2 кнопки
        [
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_main"),
            InlineKeyboardButton(text="📝 Текстовки", callback_data="texting")
        ],
        # Рядок 5: 2 кнопки
        [
            InlineKeyboardButton(text="📚 Довідка", callback_data="help"),
            InlineKeyboardButton(text="🎯 Онбординг", callback_data="onboarding_start")
        ],
    ])

def main_menu_description() -> str:
    """Опис функцій для головного меню"""
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>

<b>🤖 BOTNET</b> - Управління ботами
Додавайте до 1000+ ботів, ротуйте проксі, прогрівайте перед розсилкою

<b>🔍 OSINT</b> - Розвідка & Парсинг
Геосканування, аналіз користувачів, парсинг чатів, експорт контактів

<b>📊 АНАЛІТИКА</b> - Звіти & Метрики
Дашборд кампаній, AI Sentiment, прогноз ризиків, ROI аналізу

<b>👥 КОМАНДА</b> - Управління менеджерами
Розподіл завдань, рейтинг по якості, статистика активності

<b>📦 ПІДПИСКИ</b> - Тарифи від Free до Elite
Free (безкоштовно) → Standard (300₴) → Premium (600₴) → Elite (1200₴)

<b>💳 ПЛАТЕЖІ</b> - Способи оплати
Карта, Liqpay, Крипто платежі (BTC, ETH, TON)

<b>⚙️ НАЛАШТУВАННЯ</b> - Конфіг & Безпека
Профіль, привидний режим, сповіщення, 2FA, інтеграції

<b>📝 ТЕКСТОВКИ</b> - Кампанії з шаблонами
6 готових шаблонів, A/B тестування, сегментація, автовідправка

<b>📚 ДОВІДКА</b> - Детальна документація
Инструкції по всіх модулях, примери, FAQ

<b>🎯 ОНБОРДИНГ</b> - Навчання новачків
3-рівнева воронка для новичків, sales воронка"""

def subscription_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🆓 Free", callback_data="tier_free"),
            InlineKeyboardButton(text="⭐ Standard", callback_data="tier_standard")
        ],
        [
            InlineKeyboardButton(text="👑 Premium", callback_data="tier_premium"),
            InlineKeyboardButton(text="💎 Elite", callback_data="tier_elite")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def settings_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👻 Привидний", callback_data="ghost_mode"),
            InlineKeyboardButton(text="🔔 Сповіщення", callback_data="notifications")
        ],
        [
            InlineKeyboardButton(text="🌐 Мова", callback_data="language"),
            InlineKeyboardButton(text="🔐 Безпека", callback_data="security")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def payment_methods() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Карта", callback_data="card_payment"),
            InlineKeyboardButton(text="🔗 Liqpay", callback_data="liqpay_payment")
        ],
        [InlineKeyboardButton(text="🪙 Крипто", callback_data="crypto_payment")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
