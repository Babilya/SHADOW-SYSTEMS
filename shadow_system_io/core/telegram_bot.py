import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config.settings import settings
from database.crud import (
    create_user, get_user, get_project_bots, create_audit_log
)
from core.auth import rbac
from core.bot_automator import bot_automator
from modules.parsing.osint import osint_analyzer
from modules.messaging.campaign import campaign_manager
from modules.hybrid.manager import hybrid_manager
from modules.analytics.reporter import analytics_reporter
from utils.security import security_manager

logger = logging.getLogger(__name__)

class TelegramBotManager:
    """Central Telegram Bot Manager"""
    
    def __init__(self):
        self.app = None
        self.bot_token = settings.BOT_TOKEN
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "User"
        
        # Create or update user
        await create_user(user_id, username, role="manager")
        await create_audit_log(user_id, "login", "user", str(user_id))
        
        # Get user role
        user = await get_user(user_id)
        role = user.get("role") if user else "manager"
        
        welcome_text = f"""🎯 <b>SHADOW SYSTEM iO 2.0</b>
Привіт, {username}! 👋

Ваша роль: <b>{role.upper() if role else 'MANAGER'}</b>

Виберіть дію:"""
        
        keyboard = self._get_main_menu_keyboard(role or "manager")
        await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode="HTML")
        
        logger.info(f"✅ User {user_id} ({username}) logged in as {role}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """📚 <b>Доступні команди:</b>

/start - Головне меню
/help - Ця довідка
/projects - Мої проекти
/bots - Мої боти
/campaigns - Мої кампанії
/stats - Статистика
/settings - Налаштування

<b>Для адміна:</b>
/create_project - Створити проект
/add_manager - Додати менеджера

<b>Для суперадміна:</b>
/users - Управління користувачами
/system_settings - Системні налаштування"""
        await update.message.reply_text(help_text, parse_mode="HTML")
    
    async def projects_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's projects"""
        user_id = update.effective_user.id
        
        projects = await rbac.get_user_projects(user_id)
        
        if not projects:
            await update.message.reply_text("❌ У вас немає проектів.")
            return
        
        text = "📋 <b>Ваші проекти:</b>\n\n"
        for p in projects:
            text += f"• {p.get('name')} (ID: {p.get('project_id')})\n"
        
        await update.message.reply_text(text, parse_mode="HTML")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        if query.data == "main_menu":
            user = await get_user(user_id)
            role = user.get("role") if user else "manager"
            keyboard = self._get_main_menu_keyboard(role)
            await query.edit_message_text("🎯 <b>Головне меню</b>", 
                                         reply_markup=keyboard, parse_mode="HTML")
        
        elif query.data == "view_projects":
            await self.projects_command(update, context)
        
        elif query.data == "view_bots":
            await self._show_bots(update, context)
        
        elif query.data == "view_campaigns":
            await self._show_campaigns(update, context)
        
        elif query.data == "view_stats":
            await self._show_stats(update, context)
        
        elif query.data == "osint":
            await self._show_osint_menu(update, context)
        
        elif query.data == "hybrid":
            await self._show_hybrid_menu(update, context)
        
        elif query.data == "security":
            await self._show_security_menu(update, context)
    
    async def _show_bots(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's bots"""
        user_id = update.effective_user.id
        user = await get_user(user_id)
        project_id = user.get("project_id") if user else None
        
        if not project_id:
            await update.message.reply_text("❌ Проект не призначений.")
            return
        
        bots = await get_project_bots(project_id)
        
        if not bots:
            await update.message.reply_text("❌ У проекту немає ботів.")
            return
        
        text = "🤖 <b>Боти проекту:</b>\n\n"
        for bot in bots:
            text += f"• {bot.get('bot_id')} - {bot.get('status')}\n"
        
        await update.message.reply_text(text, parse_mode="HTML")
    
    async def _show_campaigns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show campaigns"""
        await update.message.reply_text("📊 <b>Функція кампаній</b>\n\n🚀 Створювати та управляти розсилками в розробці...", parse_mode="HTML")
    
    async def _show_osint_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show OSINT menu"""
        query = update.callback_query
        text = """🔍 <b>OSINT Парсинг і Аналіз</b>
        
• Пошук чатів за ключовими словами
• Аналіз аудиторії
• Збір даних про користувачів
• Видобування медіа

Функція в розробці... 📥"""
        await query.edit_message_text(text, parse_mode="HTML")
    
    async def _show_hybrid_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show hybrid management menu"""
        query = update.callback_query
        text = """💬 <b>Гібридна Взаємодія (Human-in-the-Loop)</b>
        
• Підключення менеджерів до ботів
• Відправка повідомлень від імені ботів
• Система сповіщень
• Рейтинг менеджерів

Функція в розробці... 🔗"""
        await query.edit_message_text(text, parse_mode="HTML")
    
    async def _show_security_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show security menu"""
        query = update.callback_query
        text = """🛡️ <b>Система Безпеки</b>
        
• Rate Limiting: Активен
• Audit Logging: Активен
• Anti-Blocking: Активен
• User Blocking: 0 користувачів

✅ Все захищено!"""
        await query.edit_message_text(text, parse_mode="HTML")
    
    async def _show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics"""
        user_id = update.effective_user.id
        user = await get_user(user_id)
        project_id = user.get("project_id") if user else None
        
        if not project_id:
            await update.message.reply_text("❌ Проект не призначений.")
            return
        
        stats = await analytics_reporter.get_project_stats(project_id)
        
        text = f"""📈 <b>Статистика проекту:</b>
        
🤖 Ботів: {stats['active_bots']}/{stats['total_bots']}
📊 Кампаній: {stats['completed_campaigns']}/{stats['total_campaigns']}
✉️ Відправлено: {stats['messages_sent']}
✅ Доставлено: {stats['messages_delivered']}
📈 Рівень доставки: {stats['delivery_rate']}"""
        await update.message.reply_text(text, parse_mode="HTML")
    
    def _get_main_menu_keyboard(self, role: str) -> InlineKeyboardMarkup:
        """Get main menu keyboard based on role"""
        buttons = [
            [InlineKeyboardButton("📋 Проекти", callback_data="view_projects")],
            [InlineKeyboardButton("🤖 Боти", callback_data="view_bots")],
            [InlineKeyboardButton("📊 Кампанії", callback_data="view_campaigns")],
            [InlineKeyboardButton("📈 Статистика", callback_data="view_stats")],
            [InlineKeyboardButton("🔍 OSINT Парсинг", callback_data="osint")],
            [InlineKeyboardButton("💬 Гібридна Взаємодія", callback_data="hybrid")],
        ]
        
        if role in ["admin", "superadmin"]:
            buttons.append([InlineKeyboardButton("⚙️ Налаштування", callback_data="settings")])
            buttons.append([InlineKeyboardButton("🛡️ Безпека", callback_data="security")])
        
        if role == "superadmin":
            buttons.append([InlineKeyboardButton("👥 Користувачі", callback_data="users")])
        
        return InlineKeyboardMarkup(buttons)
    
    async def setup(self):
        """Setup bot handlers"""
        self.app = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("projects", self.projects_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("✅ Telegram bot handlers configured")
    
    async def run(self):
        """Run bot"""
        if not self.app:
            await self.setup()
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("🚀 Telegram bot polling started")
    
    async def stop(self):
        """Stop bot"""
        if self.app:
            await self.app.stop()
            logger.info("🛑 Telegram bot stopped")

telegram_bot = TelegramBotManager()
