"""
Централізований файл для всіх FSM States системи
"""
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Стани для адмін-панелі"""
    waiting_broadcast = State()
    waiting_block_id = State()
    waiting_alert_message = State()
    waiting_ban_user = State()
    waiting_role_user_id = State()
    waiting_role_selection = State()


class AuthStates(StatesGroup):
    """Стани для авторизації"""
    waiting_key = State()
    waiting_invite = State()


class KeyStates(StatesGroup):
    """Стани для введення ключів"""
    waiting_key = State()


class FunnelStates(StatesGroup):
    """Стани для воронок"""
    creating_name = State()
    creating_description = State()
    editing_name = State()
    editing_description = State()
    adding_step_text = State()
    adding_step_photo = State()
    editing_step_text = State()


class MailingStates(StatesGroup):
    """Стани для розсилок"""
    waiting_text = State()
    waiting_media = State()
    waiting_target = State()
    waiting_schedule = State()


class OSINTStates(StatesGroup):
    """Стани для OSINT"""
    waiting_target = State()
    waiting_dns_domain = State()
    waiting_whois_domain = State()
    waiting_geoip_ip = State()
    waiting_email = State()
    waiting_user_id = State()
    waiting_chat_id = State()


class TemplateStates(StatesGroup):
    """Стани для шаблонів"""
    waiting_name = State()
    waiting_content = State()
    waiting_category = State()


class SupportStates(StatesGroup):
    """Стани для тікетів підтримки"""
    waiting_subject = State()
    waiting_message = State()
    waiting_reply = State()


class TextingStates(StatesGroup):
    """Стани для текстовок"""
    waiting_text = State()
    waiting_name = State()


class BotnetStates(StatesGroup):
    """Стани для ботнету"""
    waiting_session = State()
    waiting_proxy = State()


class WarmingStates(StatesGroup):
    """Стани для прогріву"""
    waiting_profile = State()
    waiting_settings = State()


class TeamStates(StatesGroup):
    """Стани для команди"""
    waiting_manager_id = State()
    waiting_invite_count = State()


class NotificationStates(StatesGroup):
    """Стани для сповіщень"""
    waiting_text = State()
    waiting_target = State()


class SchedulerStates(StatesGroup):
    """Стани для планувальника"""
    waiting_cron = State()
    waiting_time = State()
