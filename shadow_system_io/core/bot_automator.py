import logging
import uuid
from datetime import datetime
from database.crud import create_bot, get_project_bots, update_bot_status

logger = logging.getLogger(__name__)

class BotAutomator:
    """Автоматизація ботнету"""
    
    def __init__(self):
        self.bots_pool = {}
    
    async def add_bot_to_project(self, project_id: str, phone_number: str = None,
                                session_string: str = None):
        """Додати нового бота до проекту"""
        bot_id = f"bot_{uuid.uuid4().hex[:12]}"
        
        try:
            await create_bot(bot_id, project_id, phone_number, session_string)
            
            self.bots_pool[bot_id] = {
                "project_id": project_id,
                "phone": phone_number,
                "status": "active",
                "created_at": datetime.now()
            }
            
            logger.info(f"✅ Bot added: {bot_id}")
            return bot_id
        except Exception as e:
            logger.error(f"❌ Failed to add bot: {e}")
            return None
    
    async def import_bots_from_file(self, project_id: str, file_content: str):
        """Імпорт ботів із CSV/TXT файлу"""
        lines = file_content.strip().split('\n')
        added_bots = []
        
        for line in lines:
            phone = line.strip()
            if phone:
                bot_id = await self.add_bot_to_project(project_id, phone_number=phone)
                if bot_id:
                    added_bots.append(bot_id)
        
        logger.info(f"📥 Imported {len(added_bots)} bots for project {project_id}")
        return added_bots
    
    async def setup_bot_profile(self, bot_id: str, profile_data: dict):
        """Налаштування профілю бота"""
        profile = {
            "bot_id": bot_id,
            "name": profile_data.get("name"),
            "bio": profile_data.get("bio"),
            "avatar_url": profile_data.get("avatar"),
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"👤 Bot profile set: {bot_id}")
        return profile
    
    async def monitor_bot_status(self, bot_id: str):
        """Моніторинг статусу бота"""
        # Mock моніторинг
        status_data = {
            "bot_id": bot_id,
            "is_online": True,
            "is_blocked": False,
            "is_restricted": False,
            "last_activity": datetime.now().isoformat(),
            "health": "healthy"
        }
        
        logger.info(f"🔍 Bot health check: {bot_id} - {status_data['health']}")
        
        # Якщо заблокований, відключити
        if status_data["is_blocked"]:
            await update_bot_status(bot_id, "blocked")
        
        return status_data
    
    async def disable_bot(self, bot_id: str, reason: str):
        """Відключити бота"""
        await update_bot_status(bot_id, "disabled")
        logger.warning(f"🔴 Bot disabled: {bot_id} - {reason}")

bot_automator = BotAutomator()
