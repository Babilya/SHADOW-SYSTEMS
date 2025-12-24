from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

payments_router = Router()

def balance_payments_kb():
    """Комбіноване меню баланс + платежі"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 Баланс", callback_data="balance_view"),
            InlineKeyboardButton(text="📜 Історія", callback_data="payments_history")
        ],
        [
            InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars_payment"),
            InlineKeyboardButton(text="💳 Карта", callback_data="card_payment")
        ],
        [
            InlineKeyboardButton(text="🔗 Liqpay", callback_data="liqpay_payment"),
            InlineKeyboardButton(text="📄 Рахунок", callback_data="create_invoice")
        ],
        [
            InlineKeyboardButton(text="♻️ Повернення", callback_data="refund_request")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
        ],
    ])

@payments_router.message(Command("pay"))
async def cmd_pay(message: Message):
    """Поповнення рахунку"""
    await message.answer(
        "⭐ <b>БАЛАНС & ПЛАТЕЖІ</b>\n\n"
        "Ваш поточний баланс: <b>5,240 ⭐</b>\n\n"
        "Виберіть опцію:",
        reply_markup=balance_payments_kb(),
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "balance_payments_main")
async def balance_payments_main(query: CallbackQuery):
    await query.answer()
    await query.message.answer(
        "⭐ <b>БАЛАНС & ПЛАТЕЖІ</b>\n\n"
        "Ваш баланс: <b>5,240 ⭐</b>\n"
        "Статус: Активний\n"
        "Остання транзакція: 2025-12-24 10:00\n\n"
        "Виберіть опцію:",
        reply_markup=balance_payments_kb(),
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "balance_view")
async def balance_view(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Поповнити", callback_data="add_funds")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
    await query.message.answer(
        """💵 <b>МІЙ БАЛАНС</b>

<b>ОСНОВНІ ПОКАЗНИКИ:</b>
💰 Баланс: <b>5,240 ⭐</b>
🔒 Заморожено: 0 ⭐
🎁 Бонус: 240 ⭐
📊 До видачі: 5,000 ⭐

<b>СТАТУС:</b>
Активний ✅
Верифікація: Завершена ✅

<b>РАХУНКИ:</b>
Поточний рахунок: 1,240 ⭐
Заробіток з проектів: 4,000 ⭐
Реферальна система: 0 ⭐

<b>ОПЕРАЦІЇ:</b>
Поповнення за місяць: 5 
Видач за місяць: 2
Комісія: 0 ⭐ (0%)""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "payments_history")
async def payments_history(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Поповнення", callback_data="history_topup")],
        [InlineKeyboardButton(text="📤 Видачі", callback_data="history_withdraw")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
    await query.message.answer(
        """📜 <b>ІСТОРІЯ ПЛАТЕЖІВ</b>

<b>ОСТАННІ 10 ОПЕРАЦІЙ:</b>
1. 2025-12-24 10:00 | +300 ⭐ | Telegram Stars | ✅
2. 2025-12-20 14:30 | +500 ⭐ | Карта | ✅
3. 2025-12-18 09:15 | +1,000 ⭐ | Liqpay | ✅
4. 2025-12-15 16:45 | -1,500 ⭐ | Видача | ✅
5. 2025-12-12 11:00 | +2,000 ⭐ | Telegram Stars | ✅
6. 2025-12-10 13:20 | -500 ⭐ | Комісія | ✅
7. 2025-12-08 10:50 | +1,000 ⭐ | Реферальна | ✅
8. 2025-12-05 15:30 | +500 ⭐ | Карта | ✅
9. 2025-12-01 12:00 | +1,000 ⭐ | Liqpay | ✅
10. 2025-11-28 09:45 | -100 ⭐ | Налог | ✅

Виберіть тип:""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "history_topup")
async def history_topup(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_history")]
    ])
    await query.message.answer(
        """📥 <b>ІСТОРІЯ ПОПОВНЕНЬ</b>

1. 2025-12-24 10:00 | +300 ⭐ | Telegram Stars | ✅ | ID: TRX-001
2. 2025-12-20 14:30 | +500 ⭐ | Карта Visa | ✅ | ID: TRX-002
3. 2025-12-18 09:15 | +1,000 ⭐ | Liqpay | ✅ | ID: TRX-003
4. 2025-12-12 11:00 | +2,000 ⭐ | Telegram Stars | ✅ | ID: TRX-004
5. 2025-12-08 10:50 | +1,000 ⭐ | Реферал | ✅ | ID: TRX-005

<b>ВСЬОГО ПОПОВЛЕНО: 4,800 ⭐</b>

<b>СПОРІДНЕНІСТЬ:</b>
Середній платіж: 960 ⭐
Сума от Stars: 2,300 ⭐ (48%)
Сума від карти: 1,500 ⭐ (31%)
Сума від реф: 1,000 ⭐ (21%)""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "history_withdraw")
async def history_withdraw(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_history")]
    ])
    await query.message.answer(
        """📤 <b>ІСТОРІЯ ВИДАЧ</b>

1. 2025-12-15 16:45 | -1,500 ⭐ | Карта | ✅ | ID: WTH-001
2. 2025-12-10 13:20 | -500 ⭐ | Комісія | ✅ | ID: WTH-002
3. 2025-12-01 12:00 | -100 ⭐ | Налог | ✅ | ID: WTH-003

<b>ВСЬОГО ВИДАНО: 2,100 ⭐</b>

<b>СТАТИСТИКА:</b>
Середня видача: 700 ⭐
Остання видача: 2025-12-15
Комісія: 60 ⭐ (2.9%)
Net отримано: 2,040 ⭐""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "stars_payment")
async def stars_payment(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 100 Stars", callback_data="buy_100_stars")],
        [InlineKeyboardButton(text="⭐ 500 Stars", callback_data="buy_500_stars")],
        [InlineKeyboardButton(text="⭐ 1000 Stars", callback_data="buy_1000_stars")],
        [InlineKeyboardButton(text="💳 Інша сума", callback_data="custom_stars")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
    await query.message.answer(
        """⭐ <b>ОПЛАТА TELEGRAM STARS</b>

<b>ПЕРЕВАГИ:</b>
✓ Комісія: 0%
✓ Миттєво
✓ Без верифікації

<b>ДОСТУПНІ ПАКЕТИ:</b>
• 100 ⭐ = ~2 USD
• 500 ⭐ = ~10 USD
• 1000 ⭐ = ~20 USD

Виберіть пакет:""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data.startswith("buy_"))
async def buy_stars(query: CallbackQuery):
    await query.answer()
    amount = query.data.replace("buy_", "").replace("_stars", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Купити", callback_data=f"confirm_stars_{amount}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="stars_payment")]
    ])
    await query.message.answer(
        f"""⭐ <b>КУПІВЛЯ {amount} STARS</b>

<b>ДЕТАЛІ:</b>
Кількість: {amount} ⭐
Ціна: Залежить від валюти
Комісія: 0%
Статус: Готово до оплати

<b>ГАРАНТІЯ:</b>
✓ Безпечна оплата
✓ Миттєва кредитація
✓ 100% гарантія""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "card_payment")
async def card_payment(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити", callback_data="process_card")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
    await query.message.answer(
        """💳 <b>ОПЛАТА КАРТКОЮ</b>

<b>ПАРАМЕТРИ:</b>
Мінімум: 100 ⭐ (~2 USD)
Максимум: 100,000 ⭐ (~2,000 USD)
Комісія: 1.5%

<b>СПОСОБИ:</b>
✓ Visa / MasterCard
✓ Apple Pay
✓ Google Pay

<b>БЕЗПЕКА:</b>
✓ SSL шифрування
✓ 3D Secure
✓ Захист від шахрайства

Введіть суму в ⭐ (наприклад: 500)""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "liqpay_payment")
async def liqpay_payment(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Перейти до Liqpay", url="https://liqpay.com")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
    await query.message.answer(
        """🔗 <b>ОПЛАТА LIQPAY</b>

<b>ПАРАМЕТРИ:</b>
Комісія: 2.5%
Спосіб: Банківський переказ
Час: 15-30 хвилин

<b>СПОСОБИ LIQPAY:</b>
✓ Карта Visa/MasterCard
✓ Банківський переказ
✓ QIWI, WebMoney
✓ Apple Pay, Google Pay

<b>ПЕРЕВАГИ:</b>
✓ Захист покупця
✓ Безпечна оплата
✓ Підтримка 24/7""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "create_invoice")
async def create_invoice(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Розмір: 1000 ⭐", callback_data="inv_1000")],
        [InlineKeyboardButton(text="💰 Розмір: 5000 ⭐", callback_data="inv_5000")],
        [InlineKeyboardButton(text="💰 Кастомна сума", callback_data="inv_custom")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
    await query.message.answer(
        """📄 <b>СТВОРЕННЯ РАХУНКУ</b>

<b>ЩО ЦЕ?</b>
Рахунок це счёт за послуги, який можна відправити клієнту на оплату.

<b>ПЕРЕВАГИ:</b>
✓ Фіксована сума
✓ Строк дії: 48 годин
✓ Автоматична оплата

Виберіть суму:""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data.startswith("inv_"))
async def invoice_created(query: CallbackQuery):
    await query.answer()
    amount = query.data.replace("inv_", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Копіювати посилання", callback_data=f"copy_inv_{amount}")],
        [InlineKeyboardButton(text="📤 Поділитися", callback_data=f"share_inv_{amount}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="create_invoice")]
    ])
    await query.message.answer(
        f"""📄 <b>РАХУНОК СТВОРЕНИЙ</b>

<b>ДЕТАЛІ:</b>
ID: INV-#12345
Сума: {amount} ⭐
Статус: Очікування оплати
Активний: 48 годин

<b>ПОСИЛАННЯ:</b>
https://shadowsystem.io/invoice/12345

<b>СТАТУС:</b>
⏳ Неоплачено
Очікування платежу до 2025-12-26 10:30""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "refund_request")
async def refund_request(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Запросити повернення", callback_data="submit_refund")],
        [InlineKeyboardButton(text="📜 Історія повернень", callback_data="refund_history")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
    await query.message.answer(
        """♻️ <b>ПОВЕРНЕННЯ КОШТІВ</b>

<b>УМОВИ:</b>
• Період повернення: 14 днів
• Максимум повернень: 5 за місяць
• Комісія: 1% від суми

<b>ВАШІ ПЛАТЕЖІ:</b>
✅ 2025-12-24 10:00 | +300 ⭐ | Telegram Stars | АКТИВНА
✅ 2025-12-20 14:30 | +500 ⭐ | Карта | В межах періоду
❌ 2025-12-10 11:00 | +1,000 ⭐ | Крипто | Закінчилась (15+ днів)

Виберіть опцію:""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "submit_refund")
async def submit_refund(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="refund_request")]
    ])
    await query.message.answer(
        """📝 <b>ЗАПИТ ПОВЕРНЕННЯ</b>

Поточний баланс: 5,240 ⭐
Максимум можна повернути: 300 ⭐

<b>ПРИЧИНА ПОВЕРНЕННЯ:</b>
1. Непотрібна послуга
2. Помилка при платежі
3. Технічна проблема
4. Інше

Напишіть суму і причину.""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "refund_history")
async def refund_history(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="refund_request")]
    ])
    await query.message.answer(
        """📜 <b>ІСТОРІЯ ПОВЕРНЕНЬ</b>

1. 2025-12-20 | -500 ⭐ | Поверено | ✅
2. 2025-12-01 | -100 ⭐ | На розгляді | ⏳

<b>СТАТИСТИКА:</b>
Всього повернено: 600 ⭐
На розгляді: 100 ⭐
Разів використано: 2""",
        reply_markup=kb,
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.answer(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
