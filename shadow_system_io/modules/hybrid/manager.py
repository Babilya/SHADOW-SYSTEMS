import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridManager:
    """Гібридне управління (Human-in-the-Loop)"""
    
    def __init__(self):
        self.manager_sessions = {}  # {manager_id: {bot_id: session}}
        self.notifications = {}  # {manager_id: [notifications]}
    
    async def connect_manager_to_bot(self, manager_id: int, bot_id: str):
        """Підключити менеджера до бота"""
        if manager_id not in self.manager_sessions:
            self.manager_sessions[manager_id] = {}
        
        self.manager_sessions[manager_id][bot_id] = {
            "connected_at": datetime.now(),
            "status": "active"
        }
        
        logger.info(f"✅ Manager {manager_id} connected to bot {bot_id}")
        return True
    
    async def send_message_from_bot(self, manager_id: int, bot_id: str, 
                                   chat_id: int, message: str):
        """Відправити повідомлення від імені бота"""
        session = self.manager_sessions.get(manager_id, {}).get(bot_id)
        
        if not session:
            logger.error(f"Session not found for manager {manager_id}, bot {bot_id}")
            return False
        
        logger.info(f"📤 Message from manager {manager_id} via bot {bot_id}: {message[:50]}")
        
        # Mock відправка (в реальності Telethon API)
        return True
    
    async def notify_manager(self, manager_id: int, notification: str):
        """Відправити сповіщення менеджеру"""
        if manager_id not in self.notifications:
            self.notifications[manager_id] = []
        
        self.notifications[manager_id].append({
            "message": notification,
            "timestamp": datetime.now().isoformat(),
            "read": False
        })
        
        logger.info(f"🔔 Notification to manager {manager_id}: {notification}")
    
    async def get_manager_stats(self, manager_id: int):
        """Отримати статистику менеджера"""
        stats = {
            "manager_id": manager_id,
            "active_bots": len(self.manager_sessions.get(manager_id, {})),
            "unread_notifications": len([
                n for n in self.notifications.get(manager_id, [])
                if not n["read"]
            ]),
            "total_actions": 42,  # Mock
            "avg_response_time": "1.2s"
        }
        
        return stats

hybrid_manager = HybridManager()
