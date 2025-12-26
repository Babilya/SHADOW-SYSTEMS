from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory
from core.alerts import alert_system, AlertType
from core.encryption import encryption_manager

logger = logging.getLogger(__name__)
payments_router = Router()

class PaymentStates(StatesGroup):
    waiting_screenshot = State()
    waiting_amount = State()

pending_payments = {}

def payments_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплата карткою", callback_data="pay_card")],
        [InlineKeyboardButton(text="🔗 Liqpay", callback_data="pay_liqpay")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="pay_stars")],
        [InlineKeyboardButton(text="📋 Мої платежі", callback_data="my_payments")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def admin_payments_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Очікують підтвердження", callback_data="pending_payments")],
        [InlineKeyboardButton(text="✅ Підтверджені", callback_data="confirmed_payments")],
        [InlineKeyboardButton(text="❌ Відхилені", callback_data="rejected_payments")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])

@payments_router.message(Command("pay"))
async def cmd_pay(message: Message):
    text = """💰 <b>ОПЛАТА</b>

<b>Доступні методи:</b>
├ 💳 Карта (UAH/USD/EUR)
├ 🔗 Liqpay
└ ⭐ Telegram Stars

<b>⚠️ Важливо:</b>
Після оплати надішліть скріншот квитанції.
Ключ буде видано після ручної перевірки адміністратором.

Виберіть спосіб оплати:"""
    
    await message.answer(text, reply_markup=payments_kb(), parse_mode="HTML")

@payments_router.callback_query(F.data == "pay_card")
async def pay_card(query: CallbackQuery, state: FSMContext):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Надіслати скріншот", callback_data="send_screenshot")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]
    ])
    
    text = """💳 <b>ОПЛАТА КАРТКОЮ</b>

<b>Реквізити:</b>
Картка: <code>4441 1144 5555 7777</code>
Одержувач: ФОП "Shadow System"
IBAN: <code>UA213223130000026007233566001</code>

<b>Призначення платежу:</b>
<code>Оплата послуг, User ID: """ + str(query.from_user.id) + """</code>

<b>Після оплати:</b>
1. Зробіть скріншот квитанції
2. Натисніть "Надіслати скріншот"
3. Очікуйте підтвердження адміністратора

⏱ Час обробки: до 24 годин"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "pay_liqpay")
async def pay_liqpay(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Перейти до Liqpay", url="https://liqpay.ua")],
        [InlineKeyboardButton(text="📸 Надіслати скріншот", callback_data="send_screenshot")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]
    ])
    
    text = """🔗 <b>ОПЛАТА LIQPAY</b>

<b>Інструкція:</b>
1. Перейдіть за посиланням Liqpay
2. Введіть суму та реквізити
3. Оплатіть зручним способом
4. Надішліть скріншот квитанції

<b>Реквізити:</b>
Картка: <code>4441 1144 5555 7777</code>

<b>Комісія:</b> 0% (сплачує одержувач)"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "pay_stars")
async def pay_stars(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 100 Stars (БАЗОВИЙ)", callback_data="stars_100")],
        [InlineKeyboardButton(text="⭐ 250 Stars (СТАНДАРТ)", callback_data="stars_250")],
        [InlineKeyboardButton(text="⭐ 1250 Stars (ПРЕМІУМ)", callback_data="stars_1250")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]
    ])
    
    text = """⭐ <b>ОПЛАТА TELEGRAM STARS</b>

<b>Тарифи:</b>
├ 100 ⭐ = БАЗОВИЙ (~4,200 ₴)
├ 250 ⭐ = СТАНДАРТ (~12,500 ₴)
└ 1250 ⭐ = ПРЕМІУМ (~62,500 ₴)

<b>Переваги:</b>
✓ Миттєва обробка
✓ Без комісії
✓ Анонімно

Виберіть тариф:"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "send_screenshot")
async def send_screenshot(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(PaymentStates.waiting_screenshot)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="payments_menu")]
    ])
    
    await query.message.edit_text(
        "📸 <b>НАДСИЛАННЯ КВИТАНЦІЇ</b>\n\n"
        "Надішліть фото або скріншот квитанції про оплату.\n\n"
        "<i>Важливо: на скріншоті має бути видно суму та дату оплати.</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@payments_router.message(PaymentStates.waiting_screenshot)
async def process_screenshot(message: Message, state: FSMContext, bot: Bot):
    payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{message.from_user.id}"
    
    pending_payments[payment_id] = {
        "id": payment_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "has_photo": message.photo is not None,
        "message_id": message.message_id
    }
    
    await audit_logger.log(
        user_id=message.from_user.id,
        action="payment_screenshot_sent",
        category=ActionCategory.PAYMENT,
        username=message.from_user.username,
        details={"payment_id": payment_id}
    )
    
    for admin_id in ADMIN_IDS:
        try:
            admin_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Оплату отримано", callback_data=f"confirm_payment_{payment_id}")],
                [InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_payment_{payment_id}")]
            ])
            
            admin_text = f"""💳 <b>НОВА ОПЛАТА</b>

<b>ID:</b> {payment_id}
<b>Від:</b> @{message.from_user.username or 'N/A'}
<b>User ID:</b> <code>{message.from_user.id}</code>
<b>Час:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

<b>⚠️ Перевірте квитанцію та підтвердіть оплату:</b>"""
            
            if message.photo:
                await bot.send_photo(
                    admin_id,
                    message.photo[-1].file_id,
                    caption=admin_text,
                    reply_markup=admin_kb,
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    admin_id,
                    admin_text + f"\n\nТекст: {message.text[:200] if message.text else 'Без тексту'}",
                    reply_markup=admin_kb,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    await message.answer(
        f"""✅ <b>КВИТАНЦІЯ НАДІСЛАНА</b>

<b>ID платежу:</b> {payment_id}
<b>Статус:</b> 🟡 Очікує підтвердження

Адміністратор перевірить вашу оплату та надішле ліцензійний ключ.

<b>⏱ Час обробки:</b> до 24 годин""",
        parse_mode="HTML"
    )
    await state.clear()

@payments_router.callback_query(F.data.startswith("confirm_payment_"))
async def confirm_payment(query: CallbackQuery, bot: Bot):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    payment_id = query.data.replace("confirm_payment_", "")
    payment = pending_payments.get(payment_id)
    
    if not payment:
        await query.answer("Платіж не знайдено")
        return
    
    payment["status"] = "confirmed"
    payment["confirmed_by"] = query.from_user.id
    payment["confirmed_at"] = datetime.now().isoformat()
    
    license_key = encryption_manager.generate_secure_key("SHADOW")
    payment["license_key"] = license_key
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="payment_confirmed",
        category=ActionCategory.PAYMENT,
        username=query.from_user.username,
        details={
            "payment_id": payment_id,
            "user_id": payment["user_id"],
            "license_key": license_key
        }
    )
    
    try:
        await bot.send_message(
            payment["user_id"],
            f"""✅ <b>ОПЛАТА ПІДТВЕРДЖЕНА</b>

<b>ID платежу:</b> {payment_id}

<b>🔑 Ваш ліцензійний ключ:</b>
<code>{license_key}</code>

<b>Для активації:</b>
<code>/activate {license_key}</code>

⚠️ Збережіть ключ у безпечному місці!""",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send key to user: {e}")
    
    await query.message.edit_caption(
        caption=f"✅ <b>ОПЛАТА ПІДТВЕРДЖЕНА</b>\n\nID: {payment_id}\nКлюч: <code>{license_key}</code>\nПідтвердив: @{query.from_user.username}",
        parse_mode="HTML"
    )
    await query.answer("✅ Оплату підтверджено, ключ надіслано!")

@payments_router.callback_query(F.data.startswith("reject_payment_"))
async def reject_payment(query: CallbackQuery, bot: Bot):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    payment_id = query.data.replace("reject_payment_", "")
    payment = pending_payments.get(payment_id)
    
    if not payment:
        await query.answer("Платіж не знайдено")
        return
    
    payment["status"] = "rejected"
    payment["rejected_by"] = query.from_user.id
    payment["rejected_at"] = datetime.now().isoformat()
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="payment_rejected",
        category=ActionCategory.PAYMENT,
        username=query.from_user.username,
        details={"payment_id": payment_id, "user_id": payment["user_id"]}
    )
    
    try:
        await bot.send_message(
            payment["user_id"],
            f"""❌ <b>ОПЛАТА НЕ ПІДТВЕРДЖЕНА</b>

<b>ID платежу:</b> {payment_id}

Адміністратор не зміг підтвердити вашу оплату.
Можливі причини:
• Квитанція нечитабельна
• Сума не відповідає тарифу
• Дата оплати не співпадає

Будь ласка, зв'яжіться з підтримкою: /support""",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify user: {e}")
    
    await query.message.edit_caption(
        caption=f"❌ <b>ОПЛАТА ВІДХИЛЕНА</b>\n\nID: {payment_id}\nВідхилив: @{query.from_user.username}",
        parse_mode="HTML"
    )
    await query.answer("❌ Оплату відхилено")

@payments_router.callback_query(F.data == "my_payments")
async def my_payments(query: CallbackQuery):
    user_payments = [p for p in pending_payments.values() if p["user_id"] == query.from_user.id]
    
    if not user_payments:
        await query.message.edit_text(
            "📋 <b>МОЇ ПЛАТЕЖІ</b>\n\nУ вас немає платежів.",
            reply_markup=payments_kb(),
            parse_mode="HTML"
        )
        await query.answer()
        return
    
    text = "📋 <b>МОЇ ПЛАТЕЖІ</b>\n\n"
    
    for p in user_payments[-10:]:
        status_icon = {"pending": "🟡", "confirmed": "🟢", "rejected": "🔴"}.get(p["status"], "⚪")
        text += f"{status_icon} {p['id'][:20]} | {p['created_at'][:10]}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@payments_router.callback_query(F.data == "pending_payments")
async def admin_pending_payments(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    pending = [p for p in pending_payments.values() if p["status"] == "pending"]
    
    text = f"📥 <b>ОЧІКУЮТЬ ПІДТВЕРДЖЕННЯ ({len(pending)})</b>\n\n"
    
    if pending:
        for p in pending[-10:]:
            text += f"🟡 {p['id'][:15]} | @{p.get('username', 'N/A')}\n"
    else:
        text += "Немає платежів, що очікують"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="pending_payments")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_payments_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@payments_router.callback_query(F.data == "payments_menu")
async def payments_menu(query: CallbackQuery):
    text = """💰 <b>ОПЛАТА</b>

Виберіть спосіб оплати:"""
    
    await query.message.edit_text(text, reply_markup=payments_kb(), parse_mode="HTML")
    await query.answer()

@payments_router.callback_query(F.data == "admin_payments_menu")
async def admin_payments_menu(query: CallbackQuery):
    pending = sum(1 for p in pending_payments.values() if p["status"] == "pending")
    confirmed = sum(1 for p in pending_payments.values() if p["status"] == "confirmed")
    
    text = f"""💰 <b>УПРАВЛІННЯ ПЛАТЕЖАМИ</b>

<b>📊 Статистика:</b>
├ Очікують: {pending}
├ Підтверджено: {confirmed}
└ Всього: {len(pending_payments)}

<b>⚠️ Нагадування:</b>
Ключі видаються ТІЛЬКИ після ручного підтвердження!"""
    
    await query.message.edit_text(text, reply_markup=admin_payments_kb(), parse_mode="HTML")
    await query.answer()
