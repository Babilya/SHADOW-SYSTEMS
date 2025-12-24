from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

botnet_router = Router()

def botnet_kb():
    """2-колонне меню для ботів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Додати ботів", callback_data="add_bots"),
            InlineKeyboardButton(text="📋 Мої боти", callback_data="list_bots")
        ],
        [
            InlineKeyboardButton(text="🔄 Ротація проксі", callback_data="proxy_rotation"),
            InlineKeyboardButton(text="🔥 Прогрій ботів", callback_data="warm_bots")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="bots_stats")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
        ],
    ])

def botnet_description() -> str:
    return """<b>🤖 УПРАВЛІННЯ BOTNET</b>

<b>📊 СТАТИСТИКА:</b>
• Всього ботів: <b>45</b>
• Активних: <b>38</b> (84%)
• Неактивних: <b>7</b> (16%)

<b>🔧 ФУНКЦІОНАЛЬНІСТЬ:</b>
<b>➕ Додати ботів</b> - Масове додавання з CSV
<b>📋 Мої боти</b> - Список ботів зі статусом
<b>🔄 Ротація проксі</b> - IP-ротація для безпеки
<b>🔥 Прогрій ботів</b> - Прогрівання перед розсилкою
<b>📊 Статистика</b> - Детальна аналітика ботів"""

@botnet_router.message(Command("botnet"))
async def botnet_cmd(message: Message):
    await message.answer(botnet_description(), reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "botnet_main")
async def botnet_menu(query: CallbackQuery):
    await query.answer()
    await query.message.answer(botnet_description(), reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "add_bots")
async def add_bots(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Завантажити CSV", callback_data="upload_csv")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="bot_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.answer("""➕ <b>ДОДАВАННЯ БОТІВ</b>

<b>КРОКИ:</b>
1. Підготуйте CSV файл (phone, firstName, lastName)
2. Завантажте файл
3. Виберіть налаштування (проксі, інтервал)
4. Система створить ботів автоматично

<b>ФОРМАТ CSV:</b>
phone,firstName,lastName
79991234567,Bot,Name
79991234568,Bot2,Name2""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "upload_csv")
async def upload_csv(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="add_bots")]
    ])
    await query.message.answer("""📤 <b>ЗАВАНТАЖЕННЯ CSV</b>

Надішліть файл з номерами телефонів.
Формат: .csv або .xlsx""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bot_settings")
async def bot_settings(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔒 SOCKS5", callback_data="proxy_socks5")],
        [InlineKeyboardButton(text="🌐 HTTP", callback_data="proxy_http")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="add_bots")]
    ])
    await query.message.answer("""⚙️ <b>НАЛАШТУВАННЯ БОТІВ</b>

<b>ТИП ПРОКСІ:</b>
SOCKS5: Рекомендований (більш безпечний)
HTTP: Швидший

<b>ІНТЕРВАЛ:</b>
Мінімум: 5 сек | Рекомендовано: 10-30 сек

<b>ПРОГРІВ:</b>
✓ Автоматичний прогрів (72 години)""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "list_bots")
async def list_bots(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Активні", callback_data="bots_active")],
        [InlineKeyboardButton(text="🟡 Очікування", callback_data="bots_waiting")],
        [InlineKeyboardButton(text="🔴 Помилки", callback_data="bots_error")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.answer("""📋 <b>МОЇ БОТИ</b>

<b>СТАТИСТИКА:</b>
Всього: 45
🟢 Активні: 38 (84%)
🟡 Очікування: 5 (11%)
🔴 Помилки: 2 (5%)

Виберіть статус для детального перегляду:""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_active")
async def bots_active(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Деталі", callback_data="bot_detail_1")],
        [InlineKeyboardButton(text="🔧 Дії", callback_data="bot_actions")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]
    ])
    await query.message.answer("""🟢 <b>АКТИВНІ БОТИ (38)</b>

ТОП 3:
1. @bot_001 | 234 повідомлень | 0 помилок
2. @bot_002 | 189 повідомлень | 1 помилка
3. @bot_003 | 156 повідомлень | 0 помилок

Всього повідомлень: 12,450
Всього помилок: 3 (0.02%)""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_waiting")
async def bots_waiting(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]
    ])
    await query.message.answer("""🟡 <b>БОТИ В ОЧІКУВАННІ (5)</b>

bot_041 - Прогрівання (35%)
bot_042 - Авторизація
bot_043 - Чекає номера
bot_044 - В черзі
bot_045 - В черзі

Час до активації: ~2-4 години""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_error")
async def bots_error(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Виправити", callback_data="fix_error")],
        [InlineKeyboardButton(text="🗑️ Видалити", callback_data="delete_bot")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]
    ])
    await query.message.answer("""🔴 <b>БОТИ З ПОМИЛКАМИ (2)</b>

bot_043 - Блокування від Telegram
bot_044 - Помилка авторизації

<b>РЕКОМЕНДАЦІЯ:</b>
✓ Видаліть неробочі боти
✓ Додайте нові
✓ Переконтролюйте проксі""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_rotation")
async def proxy_rotation(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Налаштування", callback_data="proxy_config")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="proxy_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.answer("""🔄 <b>РОТАЦІЯ ПРОКСІ</b>

<b>СТАТИСТИКА:</b>
Активних: 12
Робочих: 11 (92%)
Мертвих: 1 (8%)

Остання зміна: 5 хвилин тому
Наступна: за 55 хвилин

Виберіть опцію:""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_config")
async def proxy_config(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_rotation")]
    ])
    await query.message.answer("""⚙️ <b>НАЛАШТУВАННЯ ПРОКСІ</b>

<b>ПОТОЧНІ:</b>
Інтервал ротації: 60 хвилин
Тип: SOCKS5 (100%)
Регіони: UA, RU, US, EU
Whitelist: Увімкнено

<b>СТАТУС:</b>
✅ SOCKS5 proxy 1 - OK
✅ SOCKS5 proxy 2 - OK
✅ SOCKS5 proxy 3 - OK
⚠️ HTTP proxy 1 - Повільна
❌ HTTP proxy 2 - Мертва""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_stats")
async def proxy_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_rotation")]
    ])
    await query.message.answer("""📊 <b>СТАТИСТИКА ПРОКСІ</b>

<b>ТРАФІК:</b>
Запитів день: 1,245
Помилок: 2 (0.16%)
Середня швидкість: 245ms

<b>ТОП ПРОКСІ:</b>
1. proxy_1 - 234 запиту | 99.8% uptime
2. proxy_2 - 198 запитів | 99.5% uptime
3. proxy_3 - 176 запитів | 99.2% uptime

<b>РЕГІОН:</b>
UA: 40% | RU: 35% | US: 15% | EU: 10%""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "warm_bots")
async def warm_bots(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏸️ Пауза", callback_data="pause_warming")],
        [InlineKeyboardButton(text="🛑 Зупинити", callback_data="stop_warming")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.answer("""🔥 <b>ПРОГРІЙ БОТІВ</b>

<b>ПРОГРЕС:</b>
Прогріто: 28/45 (62%)
▬▬▬▬▬░░░░░░ 62%

<b>ЧАС:</b>
Почалося: 2025-12-24 10:30
Закінчиться: 2025-12-27 10:30
Залишилось: 47 годин 15 хвилин

<b>АКТИВНІСТЬ:</b>
Відправлено: 2,340 повідомлень
Реакцій отримано: 456
Помилок: 3 (0.1%)

<b>ТИП ПРОГРІВУ:</b>
Повільне, реалістичне поведінка""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_stats")
async def bots_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Графіки", callback_data="stat_charts")],
        [InlineKeyboardButton(text="⚠️ Помилки", callback_data="stat_errors")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.answer("""📊 <b>СТАТИСТИКА БОТІВ</b>

<b>ОСНОВНІ ПОКАЗНИКИ:</b>
Активність: 84.4%
Якість: 93.3%
Помилки: 6.7%

<b>ГРАФІКИ:</b>
Активність: ████████████████░░░░ 80%
Якість: █████████████████░░ 94%
Успішність: ████████████████░░░ 85%

Виберіть розділ:""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stat_charts")
async def stat_charts(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bots_stats")]
    ])
    await query.message.answer("""📈 <b>ГРАФІКИ АКТИВНОСТІ</b>

<b>АКТИВНІСТЬ ПО ДНЯХ:</b>
Понеділок: ███████████ 85%
Вівторок: ███████████░ 87%
Середа: ████████████ 92%
Четвер: ████████████░ 90%
Пятниця: ███████████░░ 88%
Субота: ████████ 60%
Неділя: ███████ 50%

<b>ПО ГОДИНАХ:</b>
Ранок (6-12): ██████░ 65%
День (12-18): ███████████████ 95% ← Піковий час
Вечір (18-24): ████████████ 90%
Ніч (0-6): ████ 35%""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stat_errors")
async def stat_errors(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bots_stats")]
    ])
    await query.message.answer("""⚠️ <b>АНАЛІЗ ПОМИЛОК</b>

<b>ТОП ПРИЧИНИ:</b>
1. Блокування від Telegram: 1 (33%)
2. Помилка авторизації: 1 (33%)
3. Неправильний номер: 1 (33%)

<b>РІШЕННЯ:</b>
• Блокування: Видаліть, додайте новий
• Авторизація: Перевірте номер
• Номер: Отримайте коректний номер

<b>ІСТОРІЯ ПОМИЛОК:</b>
2025-12-24 09:45 - Блокування
2025-12-23 14:30 - Авторизація
2025-12-22 11:15 - Номер""", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "back_to_menu")
async def botnet_back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.answer(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
