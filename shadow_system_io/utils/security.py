import logging
import asyncio
from datetime import datetime, timedelta
from database.crud import create_audit_log

logger = logging.getLogger(__name__)

class SecurityManager:
    """Система безпеки та запобіжників"""
    
    def __init__(self):
        self.user_actions = {}  # {user_id: [timestamp, action]}
        self.blocked_users = set()
    
    async def check_rate_limit(self, user_id: int, max_actions: int = 20, 
                              time_window: int = 60) -> bool:
        """Перевірка rate limit користувача"""
        now = datetime.now()
        
        if user_id not in self.user_actions:
            self.user_actions[user_id] = []
        
        # Очистити старі дії
        self.user_actions[user_id] = [
            t for t in self.user_actions[user_id]
            if (now - t).seconds < time_window
        ]
        
        # Перевірити ліміт
        if len(self.user_actions[user_id]) >= max_actions:
            logger.warning(f"⚠️ Rate limit exceeded for user {user_id}")
            return False
        
        self.user_actions[user_id].append(now)
        return True
    
    async def log_action(self, user_id: int, action: str, resource_type: str,
                        resource_id: str, details: dict = None):
        """Логування дії користувача"""
        await create_audit_log(user_id, action, resource_type, resource_id, details)
        logger.info(f"📝 Audit: user {user_id} - {action} on {resource_type}")
    
    async def detect_suspicious_activity(self, user_id: int, action_count: int) -> bool:
        """Виявлення підозрілої активності"""
        # Якщо більше 50 дій за хвилину
        if action_count > 50:
            logger.warning(f"🚨 Suspicious activity detected for user {user_id}")
            return True
        
        return False
    
    async def block_user(self, user_id: int, reason: str):
        """Блокування користувача"""
        self.blocked_users.add(user_id)
        logger.warning(f"🔒 User {user_id} blocked: {reason}")
        
        await create_audit_log(
            user_id,
            "blocked",
            "user",
            str(user_id),
            {"reason": reason}
        )
    
    async def is_user_blocked(self, user_id: int) -> bool:
        """Перевірка чи користувач заблокований"""
        return user_id in self.blocked_users
    
    async def enable_anti_blocking(self, bot_id: str):
        """Активація anti-blocking механізмів"""
        logger.info(f"🛡️ Anti-blocking enabled for bot {bot_id}")
        
        # Випадкові затримки, зміна IP, тощо
        return {
            "random_delays": True,
            "proxy_rotation": True,
            "human_like_behavior": True,
            "random_interactions": True
        }

security_manager = SecurityManager()
