from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from . import admin_router
from .utils import safe_edit_message

@admin_router.callback_query(F.data == "project_stats")
async def project_stats_handler(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 Експорт PDF", callback_data="stats_export_pdf"),
            InlineKeyboardButton(text="📊 Експорт CSV", callback_data="stats_export_csv")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>📊 СТАТИСТИКА ПРОЕКТУ</b>

<b>💎 ТАРИФ:</b> ⭐ СТАНДАРТ
<b>📅 Активний до:</b> 15.01.2026

<b>📊 ЗАГАЛЬНА СТАТИСТИКА:</b>
├ Кампаній проведено: <b>156</b>
├ Повідомлень надіслано: <b>45,230</b>
├ Відповідей отримано: <b>6,784</b>
├ Конверсія: <b>15.0%</b>
└ ROI: <b>+245%</b>

<b>🤖 БОТИ:</b>
├ Всього: <b>45 / 500</b>
├ Активних: <b>42</b>
└ З помилками: <b>3</b>

<b>👥 КОМАНДА:</b>
├ Менеджерів: <b>3 / 5</b>
└ Активних сьогодні: <b>2</b>

<b>💰 ВИТРАТИ:</b>
└ Цей місяць: <b>12,500 ₴</b>"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "stats_export_pdf")
async def stats_export_pdf(query: CallbackQuery):
    await query.answer("📄 Генерую PDF звіт...", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="project_stats")]
    ])
    await safe_edit_message(query, "📄 <b>PDF ЗВІТ</b>\n\n⏳ Файл генерується...\n<i>Буде надіслано окремим повідомленням</i>", kb)

@admin_router.callback_query(F.data == "stats_export_csv")
async def stats_export_csv(query: CallbackQuery):
    await query.answer("📊 Генерую CSV звіт...", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="project_stats")]
    ])
    await safe_edit_message(query, "📊 <b>CSV ЗВІТ</b>\n\n⏳ Файл генерується...\n<i>Буде надіслано окремим повідомленням</i>", kb)
