from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """Головне меню з 2-3 кнопками в ряді"""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Рядок 1: Боти & OSINT
        [
            InlineKeyboardButton(text="🤖 Боти", callback_data="my_bots"),
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_data")
        ],
        # Рядок 2: Кампанії & Аналітика
        [
            InlineKeyboardButton(text="📝 Кампанії", callback_data="campaigns"),
            InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main")
        ],
        # Рядок 3: Платежі & Баланс
        [
            InlineKeyboardButton(text="💳 Платежі", callback_data="payments_main"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ],
        # Рядок 4: Профіль & Налаштування
        [
            InlineKeyboardButton(text="👤 Профіль", callback_data="profile"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_main")
        ],
        # Рядок 5: Текстовки & Довідка
        [
            InlineKeyboardButton(text="📝 Текстовки", callback_data="texting"),
            InlineKeyboardButton(text="📚 Довідка", callback_data="help")
        ],
        # Рядок 6: Підписки & Онбординг
        [
            InlineKeyboardButton(text="📦 Підписки", callback_data="subscription_main"),
            InlineKeyboardButton(text="🎯 Онбординг", callback_data="onboarding_start")
        ],
    ])

def main_menu_description() -> str:
    """Опис функцій для головного меню"""
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>

<b>🤖 BOTNET</b> - Управління ботами
✓ Додавайте до 1000+ ботів | ✓ Ротація проксі | ✓ Прогрів ботів
✓ Масове керування | ✓ Логування & Статистика

<b>🔍 OSINT</b> - Розвідка & Парсинг  
✓ Геосканування за локацією | ✓ Аналіз користувачів | ✓ Аналіз чатів
✓ Лог видалень | ✓ Експорт контактів | ✓ Пошук за інтересами

<b>📊 АНАЛІТИКА</b> - Звіти & Метрики
✓ Дашборд кампаній | ✓ AI Sentiment | ✓ Прогноз ризиків  
✓ ROI аналіз | ✓ Експорт в PDF/Excel | ✓ Порівняння періодів

<b>👥 КОМАНДА</b> - Управління менеджерами
✓ Список менеджерів | ✓ Додавання в команду | ✓ Рейтинг якості
✓ Статистика активності | ✓ Розподіл завдань

<b>📦 ПІДПИСКИ</b> - Тарифи від Free до Elite
• 🆓 Free (0 грн) - 5 ботів, 10 розсилок
• ⭐ Standard (300 грн) - 50 ботів, 500 розсилок  
• 👑 Premium (600 грн) - 100 ботів, 5000 розсилок
• 💎 VIP Elite (1200 грн) - Необмежено всього

<b>💳 ПЛАТЕЖІ</b> - Способи оплати
✓ Карта (комісія 1.5%) | ✓ Liqpay (2.5%) | ✓ Крипто BTC/ETH (0%)
✓ Історія платежів | ✓ Рахунки | ✓ Повернення коштів

<b>⚙️ НАЛАШТУВАННЯ</b> - Конфіг & Безпека
✓ Профіль & статистика | ✓ Привидний режим | ✓ Сповіщення  
✓ 2FA & Шифрування | ✓ Мовні налаштування | ✓ Інтеграції

<b>📝 ТЕКСТОВКИ</b> - Кампанії з шаблонами
✓ 6 готових шаблонів | ✓ A/B тестування | ✓ Сегментація
✓ Автовідправка | ✓ Відкладена розсилка | ✓ Аналіз результатів

<b>📚 ДОВІДКА</b> - Детальна документація
✓ Інструкції по модулям | ✓ Примери & кейси | ✓ FAQ
✓ Відео-туторіали | ✓ Техпідтримка 24/7

<b>🎯 ОНБОРДИНГ</b> - Навчання новачків
✓ 3-рівнева воронка | ✓ Sales воронка | ✓ Градуальне навчання
✓ Практичні завдання | ✓ Сертифікація"""

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
